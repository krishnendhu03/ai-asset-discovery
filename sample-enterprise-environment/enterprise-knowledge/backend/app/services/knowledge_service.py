import joblib
from pathlib import Path

from app.models.knowledge import KnowledgeRequest


# =========================================================
# LOCAL ML MODEL
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BASE_DIR
    / "ml"
    / "artifacts"
    / "enterprise_knowledge_model.joblib"
)

ml_model = joblib.load(MODEL_PATH)


# =========================================================
# ENTERPRISE KNOWLEDGE BASE
# =========================================================

KNOWLEDGE_BASE = [
    {
        "category": "p1",
        "keywords": ["p1", "critical", "major outage"],
        "answer": (
            "P1 incidents must be acknowledged immediately and "
            "the on-call engineering team should be engaged without delay."
        ),
        "source": "Incident Response Policy",
    },
    {
        "category": "p2",
        "keywords": ["p2", "high priority", "high severity"],
        "answer": (
            "P2 incidents must be acknowledged within 15 minutes. "
            "The responsible support team should begin investigation "
            "and escalate to the appropriate engineering team when required."
        ),
        "source": "Incident Response Policy",
    },
    {
        "category": "p3",
        "keywords": ["p3", "medium priority", "medium severity"],
        "answer": (
            "P3 incidents should be acknowledged within 1 hour. "
            "The assigned support employee should investigate the issue "
            "and escalate if the impact increases."
        ),
        "source": "Incident Response Policy",
    },
    {
        "category": "access_approval",
        "keywords": [
            "approval",
            "production access",
            "access request",
        ],
        "answer": (
            "Production access requests require approval from the "
            "employee's manager followed by the designated service owner."
        ),
        "source": "Access Approval Policy",
    },
    {
        "category": "escalation",
        "keywords": [
              "escalation",
              "escalate",
              "engineering",
              "engineering team",
              "cannot be fixed",
              "cannot fix",
              "cannot resolve",
              "cannot be resolved",
              "unresolved",
              "troubleshooting does not resolve",
              "troubleshooting cannot resolve",
              "serious incident",
],
        "answer": (
            "Support employees should first perform the standard "
            "troubleshooting procedure. If the issue cannot be resolved "
            "within the applicable response window, it should be escalated "
            "to the responsible engineering team."
        ),
        "source": "Support Escalation Procedure",
    },
    {
        "category": "support_tools",
        "keywords": [
            "support tool",
            "ticketing",
            "incident tool",
        ],
        "answer": (
            "Support employees use the incident management platform "
            "for incident tracking, the service monitoring platform "
            "for health checks, and the knowledge portal for operational guidance."
        ),
        "source": "Support Tools Guide",
    },
]


# =========================================================
# CATEGORY LOOKUP
# =========================================================

CATEGORY_MAP = {
    entry["category"]: entry
    for entry in KNOWLEDGE_BASE
}


# =========================================================
# KEYWORD FALLBACK
# =========================================================

def keyword_fallback(question: str):
    matched_entry = None
    matched_keywords = 0

    for entry in KNOWLEDGE_BASE:
        matches = sum(
            1
            for keyword in entry["keywords"]
            if keyword in question
        )

        if matches > matched_keywords:
            matched_keywords = matches
            matched_entry = entry

    if matched_entry:
        return {
            "answer": matched_entry["answer"],
            "sources": [matched_entry["source"]],
            "confidence": (
                "High"
                if matched_keywords >= 2
                else "Medium"
            ),
        }

    return {
        "answer": (
            "No specific enterprise knowledge article matched "
            "the question. Please consult the support knowledge "
            "portal or contact the appropriate support lead."
        ),
        "sources": [],
        "confidence": "Low",
    }


# =========================================================
# ML + KNOWLEDGE SEARCH
# =========================================================

def search_knowledge(request: KnowledgeRequest) -> dict:

    question = request.question.strip()

    if not question:
        return {
            "answer": "Please provide a question.",
            "sources": [],
            "confidence": "Low",
        }

    normalized_question = question.lower()

    # -----------------------------------------------------
    # STEP 1: LOCAL ML PREDICTION
    # -----------------------------------------------------

    predicted_category = ml_model.predict(
        [question]
    )[0]

    probabilities = ml_model.predict_proba(
        [question]
    )[0]

    confidence_score = max(probabilities)

    # -----------------------------------------------------
    # STEP 2: ML RESULT
    # -----------------------------------------------------

    if (
       confidence_score >= 0.50
       and predicted_category in CATEGORY_MAP
   ):
       entry = CATEGORY_MAP[predicted_category]

       confidence_label = (
        "High"
        if confidence_score >= 0.60
        else "Medium"
       )

       return {
        "answer": entry["answer"],
        "sources": [entry["source"]],
        "confidence": confidence_label,
    }

    # -----------------------------------------------------
    # STEP 3: FALLBACK TO KEYWORD SEARCH
    # -----------------------------------------------------

    fallback_result = keyword_fallback(
        normalized_question
    )

    return fallback_result