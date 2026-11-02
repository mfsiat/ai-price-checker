"""Unit tests for the pure cost-calculation helper."""

from app.calculator import calculate_cost


def test_basic_monthly_cost():
    # 1M input tokens @ $2/M + 1M output @ $8/M = $10 per request,
    # 1 request/day * 30 days = $300.
    cost = calculate_cost(2.0, 8.0, 1_000_000, 1_000_000, 1)
    assert cost == 300.0


def test_cost_scales_with_requests_per_day():
    one = calculate_cost(2.0, 8.0, 1000, 500, 1)
    hundred = calculate_cost(2.0, 8.0, 1000, 500, 100)
    assert round(hundred, 6) == round(one * 100, 6)


def test_cost_is_rounded_to_cents():
    cost = calculate_cost(0.1, 0.4, 333, 777, 7)
    # Two decimal places at most.
    assert cost == round(cost, 2)


def test_zero_priced_model_is_free():
    assert calculate_cost(0, 0, 10_000, 10_000, 1000) == 0.0
