from pydantic import BaseModel
from typing import Dict


class UsageRequest(BaseModel):
    input_tokens: int
    output_tokens: int
    requests_per_day: int
    selected_models: Dict[str, str]


class ProviderCost(BaseModel):
    provider: str
    model: str
    monthly_cost: float
