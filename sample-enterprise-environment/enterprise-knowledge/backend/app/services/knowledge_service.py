from app.models.knowledge import KnowledgeRequest


KNOWLEDGE_BASE = [
    {
        "keywords": ["p1", "critical", "major outage"],
        "answer": (
            "P1 incidents must be acknowledged immediately and "
            "the on-call engineering team should be engaged without delay."
        ),
        "source": "Incident Response Policy",
    },
    {
        "keywords": ["p2", "high priority", "high severity"],
        "answer": (
            "P2 incidents must be acknowledged within 15 minutes. "
            "The responsible support team should begin investigation "
            "and escalate to the appropriate engineering team when required."
        ),
        "source": "Incident Response Policy",
    },
    {
        "keywords": ["p3", "medium priority", "medium severity"],
        "answer": (
            "P3 incidents should be acknowledged within 1 hour. "
            "The assigned support employee should investigate the issue "
            "and escalate if the impact increases."
        ),
        "source": "Incident Response Policy",
    },
    {
        "keywords": ["approval", "production access", "access request"],
        "answer": (
            "Production access requests require approval from the "
            "employee's manager followed by the designated service owner."
        ),
        "source": "Access Approval Policy",
    },
    {
        "keywords": ["escalation", "escalate", "engineering team"],
        "answer": (
            "Support employees should first perform the standard "
            "troubleshooting procedure. If the issue cannot be resolved "
            "within the applicable response window, it should be escalated "
            "to the responsible engineering team."
        ),
        "source": "Support Escalation Procedure",
    },
    {
        "keywords": ["support tool", "ticketing", "incident tool"],
        "answer": (
            "Support employees use the incident management platform "
            "for incident tracking, the service monitoring platform "
            "for health checks, and the knowledge portal for operational guidance."
        ),
        "source": "Support Tools Guide",
    },
]


def search_knowledge(request: KnowledgeRequest) -> dict:
    question = request.question.strip().lower()

    if not question:
        return {
            "answer": "Please provide a question.",
            "sources": [],
            "confidence": "Low",
        }

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
                "High" if matched_keywords >= 2 else "Medium"
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