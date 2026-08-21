from pydantic import BaseModel


class AssistRequest(BaseModel):
    issue: str
    service: str | None = None


class AssistResponse(BaseModel):
    possible_cause: str
    troubleshooting_steps: list[str]
    recommended_action: str
    confidence: str