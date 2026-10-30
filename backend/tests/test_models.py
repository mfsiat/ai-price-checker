"""Tests for UsageRequest input validation (issue #11).

`input_tokens`, `output_tokens`, and `requests_per_day` must be positive
integers. Zero or negative values are nonsensical for a cost calculation,
so the Pydantic `Field(gt=0)` constraints should reject them before any
pricing math runs.
"""

import pytest
from pydantic import ValidationError

from app.models import UsageRequest

VALID_PAYLOAD = {
    "input_tokens": 2000,
    "output_tokens": 500,
    "requests_per_day": 1000,
    "selected_models": {"anthropic": "claude-opus-4-8"},
}

CONSTRAINED_FIELDS = ["input_tokens", "output_tokens", "requests_per_day"]


def test_valid_payload_is_accepted():
    request = UsageRequest(**VALID_PAYLOAD)
    assert request.input_tokens == 2000
    assert request.output_tokens == 500
    assert request.requests_per_day == 1000
    assert request.selected_models == {"anthropic": "claude-opus-4-8"}


@pytest.mark.parametrize("field", CONSTRAINED_FIELDS)
@pytest.mark.parametrize("bad_value", [0, -1, -1000])
def test_non_positive_values_are_rejected(field, bad_value):
    payload = {**VALID_PAYLOAD, field: bad_value}
    with pytest.raises(ValidationError) as exc_info:
        UsageRequest(**payload)

    errors = exc_info.value.errors()
    assert any(err["loc"] == (field,) for err in errors), errors


@pytest.mark.parametrize("field", CONSTRAINED_FIELDS)
def test_smallest_positive_value_is_accepted(field):
    payload = {**VALID_PAYLOAD, field: 1}
    request = UsageRequest(**payload)
    assert getattr(request, field) == 1
