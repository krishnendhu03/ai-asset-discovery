from typing import List

from pydantic import BaseModel, Field


class AssistRequest(BaseModel):

    issue: str = Field(..., min_length=3)

    service: str = Field(..., min_length=1)


class AssistResponse(BaseModel):

    possible_cause: str

    troubleshooting_steps: List[str]

    recommended_action: str

    confidence: str

    confidence_score: float = 0.0