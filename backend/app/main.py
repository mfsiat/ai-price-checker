import json
import threading
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models import UsageRequest

# -----------------------------
# Initialize FastAPI
# -----------------------------
app = FastAPI(title="AI Price Checker API")

# -----------------------------
# Enable CORS (for frontend)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Load Pricing Data
# -----------------------------
def load_pricing():
    with open("app/pricing.json") as f:
        return json.load(f)

pricing = load_pricing()

# -----------------------------
# Optional: Auto-refresh pricing (every 1 hour)
# -----------------------------
def refresh_pricing():
    global pricing
    while True:
        try:
            pricing = load_pricing()
        except Exception as e:
            print("Pricing reload failed:", e)
        time.sleep(3600)

threading.Thread(target=refresh_pricing, daemon=True).start()

# -----------------------------
# Health Check
# -----------------------------
@app.get("/")
def health():
    return {"status": "running"}

# -----------------------------
# Get All Providers & Models
# -----------------------------
@app.get("/providers")
def get_providers():
    return pricing

# -----------------------------
# Filter Models (Optional Advanced API)
# -----------------------------
@app.get("/models")
def get_models(
    provider: str = None,
    tier: str = None,
    speed: str = None,
    multimodal: bool = None
):
    result = {}

    for p, pdata in pricing.items():
        if provider and p != provider:
            continue

        models = {}

        for m, mdata in pdata["models"].items():
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

# -----------------------------
# Calculate Pricing
# -----------------------------
@app.post("/calculate")
def calculate(request: UsageRequest):
    results = []

    for provider, model in request.selected_models.items():
        if provider not in pricing:
            continue

        model_data = pricing[provider]["models"].get(model)
        if not model_data:
            continue

        input_cost = model_data["input"]
        output_cost = model_data["output"]

        # Cost per request
        cost_per_request = (
            (request.input_tokens / 1000) * input_cost +
            (request.output_tokens / 1000) * output_cost
        )

        # Daily & Monthly
        daily_cost = cost_per_request * request.requests_per_day
        monthly_cost = daily_cost * 30

        results.append({
            "provider": provider,
            "model": model,
            "monthly_cost": round(monthly_cost, 2),

            # Extra metadata (from pricing.json)
            "context": model_data.get("context"),
            "speed": model_data.get("speed"),
            "tier": model_data.get("tier"),
            "multimodal": model_data.get("multimodal"),
            "vision": model_data.get("vision")
        })

    return {"results": results}