import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .calculator import calculate_cost
from .models import UsageRequest
from .services import load_pricing

app = FastAPI(title="AI Price Checker API")

_raw = os.getenv("CORS_ORIGINS", "http://localhost:3000")
allowed_origins = [o.strip() for o in _raw.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pricing = load_pricing()


@app.get("/")
def health():
    return {"status": "running"}


@app.get("/providers")
def get_providers():
    return pricing


@app.post("/calculate")
def calculate(request: UsageRequest):
    results = []

    for provider, model in request.selected_models.items():
        if provider not in pricing:
            continue

        model_data = pricing[provider]["models"].get(model)
        if not model_data:
            continue

        monthly_cost = calculate_cost(
            model_data["input"],
            model_data["output"],
            request.input_tokens,
            request.output_tokens,
            request.requests_per_day,
        )

        results.append({
            "provider": provider,
            "model": model,
            "monthly_cost": monthly_cost,
            "context": model_data.get("context"),
            "speed": model_data.get("speed"),
            "tier": model_data.get("tier"),
            "multimodal": model_data.get("multimodal"),
            "vision": model_data.get("vision")
        })

    return {"results": results}

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