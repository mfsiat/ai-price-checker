# AI Price Checker — Project Analysis

## Overview

A full-stack web application for comparing the estimated monthly costs of LLM APIs across multiple providers. Users configure token usage parameters (input tokens, output tokens, requests/day), select one model per provider, and receive a cost breakdown presented as model cards, a bar chart, and a pie chart.

---

## Architecture

```
ai-price-checker/
├── backend/
│   └── app/
│       ├── main.py         FastAPI app, route definitions
│       ├── models.py       Pydantic request/response schemas
│       ├── services.py     Loads pricing.json from disk
│       ├── calculator.py   Standalone cost calculation helper
│       └── pricing.json    Static pricing data (8 providers, 27 models)
└── frontend/
    └── src/
        ├── App.js          Root component, state management
        ├── api.js          Axios client (3 endpoints)
        └── components/
            ├── ModelSelector.js   Per-provider model dropdowns
            ├── ModelCard.js       Metadata card per model
            ├── BarChart.js        Monthly cost bar chart
            ├── PieChart.js        Cost share pie chart
            └── PriceTable.js      Results table (unused)
```

**Tech stack:**
- Backend: Python, FastAPI, Pydantic
- Frontend: React 19, Chart.js (via react-chartjs-2), Axios
- Data: Static `pricing.json` (no database)

---

## Bugs

### Critical — will crash at runtime

**1. `NameError`: `pricing` is undefined in `main.py`**

- **File:** `backend/app/main.py:64, 103`
- **Problem:** `load_pricing()` assigns its return value to `pricing_data` (line 17), but the `/calculate` and `/models` endpoints reference the name `pricing` (no `_data` suffix). Every POST to `/calculate` and GET to `/models` will raise a `NameError` and return HTTP 500.
- **Fix:** Either rename `pricing_data` → `pricing` on line 17, or update all references in the two endpoints to use `pricing_data`.

```python
# current (broken)
pricing_data = load_pricing()
...
for provider, model in request.selected_models.items():
    if provider not in pricing:   # NameError here
        ...

# fix
pricing = load_pricing()
```

---

**2. Stale Pydantic model in `models.py`**

- **File:** `backend/app/models.py:8`
- **Problem:** `UsageRequest` declares `providers: List[str]`, but the `/calculate` endpoint reads `request.selected_models` (a `Dict[str, str]`), and the frontend sends `selected_models`. Pydantic will reject the request body before the route handler even runs, returning HTTP 422.
- **Fix:** Update `UsageRequest` to match the actual contract:

```python
from pydantic import BaseModel
from typing import Dict

class UsageRequest(BaseModel):
    input_tokens: int
    output_tokens: int
    requests_per_day: int
    selected_models: Dict[str, str]
```

---

**3. Dead code / inconsistent token pricing unit in `calculator.py`**

- **File:** `backend/app/calculator.py`
- **Problem:** `calculate_cost()` divides tokens by `1_000_000` (per-million pricing), but the inline cost logic in `/calculate` divides by `1000`. The function is also never called anywhere. The two approaches give results that differ by a factor of 1000.
- **Fix:** Either remove `calculator.py` and use the inline logic consistently, or replace the inline logic with a call to the helper and pick one pricing unit (per-million is the industry standard).

---

### Non-critical bugs

**4. Input values sent as strings to the backend**

- **File:** `frontend/src/App.js:46–48`
- **Problem:** `setInputTokens(e.target.value)` stores a string. The initial state is `number`, but after any user interaction the values become strings. FastAPI/Pydantic will coerce `"2000"` to `int` for top-level fields, but it is fragile and inconsistent.
- **Fix:** Parse on change: `setInputTokens(Number(e.target.value))` or `parseInt(e.target.value, 10)`.

**5. No error handling on API calls in the frontend**

- **File:** `frontend/src/App.js:30–38`
- **Problem:** `calculate()` has no `try/catch`. A network error or 5xx response silently does nothing — no user feedback.
- **Fix:** Wrap in try/catch and display an error message.

**6. `PriceTable` component is unused**

- **File:** `frontend/src/components/PriceTable.js`
- **Problem:** The component is fully implemented but never imported or rendered in `App.js`. Users see charts but no tabular data.
- **Fix:** Import and render `<PriceTable results={results} />` below the charts in `App.js`.

---

## Stale / Incorrect Data

**7. `pricing.json` contains outdated models and prices**

The pricing data does not reflect the current (2025) state of any of the listed providers. Notable gaps:

| Provider  | In pricing.json         | Current (missing)                         |
|-----------|-------------------------|-------------------------------------------|
| Anthropic | claude-3-opus/sonnet/haiku | claude-3.5-haiku, claude-3.5-sonnet, claude-opus-4, claude-sonnet-4 |
| OpenAI    | gpt-4o, gpt-4-turbo, o1  | gpt-4.1, gpt-4.1-mini, o3, o3-mini, o4-mini |
| Google    | gemini-1.5-pro/flash     | gemini-2.0-flash, gemini-2.5-pro          |
| Meta      | llama-3-70b/8b           | llama-3.3-70b, llama-4 scout/maverick     |

Additionally, the prices in the file (e.g. `gpt-4o` input at `$5/1M`) no longer match current published rates. Since this is a static file, it requires manual upkeep.

---

## Improvements

### Backend

**8. Extract inline cost logic to use `calculator.py`**

The per-request cost formula is duplicated inline in `main.py`. Move it into `calculator.py`, fix the units, and call it from the route — single responsibility, easier to test.

**9. Add input validation**

`input_tokens`, `output_tokens`, and `requests_per_day` should be validated as positive integers. Pydantic's `Field(gt=0)` handles this cleanly:

```python
from pydantic import BaseModel, Field

class UsageRequest(BaseModel):
    input_tokens: int = Field(gt=0)
    output_tokens: int = Field(gt=0)
    requests_per_day: int = Field(gt=0)
    selected_models: Dict[str, str]
```

**10. Restrict CORS in production**

`allow_origins=["*"]` in `main.py` is acceptable for local development but should be restricted to the actual frontend origin before any deployment.

**11. Consider a dynamic pricing source**

The static `pricing.json` will keep going stale. Options:
- Scrape/poll provider pricing pages on a schedule.
- Use a third-party pricing API (e.g. OpenRouter's public pricing endpoint).
- At minimum, add a `last_updated` timestamp to the JSON and display it in the UI.

**12. Add a `requirements.txt` / `pyproject.toml`**

There is no Python dependency file. Anyone cloning the repo has to guess the dependencies (`fastapi`, `uvicorn`, `pydantic`). Add a `requirements.txt` or use a tool like Poetry/uv.

---

### Frontend

**13. Wire up `PriceTable`**

The table component is built — just import and render it. It provides a scannable, copy-pasteable view of results that the charts alone don't offer.

**14. Add loading and error states**

```jsx
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);

const calculate = async () => {
  setLoading(true);
  setError(null);
  try {
    const res = await calculatePrice({ ... });
    setResults(res.data.results);
  } catch (err) {
    setError("Calculation failed. Is the backend running?");
  } finally {
    setLoading(false);
  }
};
```

**15. Add labels to the token input fields**

`App.js:46–48` renders three bare `<input>` elements with no labels. It is not obvious which is which without reading the code. Add `<label>` elements or placeholder text.

**16. Sort results by cost**

After calculation, sort `results` ascending by `monthly_cost` before rendering. This makes the charts and cards immediately useful for comparison without requiring the user to visually scan.

**17. Consider `react-query` or `SWR` for data fetching**

The manual `useEffect` + `useState` pattern in `App.js` for `getProviders` is functional but fragile. A library like `react-query` handles caching, loading states, and retries with much less boilerplate.

---

## Summary

| Category     | Count | Severity         |
|--------------|-------|------------------|
| Runtime crash bugs | 2 | Critical |
| Logic/data bugs    | 4 | Medium   |
| Stale data         | 1 | Medium   |
| Improvements       | 10 | Low–Medium |

The two critical fixes needed to make the app functional are:
1. Rename `pricing_data` → `pricing` in `main.py` (or update all references).
2. Update `UsageRequest` in `models.py` to include `selected_models: Dict[str, str]`.

Everything else is quality-of-life.
