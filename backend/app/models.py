from pydantic import BaseModel, Field
from typing import Dict


class UsageRequest(BaseModel):
    input_tokens: int = Field(gt=0)
    output_tokens: int = Field(gt=0)
    requests_per_day: int = Field(gt=0)
    selected_models: Dict[str, str]
