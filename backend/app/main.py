from fastapi import FastAPI
from .models import UsageRequest
from .services import load_pricing
from .calculator import calculate_cost

app = FastAPI(title="AI Price Checker API")

pricing_data = load_pricing()


@app.get("/")
def health():
    return {"status": "running"}


@app.get("/providers")
def get_providers():
    return pricing_data


@app.post("/calculate")
def calculate(request: UsageRequest):

    results = []

    for provider in request.providers:

        if provider not in pricing_data:
            continue

        pricing = pricing_data[provider]

        cost = calculate_cost(
            pricing,
            request.input_tokens,
            request.output_tokens,
            request.requests_per_day
        )

        results.append({
            "provider": provider,
            "model": pricing["model"],
            "monthly_cost": cost
        })

    return {"results": results}
