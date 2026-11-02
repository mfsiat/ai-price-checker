"""Standardized error responses.

Every error the API returns uses one consistent envelope::

    {"error": {"code": "<machine_code>", "message": "<human text>", "details": ...}}

This replaces FastAPI's two different default shapes (``{"detail": "..."}`` for
HTTP errors and ``{"detail": [...]}`` for validation errors) with a single,
predictable structure that clients can branch on.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .logging_config import get_logger

logger = get_logger()


def error_body(code: str, message: str, details: Any = None) -> dict[str, Any]:
    body: dict[str, Any] = {"error": {"code": code, "message": message}}
    if details is not None:
        body["error"]["details"] = details
    return body


def register_exception_handlers(app: FastAPI) -> None:
    """Attach handlers that render every error in the standard envelope."""

    @app.exception_handler(RequestValidationError)
    async def _validation_handler(request: Request, exc: RequestValidationError):
        # errors() can contain non-JSON-serializable context (e.g. exceptions);
        # str() keeps the response safe to serialize.
        details = [
            {"loc": list(err.get("loc", [])), "msg": err.get("msg"), "type": err.get("type")}
            for err in exc.errors()
        ]
        logger.warning("Validation error on %s %s: %s", request.method, request.url.path, details)
        return JSONResponse(
            status_code=422,
            content=error_body("validation_error", "Request validation failed.", details),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(
            "HTTP %s on %s %s: %s", exc.status_code, request.method, request.url.path, exc.detail
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_body("http_error", str(exc.detail)),
        )

    @app.exception_handler(Exception)
    async def _unhandled_handler(request: Request, exc: Exception):
        # Never leak internals to the client; log the full detail server-side.
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content=error_body("internal_error", "An unexpected error occurred."),
        )
