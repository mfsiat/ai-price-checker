"""Centralized, environment-driven application configuration.

All runtime configuration is read from environment variables here, in one
place, so the rest of the app never calls ``os.getenv`` directly. Parsing and
production-safety rules live with the values they validate.

Environment variables
---------------------
- ``ENVIRONMENT``   one of ``development`` (default) | ``staging`` | ``production``
- ``CORS_ORIGINS``  comma-separated list of allowed browser origins
                    (default ``http://localhost:3000`` for local dev)
- ``LOG_LEVEL``     standard logging level name (default ``INFO``)
- ``PRICING_FILE``  optional override path to the pricing JSON file
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_CORS_ORIGIN = "http://localhost:3000"


class ConfigError(RuntimeError):
    """Raised when configuration is invalid for the target environment."""


def _parse_origins(raw: str) -> list[str]:
    """Split a comma-separated origins string into a clean list.

    Empty entries and stray whitespace (e.g. a trailing comma) are dropped so
    an env value like ``"a.com, , b.com,"`` never yields empty origins that
    would silently break CORS.
    """
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@dataclass(frozen=True)
class Settings:
    """Immutable, validated view of the process environment."""

    environment: str = "development"
    cors_origins: list[str] = field(default_factory=lambda: [DEFAULT_CORS_ORIGIN])
    log_level: str = "INFO"
    pricing_file: Path | None = None

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    def validate(self) -> Settings:
        """Fail fast on configuration that is unsafe for production.

        A wildcard CORS origin combined with ``allow_credentials=True`` is both
        insecure and rejected by browsers, so it must never reach production.
        """
        if self.is_production:
            if not self.cors_origins:
                raise ConfigError(
                    "CORS_ORIGINS must be set to explicit origins in production."
                )
            if "*" in self.cors_origins:
                raise ConfigError(
                    "Wildcard CORS origin '*' is not allowed in production; "
                    "set CORS_ORIGINS to explicit frontend origins."
                )
        return self


def load_settings(env: dict[str, str] | None = None) -> Settings:
    """Build :class:`Settings` from the environment (or an explicit mapping).

    Passing ``env`` makes this trivially testable without mutating the real
    process environment.
    """
    env = os.environ if env is None else env

    raw_origins = env.get("CORS_ORIGINS", DEFAULT_CORS_ORIGIN)
    origins = _parse_origins(raw_origins)
    # An env var set to only commas/whitespace would parse to []; fall back to
    # the safe local default rather than booting with no allowed origins.
    if not origins:
        origins = [DEFAULT_CORS_ORIGIN]

    pricing_override = env.get("PRICING_FILE")

    return Settings(
        environment=env.get("ENVIRONMENT", "development").strip().lower() or "development",
        cors_origins=origins,
        log_level=env.get("LOG_LEVEL", "INFO").strip().upper() or "INFO",
        pricing_file=Path(pricing_override) if pricing_override else None,
    ).validate()
