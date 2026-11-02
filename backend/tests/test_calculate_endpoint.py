"""API-level tests for POST /calculate.

Covers validation surfacing as HTTP 422 in the standard error envelope
(issue #11), real cost calculation against the live pricing dataset, and the
``warnings`` feedback for unknown models (so stale clients aren't silently
handed empty results).
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app, repository

client = TestClient(app)

VALID_PAYLOAD = {
    "input_tokens": 2000,
    "output_tokens": 500,
    "requests_per_day": 1000,
    "selected_models": {},
}


def _first_real_model() -> tuple[str, str]:
    provider = next(iter(repository.providers))
    model = next(iter(repository.providers[provider]["models"]))
    return provider, model


def test_calculate_accepts_valid_payload():
    response = client.post("/calculate", json=VALID_PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert body["results"] == []
    assert body["warnings"] == []


def test_calculate_returns_cost_for_known_model():
    provider, model = _first_real_model()
    payload = {**VALID_PAYLOAD, "selected_models": {provider: model}}

    response = client.post("/calculate", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert len(body["results"]) == 1
    entry = body["results"][0]
    assert entry["provider"] == provider
    assert entry["model"] == model
    assert entry["monthly_cost"] > 0
    assert body["warnings"] == []


def test_calculate_results_sorted_ascending_by_cost():
    payload = {
        **VALID_PAYLOAD,
        "selected_models": {p: next(iter(d["models"])) for p, d in repository.providers.items()},
    }
    response = client.post("/calculate", json=payload)
    costs = [r["monthly_cost"] for r in response.json()["results"]]
    assert costs == sorted(costs)


def test_calculate_warns_about_unknown_model():
    payload = {**VALID_PAYLOAD, "selected_models": {"nope": "ghost-model"}}
    response = client.post("/calculate", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["results"] == []
    assert len(body["warnings"]) == 1
    assert body["warnings"][0]["provider"] == "nope"
    assert body["warnings"][0]["model"] == "ghost-model"


@pytest.mark.parametrize("field", ["input_tokens", "output_tokens", "requests_per_day"])
def test_calculate_rejects_non_positive_tokens(field):
    payload = {**VALID_PAYLOAD, field: 0}
    response = client.post("/calculate", json=payload)

    assert response.status_code == 422
    body = response.json()
    # Standardized error envelope (see app/errors.py).
    assert body["error"]["code"] == "validation_error"
    assert any(err["loc"][-1] == field for err in body["error"]["details"]), body
