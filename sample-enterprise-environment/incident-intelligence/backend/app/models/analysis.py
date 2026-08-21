from typing import Literal

from pydantic import BaseModel, Field


class IncidentAnalysis(BaseModel):
    summary: str = Field(
        description="Concise summary of the incident."
    )

    severity: Literal["P1", "P2", "P3", "P4"] = Field(
        description="Incident severity."
    )

    category: str = Field(
        description="Category of the incident."
    )

    recommended_team: str = Field(
        description="Team that should handle the incident."
    )

    reason: str = Field(
        description="Reason for the recommended team and severity."
    )

    confidence: Literal["High", "Medium", "Low"] = Field(
        description="Confidence in the analysis."
    )