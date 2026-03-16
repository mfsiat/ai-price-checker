def calculate_cost(pricing, input_tokens, output_tokens, requests_per_day):

    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    cost_per_request = input_cost + output_cost
    monthly_cost = cost_per_request * requests_per_day * 30
    return round(monthly_cost, 2)
