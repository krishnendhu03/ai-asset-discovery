from app.models.analysis import IncidentAnalysis
from app.models.incident import Incident

from app.services.local_provider import LocalAIProvider


provider = LocalAIProvider()


def analyze_incident(
    incident: Incident,
) -> IncidentAnalysis:

    return provider.analyze(incident)