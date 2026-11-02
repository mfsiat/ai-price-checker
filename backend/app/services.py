"""Pricing data access and cost-comparison business logic.

The :class:`PricingRepository` owns everything about the pricing dataset:
loading it from disk, validating its shape, exposing metadata
(``last_updated``/``version``/``source``), looking up individual models, and
reloading on demand. Keeping this in one place means the route handlers in
:mod:`app.main` stay thin and the business rules are unit-testable without a
running server.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .calculator import calculate_cost

DEFAULT_PRICING_FILE = Path(__file__).parent / "pricing.json"

# Fields every model entry must define for the app to treat it as valid.
REQUIRED_MODEL_FIELDS = ("input", "output", "context", "speed", "tier", "multimodal", "vision")


class PricingDataError(RuntimeError):
    """Raised when the pricing dataset is missing or structurally invalid."""


def load_pricing(path: Path | None = None) -> dict[str, Any]:
    """Read and parse the raw pricing JSON file.

    Kept as a thin module-level function for backwards compatibility and simple
    one-off reads; most callers should use :class:`PricingRepository`.
    """
    pricing_path = path or DEFAULT_PRICING_FILE
    with open(pricing_path) as f:
        return json.load(f)


def _validate(data: dict[str, Any]) -> dict[str, Any]:
    """Validate the top-level and per-model shape of the pricing dataset.

    Raises :class:`PricingDataError` with a clear message on the first problem
    so a malformed deploy fails loudly at startup instead of serving garbage.
    """
    if not isinstance(data, dict):
        raise PricingDataError("Pricing data must be a JSON object.")

    providers = data.get("providers")
    if not isinstance(providers, dict) or not providers:
        raise PricingDataError("Pricing data must contain a non-empty 'providers' object.")

    for provider, pdata in providers.items():
        models = (pdata or {}).get("models") if isinstance(pdata, dict) else None
        if not isinstance(models, dict) or not models:
            raise PricingDataError(f"Provider '{provider}' must have a non-empty 'models' map.")
        for model, mdata in models.items():
            if not isinstance(mdata, dict):
                raise PricingDataError(f"Model '{provider}/{model}' must be an object.")
            missing = [k for k in REQUIRED_MODEL_FIELDS if k not in mdata]
            if missing:
                raise PricingDataError(
                    f"Model '{provider}/{model}' is missing required field(s): "
                    f"{', '.join(missing)}."
                )
            for num_field in ("input", "output"):
                value = mdata[num_field]
                if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
                    raise PricingDataError(
                        f"Model '{provider}/{model}' field '{num_field}' must be a positive number."
                    )
    return data


class PricingRepository:
    """In-memory, reloadable view of the pricing dataset."""

    def __init__(self, path: Path | None = None):
        self._path = path or DEFAULT_PRICING_FILE
        self._data: dict[str, Any] = {}
        self.reload()

    def reload(self) -> None:
        """(Re)load and validate the dataset from disk.

        Enables a data refresh without a process restart: update the JSON file
        (or point ``PRICING_FILE`` at a new one) and call this.
        """
        self._data = _validate(load_pricing(self._path))

    # -- metadata -----------------------------------------------------------
    @property
    def providers(self) -> dict[str, Any]:
        return self._data.get("providers", {})

    @property
    def last_updated(self) -> str | None:
        return self._data.get("last_updated")

    @property
    def version(self) -> str | None:
        return self._data.get("version")

    @property
    def source(self) -> str | None:
        return self._data.get("source")

    @property
    def model_count(self) -> int:
        return sum(len(p.get("models", {})) for p in self.providers.values())

    def metadata(self) -> dict[str, Any]:
        """Dataset provenance, surfaced by ``/providers`` and ``/health``."""
        return {
            "last_updated": self.last_updated,
            "version": self.version,
            "source": self.source,
            "model_count": self.model_count,
            "provider_count": len(self.providers),
        }

    # -- lookups ------------------------------------------------------------
    def get_model(self, provider: str, model: str) -> dict[str, Any] | None:
        provider_data = self.providers.get(provider)
        if not provider_data:
            return None
        return provider_data.get("models", {}).get(model)

    def compute_comparison(
        self,
        selected_models: dict[str, str],
        input_tokens: int,
        output_tokens: int,
        requests_per_day: int,
    ) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
        """Compute monthly costs for the selected models.

        Returns ``(results, warnings)`` where ``results`` is sorted ascending by
        monthly cost and ``warnings`` lists any selected provider/model that was
        not found in the dataset — so a stale client gets explicit feedback
        instead of a silently-empty result set.
        """
        results: list[dict[str, Any]] = []
        warnings: list[dict[str, str]] = []

        for provider, model in selected_models.items():
            model_data = self.get_model(provider, model)
            if not model_data:
                warnings.append(
                    {
                        "provider": provider,
                        "model": model,
                        "reason": "Unknown provider or model; not found in pricing data.",
                    }
                )
                continue

            monthly_cost = calculate_cost(
                model_data["input"],
                model_data["output"],
                input_tokens,
                output_tokens,
                requests_per_day,
            )
            results.append(
                {
                    "provider": provider,
                    "model": model,
                    "monthly_cost": monthly_cost,
                    "context": model_data.get("context"),
                    "speed": model_data.get("speed"),
                    "tier": model_data.get("tier"),
                    "multimodal": model_data.get("multimodal"),
                    "vision": model_data.get("vision"),
                }
            )

        results.sort(key=lambda r: r["monthly_cost"])
        return results, warnings

    def filter_models(
        self,
        provider: str | None = None,
        tier: str | None = None,
        speed: str | None = None,
        multimodal: bool | None = None,
    ) -> dict[str, Any]:
        """Return providers/models matching the given filters."""
        result: dict[str, Any] = {}
        for p, pdata in self.providers.items():
            if provider and p != provider:
                continue

            models = {}
            for m, mdata in pdata.get("models", {}).items():
                if tier and mdata.get("tier") != tier:
                    continue
                if speed and mdata.get("speed") != speed:
                    continue
                if multimodal is not None and mdata.get("multimodal") != multimodal:
                    continue
                models[m] = mdata

            if models:
                result[p] = {"models": models}
        return result
