"""Tests that CORS origins are restricted, not wildcarded (issue #15).

The app must never fall back to ``allow_origins=["*"]``. Origins come from the
``CORS_ORIGINS`` env var and default to ``http://localhost:3000`` for local dev.
"""

import importlib

from fastapi.testclient import TestClient

import app.main as main


def _client_with_cors(monkeypatch, value):
    """Reload the app with CORS_ORIGINS set to ``value`` and return a client."""
    if value is None:
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
    else:
        monkeypatch.setenv("CORS_ORIGINS", value)
    reloaded = importlib.reload(main)
    return TestClient(reloaded.app), reloaded


def test_default_origin_is_localhost_not_wildcard(monkeypatch):
    client, reloaded = _client_with_cors(monkeypatch, None)
    try:
        assert reloaded.allowed_origins == ["http://localhost:3000"]
        assert "*" not in reloaded.allowed_origins

        response = client.get("/", headers={"Origin": "http://localhost:3000"})
        allow_origin = response.headers.get("access-control-allow-origin")
        assert allow_origin == "http://localhost:3000"
        assert allow_origin != "*"
    finally:
        importlib.reload(main)  # restore default module state for other tests


def test_unlisted_origin_is_not_allowed(monkeypatch):
    client, _ = _client_with_cors(monkeypatch, None)
    try:
        response = client.get("/", headers={"Origin": "http://evil.example.com"})
        # Starlette omits the header entirely when the origin isn't allowed.
        assert response.headers.get("access-control-allow-origin") != "*"
        assert response.headers.get("access-control-allow-origin") != "http://evil.example.com"
    finally:
        importlib.reload(main)


def test_origins_read_from_env_var(monkeypatch):
    client, reloaded = _client_with_cors(
        monkeypatch, "https://app.example.com, https://admin.example.com"
    )
    try:
        assert reloaded.allowed_origins == [
            "https://app.example.com",
            "https://admin.example.com",
        ]

        response = client.get("/", headers={"Origin": "https://admin.example.com"})
        assert response.headers.get("access-control-allow-origin") == "https://admin.example.com"
    finally:
        importlib.reload(main)
