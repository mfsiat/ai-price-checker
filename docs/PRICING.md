# Pricing Data Lifecycle

The app compares **estimated** monthly LLM costs using a curated dataset at
`backend/app/pricing.json`. This document defines how that data stays correct
and fresh.

## Why static JSON (and how it's hardened)

A hand-maintained JSON file is intentionally simple — there is no reliable,
free, unified pricing API across all vendors, and prices change rarely enough
that a curated file is the pragmatic choice. The risks of a static file (going
stale, typos, malformed edits) are mitigated by:

1. **Schema validation at startup.** `PricingRepository` validates structure and
   per-model fields on load (`backend/app/services.py`). A malformed dataset
   makes the app fail loudly instead of serving garbage.
2. **A validation + freshness script.** `backend/scripts/validate_pricing.py`
   runs the same validation and can also flag stale data.
3. **CI gates.** The backend test job validates the data on every PR; a
   scheduled workflow flags staleness (see below).
4. **Provenance metadata.** `version`, `last_updated`, and `source` are stored
   in the file and exposed via `GET /providers` and `GET /health`, and the UI
   shows the last-updated date.
5. **Runtime reload.** `PricingRepository.reload()` re-reads the file without a
   process restart (point `PRICING_FILE` at a new file or edit in place).

## Data shape

```jsonc
{
  "version": "2026.10.1",            // bump on every pricing change
  "last_updated": "2026-10-16",      // ISO date (YYYY-MM-DD)
  "source": "Vendor public pricing pages, manually curated.",
  "providers": {
    "openai": {
      "models": {
        "gpt-4.1": {
          "input": 2.0,              // USD per 1M input tokens  (> 0)
          "output": 8.0,             // USD per 1M output tokens (> 0)
          "context": 1047576,        // positive integer
          "multimodal": true,        // boolean
          "vision": true,            // boolean (vision ⇒ multimodal)
          "speed": "fast",           // non-empty label
          "tier": "flagship"         // non-empty label
        }
      }
    }
  }
}
```

## How to refresh prices

1. Edit `backend/app/pricing.json` — update prices/models.
2. Bump `version` and set `last_updated` to today (ISO `YYYY-MM-DD`).
3. Validate locally:
   ```bash
   cd backend
   python -m scripts.validate_pricing --max-age-days 120
   ```
4. Run the test suites (`pytest` in `backend`, `CI=true npm test` in `frontend`
   — `frontend/src/pricing.test.js` cross-checks the same file).
5. Open a PR. CI re-validates before merge.

A running instance can pick up changes without redeploying by calling
`PricingRepository.reload()` (e.g. wire it to an authenticated admin endpoint if
you need hot reloads in production).

## Staleness policy

Target refresh cadence: **every 90 days**, or sooner when a major model ships.
The scheduled CI workflow (`.github/workflows/pricing-freshness.yml`) runs
`validate_pricing.py --max-age-days 120` monthly and fails if the data is older
than the threshold, surfacing a reminder to refresh.
