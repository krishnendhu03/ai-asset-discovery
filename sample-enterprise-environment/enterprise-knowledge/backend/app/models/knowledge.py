from pydantic import BaseModel


class KnowledgeRequest(BaseModel):
    question: str


class KnowledgeResponse(BaseModel):
    answer: str
    sources: list[str]
    confidence: str