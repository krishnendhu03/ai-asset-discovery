import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.models.incident import Incident
from app.services.local_analyzer import analyze_incident_locally

router = APIRouter(prefix="/incidents", tags=["Incidents"])


DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "incidents.json"
)


def load_incidents() -> list[Incident]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return [Incident(**incident) for incident in data]


@router.get("/", response_model=list[Incident])
def get_incidents():
    return load_incidents()


@router.get("/{incident_id}", response_model=Incident)
def get_incident(incident_id: str):
    incidents = load_incidents()

    for incident in incidents:
        if incident.id == incident_id:
            return incident

    raise HTTPException(
        status_code=404,
        detail="Incident not found",
    )

    
@router.post("/{incident_id}/analyze")
def analyze_incident_endpoint(incident_id: str):
    incidents = load_incidents()

    for incident in incidents:
        if incident.id == incident_id:
            analysis = analyze_incident_locally(incident)
            return {
                "incident_id": incident.id,
                "analysis": analysis
            }

    raise HTTPException(
        status_code=404,
        detail="Incident not found",
    )
    