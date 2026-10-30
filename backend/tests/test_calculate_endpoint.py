"""API-level tests that UsageRequest validation surfaces as HTTP 422 (issue #11)."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

VALID_PAYLOAD = {
    "input_tokens": 2000,
    "output_tokens": 500,
    "requests_per_day": 1000,
    "selected_models": {},
}


def test_calculate_accepts_valid_payload():
    response = client.post("/calculate", json=VALID_PAYLOAD)
    assert response.status_code == 200
    assert "results" in response.json()


@pytest.mark.parametrize("field", ["input_tokens", "output_tokens", "requests_per_day"])
def test_calculate_rejects_non_positive_tokens(field):
    payload = {**VALID_PAYLOAD, field: 0}
    response = client.post("/calculate", json=payload)
    assert response.status_code == 422
    body = response.json()
    assert any(err["loc"][-1] == field for err in body["detail"]), body
