"""FastAPI application wiring.

This module stays deliberately thin: it loads configuration, sets up logging,
builds the pricing repository, registers middleware/handlers, and declares
routes. All business logic lives in :mod:`app.services`.
"""

from __future__ import annotations

import time

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from .config import load_settings
from .errors import register_exception_handlers
from .logging_config import configure_logging
from .models import UsageRequest
from .services import PricingRepository

settings = load_settings()
logger = configure_logging(settings.log_level)

# Exposed at module level because deployment/config tests assert on it.
allowed_origins = settings.cors_origins

app = FastAPI(title="AI Price Checker API", version="1.0.0")

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load pricing once at startup; a bad dataset fails loudly here rather than
# on the first request. Use repository.reload() to refresh without a restart.
repository = PricingRepository(path=settings.pricing_file)
logger.info(
    "Pricing loaded: %d models across %d providers (last_updated=%s, version=%s)",
    repository.model_count,
    len(repository.providers),
    repository.last_updated,
    repository.version,
)


@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    """Log every request with its status code and wall-clock duration."""
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s -> %d (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.get("/")
def health():
    """Liveness + readiness check (also used as the platform health check path)."""
    return {
        "status": "running",
        "environment": settings.environment,
        "pricing": repository.metadata(),
    }


@app.get("/health")
def health_detailed():
    """Alias of ``/`` for conventional ``/health`` probes."""
    return health()


@app.get("/providers")
def get_providers():
    return {**repository.metadata(), "providers": repository.providers}


@app.post("/calculate")
def calculate(request: UsageRequest):
    results, warnings = repository.compute_comparison(
        request.selected_models,
        request.input_tokens,
        request.output_tokens,
        request.requests_per_day,
    )
    if warnings:
        logger.warning(
            "Calculation skipped %d unknown model(s): %s",
            len(warnings),
            ", ".join(f"{w['provider']}/{w['model']}" for w in warnings),
        )
    return {"results": results, "warnings": warnings}


@app.get("/models")
def get_models(
    provider: str = None,
    tier: str = None,
    speed: str = None,
    multimodal: bool = None,
):
    return repository.filter_models(
        provider=provider, tier=tier, speed=speed, multimodal=multimodal
    )
