from app.models.analysis import IncidentAnalysis
from app.models.incident import Incident

from app.services.ai_provider import AIProvider
from app.services.local_analyzer import analyze_incident_locally


class LocalAIProvider(AIProvider):

    def analyze(
        self,
        incident: Incident,
    ) -> IncidentAnalysis:
        return analyze_incident_locally(incident)