from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .calculator import calculate_cost
from .models import UsageRequest
from .services import load_pricing

app = FastAPI(title="AI Price Checker API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow frontend to access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pricing_data = load_pricing()


@app.get("/")
def health():
    return {"status": "running"}


@app.get("/providers")
def get_providers():
    return pricing_data


# @app.post("/calculate")
# def calculate(request: UsageRequest):

#     results = []

#     for provider in request.providers:

#         if provider not in pricing_data:
#             continue

#         pricing = pricing_data[provider]

#         cost = calculate_cost(
#             pricing,
#             request.input_tokens,
#             request.output_tokens,
#             request.requests_per_day
#         )

#         results.append({
#             "provider": provider,
#             "model": pricing["model"],
#             "monthly_cost": cost
#         })

#     return {"results": results}
#     return {"results": results}
#     return {"results": results}

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

        daily_cost = (
            (request.input_tokens / 1000) * input_cost +
            (request.output_tokens / 1000) * output_cost
        ) * request.requests_per_day

        monthly_cost = daily_cost * 30

        results.append({
            "provider": provider,
            "model": model,
            "monthly_cost": round(monthly_cost, 2),
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