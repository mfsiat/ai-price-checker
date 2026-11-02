def calculate_cost(
    input_cost_per_m: float,
    output_cost_per_m: float,
    input_tokens: int,
    output_tokens: int,
    requests_per_day: int,
) -> float:
    """Estimate the monthly cost for one model.

    Prices are USD per 1M tokens. Assumes a 30-day month. Returns dollars
    rounded to cents.
    """
    cost_per_request = (
        (input_tokens / 1_000_000) * input_cost_per_m
        + (output_tokens / 1_000_000) * output_cost_per_m
    )
    return round(cost_per_request * requests_per_day * 30, 2)
