from abc import ABC, abstractmethod

from app.models.analysis import IncidentAnalysis
from app.models.incident import Incident


class AIProvider(ABC):

    @abstractmethod
    def analyze(
        self,
        incident: Incident,
    ) -> IncidentAnalysis:
        """Analyze an incident."""
        raise NotImplementedError