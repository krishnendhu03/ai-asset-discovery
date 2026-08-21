from pydantic import BaseModel


class Incident(BaseModel):
    id: str
    title: str
    description: str
    service: str
    status: str
    created_at: str