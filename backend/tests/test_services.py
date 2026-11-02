"""Tests for PricingRepository: loading, validation, metadata, lookups, reload."""

import json

import pytest

from app.services import PricingDataError, PricingRepository

VALID_DATASET = {
    "version": "2026.1.0",
    "last_updated": "2026-01-01",
    "source": "test",
    "providers": {
        "acme": {
            "models": {
                "cheap": {
                    "input": 0.1,
                    "output": 0.2,
                    "context": 1000,
                    "speed": "fast",
                    "tier": "budget",
                    "multimodal": False,
                    "vision": False,
                },
                "pricey": {
                    "input": 5.0,
                    "output": 15.0,
                    "context": 2000,
                    "speed": "slow",
                    "tier": "flagship",
                    "multimodal": True,
                    "vision": True,
                },
            }
        }
    },
}


def _write(tmp_path, data):
    path = tmp_path / "pricing.json"
    path.write_text(json.dumps(data))
    return path


def test_loads_metadata(tmp_path):
    repo = PricingRepository(path=_write(tmp_path, VALID_DATASET))
    meta = repo.metadata()
    assert meta["version"] == "2026.1.0"
    assert meta["last_updated"] == "2026-01-01"
    assert meta["source"] == "test"
    assert meta["model_count"] == 2
    assert meta["provider_count"] == 1


def test_get_model_returns_none_for_unknown(tmp_path):
    repo = PricingRepository(path=_write(tmp_path, VALID_DATASET))
    assert repo.get_model("acme", "cheap") is not None
    assert repo.get_model("acme", "missing") is None
    assert repo.get_model("ghost", "cheap") is None


def test_compute_comparison_sorts_and_warns(tmp_path):
    repo = PricingRepository(path=_write(tmp_path, VALID_DATASET))
    results, warnings = repo.compute_comparison(
        {"acme": "pricey", "ghost": "x", "acme2": "y"},
        input_tokens=1000,
        output_tokens=1000,
        requests_per_day=10,
    )
    # Only the known model yields a result.
    assert [r["model"] for r in results] == ["pricey"]
    # Two unknown selections are reported as warnings.
    assert {w["provider"] for w in warnings} == {"ghost", "acme2"}


def test_compute_comparison_is_sorted(tmp_path):
    # Two providers so a single call returns both models and we can assert order.
    data = json.loads(json.dumps(VALID_DATASET))
    acme_models = data["providers"]["acme"]["models"]
    data["providers"]["bravo"] = {"models": {"pricey": acme_models["pricey"]}}
    data["providers"]["acme"]["models"] = {"cheap": acme_models["cheap"]}

    repo = PricingRepository(path=_write(tmp_path, data))
    results, _ = repo.compute_comparison(
        {"acme": "cheap", "bravo": "pricey"}, 1000, 1000, 1
    )
    costs = [r["monthly_cost"] for r in results]
    assert costs == sorted(costs)


def test_filter_models_by_tier(tmp_path):
    repo = PricingRepository(path=_write(tmp_path, VALID_DATASET))
    filtered = repo.filter_models(tier="budget")
    assert list(filtered["acme"]["models"]) == ["cheap"]


def test_reload_picks_up_changes(tmp_path):
    path = _write(tmp_path, VALID_DATASET)
    repo = PricingRepository(path=path)
    assert repo.model_count == 2

    cheap = VALID_DATASET["providers"]["acme"]["models"]["cheap"]
    updated = {**VALID_DATASET, "providers": {"acme": {"models": {"cheap": cheap}}}}
    path.write_text(json.dumps(updated))
    repo.reload()
    assert repo.model_count == 1


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.pop("providers"),
        lambda d: d.update(providers={}),
        lambda d: d["providers"]["acme"].update(models={}),
    ],
)
def test_invalid_structure_rejected(tmp_path, mutate):
    data = json.loads(json.dumps(VALID_DATASET))
    mutate(data)
    with pytest.raises(PricingDataError):
        PricingRepository(path=_write(tmp_path, data))


def test_missing_required_field_rejected(tmp_path):
    data = json.loads(json.dumps(VALID_DATASET))
    del data["providers"]["acme"]["models"]["cheap"]["tier"]
    with pytest.raises(PricingDataError):
        PricingRepository(path=_write(tmp_path, data))


def test_non_positive_price_rejected(tmp_path):
    data = json.loads(json.dumps(VALID_DATASET))
    data["providers"]["acme"]["models"]["cheap"]["input"] = 0
    with pytest.raises(PricingDataError):
        PricingRepository(path=_write(tmp_path, data))
