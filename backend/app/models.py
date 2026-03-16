from pydantic import BaseModel
from typing import List


class UsageRequest(BaseModel):
    input_tokens: int
    output_tokens: int
    requests_per_day: int
    providers: List[str]


class ProviderCost(BaseModel):
    provider: str
    model: str
    monthly_cost: float
