from pydantic import BaseModel
from typing import List, Optional


class Evidence(BaseModel):
    type: str
    value: str
    file: str
    line_number: Optional[int] = None


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