def calculate_cost(input_cost_per_m, output_cost_per_m, input_tokens, output_tokens, requests_per_day):
    cost_per_request = (
        (input_tokens / 1_000_000) * input_cost_per_m +
        (output_tokens / 1_000_000) * output_cost_per_m
    )
    return round(cost_per_request * requests_per_day * 30, 2)
