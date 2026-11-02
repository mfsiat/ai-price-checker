"""Tests for the /, /health, /providers, and /models endpoints."""

from fastapi.testclient import TestClient

from app.main import app, repository

client = TestClient(app)


def test_health_reports_status_and_pricing_metadata():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "running"
    assert "environment" in body
    assert body["pricing"]["model_count"] == repository.model_count
    assert body["pricing"]["provider_count"] == len(repository.providers)


def test_health_alias_matches_root():
    assert client.get("/health").json() == client.get("/").json()


def test_providers_returns_metadata_and_providers():
    response = client.get("/providers")
    assert response.status_code == 200
    body = response.json()
    assert "last_updated" in body
    assert "version" in body
    assert "source" in body
    assert isinstance(body["providers"], dict)
    assert len(body["providers"]) == len(repository.providers)


def test_models_unfiltered_returns_all_providers():
    response = client.get("/models")
    assert response.status_code == 200
    assert len(response.json()) == len(repository.providers)


def test_models_filtered_by_provider():
    provider = next(iter(repository.providers))
    response = client.get("/models", params={"provider": provider})
    body = response.json()
    assert list(body.keys()) == [provider]


def test_models_filtered_by_multimodal():
    response = client.get("/models", params={"multimodal": "true"})
    body = response.json()
    for pdata in body.values():
        for mdata in pdata["models"].values():
            assert mdata["multimodal"] is True
