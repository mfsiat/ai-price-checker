"""Minimal, dependency-free logging setup.

Logs go to stdout so they are captured by the container platform (Render,
Docker, etc.) without any extra configuration. The level is driven by
``LOG_LEVEL`` via :mod:`app.config`.
"""

from __future__ import annotations

import logging

LOGGER_NAME = "ai_price_checker"

_LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def configure_logging(level: str = "INFO") -> logging.Logger:
    """Configure and return the application logger.

    Idempotent: calling it more than once (e.g. on module reload in tests)
    reconfigures the level without stacking duplicate handlers.
    """
    logging.basicConfig(level=level, format=_LOG_FORMAT)
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger(LOGGER_NAME)
