from pathlib import Path

import joblib

from app.models.incident import Incident


BASE_DIR = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = BASE_DIR / "ml" / "artifacts"


# Load trained ML models
category_model = joblib.load(
    ARTIFACTS_DIR / "category_model.joblib"
)

severity_model = joblib.load(
    ARTIFACTS_DIR / "severity_model.joblib"
)

team_model = joblib.load(
    ARTIFACTS_DIR / "team_model.joblib"
)


def analyze_incident_locally(incident: Incident) -> dict:
    """
    Analyze an incident using the locally trained ML models
    and generate additional incident-specific intelligence.
    """

    text = f"""
    Title: {incident.title}
    Description: {incident.description}
    Service: {incident.service}
    Status: {incident.status}
    """

    # ---------------------------------------------------------
    # ML PREDICTIONS
    # ---------------------------------------------------------

    category = category_model.predict([text])[0]
    severity = severity_model.predict([text])[0]
    team = team_model.predict([text])[0]

    # ---------------------------------------------------------
    # NORMALIZED TEXT FOR RULE-BASED INTELLIGENCE
    # ---------------------------------------------------------

    incident_text = (
        f"{incident.title} "
        f"{incident.description} "
        f"{incident.service}"
    ).lower()

    # ---------------------------------------------------------
    # DEFAULT INTELLIGENCE
    # ---------------------------------------------------------

    possible_causes = [
        "Recent deployment or configuration changes",
        "Service dependency or infrastructure issues",
    ]

    impact = (
        "The incident may affect users of the impacted service "
        "and could reduce service reliability."
    )

    risks = [
        "Continued service degradation",
        "Additional user impact if the issue persists",
    ]

    recommended_actions = [
        "Review service health and error metrics",
        "Check recent deployments and configuration changes",
        "Review application and infrastructure logs",
    ]

    # ---------------------------------------------------------
    # PAYMENT INCIDENTS
    # ---------------------------------------------------------

    if (
        "payment" in incident_text
        or "transaction" in incident_text
        or "billing" in incident_text
    ):
        possible_causes = [
            "Payment service latency or downstream dependency failure",
            "Increased request volume or resource contention",
            "Recent payment-service deployment or configuration change",
        ]

        impact = (
            "Users may experience failed, delayed, or incomplete "
            "payment transactions."
        )

        risks = [
            "Repeated payment failures",
            "Delayed transactions",
            "Potential customer and revenue impact",
        ]

        recommended_actions = [
            "Check Payment API latency and error rates",
            "Review downstream payment dependencies",
            "Check recent payment-service deployments",
            "Review timeout and transaction failure logs",
        ]

    # ---------------------------------------------------------
    # AUTHENTICATION INCIDENTS
    # ---------------------------------------------------------

    elif (
        "authentication" in incident_text
        or "login" in incident_text
        or "log in" in incident_text
        or "identity" in incident_text
    ):
        possible_causes = [
            "Authentication or identity-service failure",
            "Invalid authentication configuration or token issues",
            "Recent identity-service deployment or dependency failure",
        ]

        impact = (
            "Users may be unable to authenticate and access "
            "enterprise applications."
        )

        risks = [
            "Increasing number of users unable to access the application",
            "Authentication failure rate may continue to increase",
            "Potential disruption to dependent services",
        ]

        recommended_actions = [
            "Check Identity Service health and authentication error rates",
            "Review recent authentication deployments",
            "Check token, session, and identity-provider errors",
            "Determine whether the issue affects multiple users",
        ]

    # ---------------------------------------------------------
    # DOCUMENT PROCESSING INCIDENTS
    # ---------------------------------------------------------

    elif (
        "document" in incident_text
        or "processing" in incident_text
        or "queue" in incident_text
    ):
        possible_causes = [
            "Document-processing queue growth",
            "Insufficient processing-worker capacity",
            "Slow downstream processing dependency",
        ]

        impact = (
            "Users may experience delays while documents are "
            "processed and completed."
        )

        risks = [
            "Processing backlog may continue to increase",
            "Processing delays may affect more users",
            "Queue growth could eventually cause service degradation",
        ]

        recommended_actions = [
            "Check document-processing queue depth",
            "Review worker health and processing capacity",
            "Check processing latency and failure rates",
            "Review recent deployments and configuration changes",
        ]

    # ---------------------------------------------------------
    # CUSTOMER SERVICE INCIDENTS
    # ---------------------------------------------------------

    elif (
        "customer service" in incident_text
        or "customer" in incident_text
        or "timeout" in incident_text
    ):
        possible_causes = [
            "Customer-service API timeout",
            "Downstream dependency latency",
            "Recent deployment or infrastructure issue",
        ]

        impact = (
            "Users may experience delays or failures when "
            "accessing customer-service functionality."
        )

        risks = [
            "Repeated timeout failures",
            "Increased user-facing errors",
            "Potential escalation if the service remains unavailable",
        ]

        recommended_actions = [
            "Check customer-service API health",
            "Review timeout and error metrics",
            "Check downstream dependency latency",
            "Review recent deployments and application logs",
        ]

    # ---------------------------------------------------------
    # CONFIDENCE
    # ---------------------------------------------------------

    confidence = "Medium"

    # If the incident contains very clear domain-specific signals,
    # we can consider the generated intelligence more reliable.
    strong_keywords = [
        "payment",
        "authentication",
        "login",
        "document",
        "processing",
        "customer service",
        "timeout",
    ]

    if any(keyword in incident_text for keyword in strong_keywords):
        confidence = "High"

    # ---------------------------------------------------------
    # FINAL RESPONSE
    # ---------------------------------------------------------

    return {
        "summary": incident.description,
        "severity": severity,
        "category": category,
        "possible_causes": possible_causes,
        "impact": impact,
        "risks": risks,
        "recommended_actions": recommended_actions,
        "recommended_team": team,
        "reason": (
            "The recommendation is based on the incident's "
            "title, description, service, status, and detected "
            "incident characteristics."
        ),
        "confidence": confidence,
    }