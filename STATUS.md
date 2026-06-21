# AI Price Checker — Project Status

**Last updated:** 2026-06-21  
**Branch:** master  
**Last commit:** `67fbce2`

---

## Stack

| Layer | Tech |
|-------|------|
| Backend | Python FastAPI (`backend/app/`) |
| Frontend | React CRA (`frontend/src/`) |
| Containerisation | Dockerfile in both `backend/` and `frontend/` (nginx) |

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check |
| GET | `/providers` | Full pricing data |
| POST | `/calculate` | `{input_tokens, output_tokens, requests_per_day, selected_models: {provider: model}}` → `{results: [...]}` sorted ascending by monthly cost |
| GET | `/models` | Filter by `provider`, `tier`, `speed`, `multimodal` |

---

## Bugs Fixed (this session)

| Commit | File | Fix |
|--------|------|-----|
| `6943fb9` | `backend/app/main.py:13` | `CORS_ORIGINS=""` or trailing comma produced `[""]`, blocking all cross-origin requests. Now filters empty strings. |
| `ab82b67` | `frontend/src/api.js:4` | Hardcoded `http://127.0.0.1:8000` broke every non-localhost deployment. Now reads `REACT_APP_API_URL` env var. |
| `5d59a0b` | `frontend/src/App.js:61` | Clearing a token input set value to `0` via `parseInt \|\| 0`, causing a Pydantic 422 misreported as "Is the backend running?". Added `>= 1` guard before API call. |
| `5d59a0b` | `frontend/src/App.js:90` | ModelCard showed stale cost from the previous calculation after changing the model dropdown. Fixed by matching `results.find` on both provider AND model. |
| `3f24fd7` | `frontend/src/components/ModelSelector.js:22` | JS dropped trailing zeros: `2.00` rendered as `$2`, `0.10` as `$0.1`. Fixed with `.toFixed(2)`. |
| `760faa2` | `frontend/src/components/PriceTable.js:17` | Row `key={item.provider}` would cause React duplicate-key warnings. Changed to `provider-model` composite. |
| `7ed8b5e` | `frontend/src/App.test.js:4` | Default CRA test checked for "learn react" — app never rendered that text, so the entire test suite was permanently failing. Updated to assert actual heading. |
| `dad6255` | `BarChart.js` + `PieChart.js` | Identical `colors` arrays duplicated. Extracted to shared `frontend/src/chartColors.js`. |
| `67fbce2` | `frontend/Dockerfile` | `REACT_APP_API_URL` was not passed as a build arg, so Docker builds always used the localhost fallback. Added `ARG`/`ENV` before `npm run build`. |

---

## Remaining Known Issues (non-critical)

- `pricing` is loaded once at startup — updating `pricing.json` on disk requires a process restart (no hot-reload).
- `/calculate` silently returns HTTP 200 with empty results for unrecognised model names (e.g. stale client still sending old model name after a rename). No error is surfaced to the caller.
- No `last_updated` timestamp on pricing data.

---

## Deployment

### Recommended: Render (backend) + Vercel (frontend)

#### 1. Deploy backend on Render
- New Web Service → connect repo → Root directory: `backend` → Runtime: **Docker**
- Environment variable:
  ```
  CORS_ORIGINS=https://<your-frontend>.vercel.app
  ```

#### 2. Deploy frontend on Vercel
- Import repo → Root directory: `frontend` → Framework: Create React App
- Environment variable:
  ```
  REACT_APP_API_URL=https://<your-backend>.onrender.com
  ```
- **Note:** CRA bakes env vars at build time — changing `REACT_APP_API_URL` requires a redeploy.

### Alternative: Railway
Same pattern — create two services from the same repo, one pointing at `backend/`, one at `frontend/`, set the same two env vars.

### Docker (manual)
```bash
# Backend
cd backend
docker build -t ai-price-checker-backend .
docker run -p 8000:8000 -e CORS_ORIGINS=http://localhost:3000 ai-price-checker-backend

# Frontend
cd frontend
docker build --build-arg REACT_APP_API_URL=http://localhost:8000 -t ai-price-checker-frontend .
docker run -p 80:80 ai-price-checker-frontend
```
