from pydantic import BaseModel
from typing import List


class Evidence(BaseModel):
    type: str
    value: str
    file: str


class AIAsset(BaseModel):
    id: str
    name: str

    # Enterprise inventory fields
    asset_type: str
    model: str
    provider: str
    location: str
    application: str
    purpose: str
    discovery_source: str
    status: str

    # Existing classification fields
    category: str
    confidence: str

    evidence: List[Evidence]

    description: str