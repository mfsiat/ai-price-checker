from typing import Dict

from pydantic import BaseModel


class UsageRequest(BaseModel):
    input_tokens: int
    output_tokens: int
    requests_per_day: int
    selected_models: Dict[str, str]  # { provider: model }    requests_per_day: int
    selected_models: Dict[str, str]  # { provider: model }