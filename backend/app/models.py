from pydantic import BaseModel, Field


class UsageRequest(BaseModel):
    """Request body for POST /calculate.

    Token/volume fields must be positive integers (``gt=0``), rejected as HTTP
    422 before any pricing math runs.
    """


    input_tokens: int = Field(gt=0)
    output_tokens: int = Field(gt=0)
    requests_per_day: int = Field(gt=0)
    selected_models: dict[str, str]
