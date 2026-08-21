from app.models.assist import AssistRequest


def generate_assistance(request: AssistRequest) -> dict:
    """
    Generate troubleshooting guidance for a support employee.

    This sample implementation uses deterministic local rules so that
    the application can run without requiring an external AI API.

    The rules intentionally require contextual evidence before selecting
    a specialized troubleshooting workflow.
    """

    issue = request.issue.strip().lower()
    service = (request.service or "").strip().lower()

    # ---------------------------------------------------------
    # Basic validation
    # ---------------------------------------------------------

    if not issue:
        return {
            "possible_cause": "No issue description was provided.",
            "troubleshooting_steps": [
                "Describe the problem experienced by the user.",
                "Include the affected service if known.",
                "Mention any error message or observable behavior.",
            ],
            "recommended_action": (
                "Provide additional incident details before "
                "attempting diagnosis."
            ),
            "confidence": "Low",
        }

    # ---------------------------------------------------------
    # Identity / Authentication
    # ---------------------------------------------------------

    identity_signals = [
        "login",
        "log in",
        "authentication",
        "authenticate",
        "sign in",
        "signin",
        "password",
        "access denied",
        "unauthorized",
    ]

    identity_issue = any(
        signal in issue
        for signal in identity_signals
    )

    identity_service = any(
        signal in service
        for signal in [
            "identity",
            "authentication",
            "login",
            "access",
        ]
    )

    if identity_issue and identity_service:
        return {
            "possible_cause": (
                "The issue may be related to authentication "
                "service failures or recent identity changes."
            ),
            "troubleshooting_steps": [
                "Check the authentication service health.",
                "Review recent authentication-related deployment logs.",
                "Check authentication failure rates.",
                "Verify whether the issue affects multiple users.",
            ],
            "recommended_action": (
                "If failures are affecting multiple users, "
                "route the issue to Identity Engineering."
            ),
            "confidence": "High",
        }

    # ---------------------------------------------------------
    # Payment
    # ---------------------------------------------------------

    payment_signals = [
        "payment failed",
        "payment failure",
        "payment timeout",
        "payment timed out",
        "transaction failed",
        "transaction timeout",
        "checkout failed",
        "checkout timeout",
    ]

    payment_issue = any(
        signal in issue
        for signal in payment_signals
    )

    payment_service = any(
        signal in service
        for signal in [
            "payment",
            "checkout",
            "transaction",
        ]
    )

    if payment_issue and payment_service:
        return {
            "possible_cause": (
                "The issue may be related to payment-service "
                "timeouts or downstream dependency latency."
            ),
            "troubleshooting_steps": [
                "Check Payment API health and error rates.",
                "Review recent payment-service deployments.",
                "Check downstream dependency latency.",
                "Review timeout-related application logs.",
            ],
            "recommended_action": (
                "Route persistent payment failures to "
                "Payments Engineering."
            ),
            "confidence": "High",
        }

    # ---------------------------------------------------------
    # Service-specific but insufficient evidence
    # ---------------------------------------------------------

    if identity_service:
        return {
            "possible_cause": (
                "The issue is associated with the Identity Service, "
                "but the available information is insufficient to "
                "identify a specific authentication problem."
            ),
            "troubleshooting_steps": [
                "Check Identity Service health.",
                "Review recent deployments or configuration changes.",
                "Review application and authentication logs.",
                "Check whether other users are experiencing the issue.",
            ],
            "recommended_action": (
                "Gather additional evidence before escalating "
                "to Identity Engineering."
            ),
            "confidence": "Low",
        }

    if payment_service:
        return {
            "possible_cause": (
                "The issue is associated with the Payment service, "
                "but the available information is insufficient to "
                "identify a specific payment failure."
            ),
            "troubleshooting_steps": [
                "Check Payment API health.",
                "Review recent deployments or configuration changes.",
                "Review payment-service error logs.",
                "Check downstream dependency health.",
            ],
            "recommended_action": (
                "Gather additional evidence before escalating "
                "to Payments Engineering."
            ),
            "confidence": "Low",
        }

    # ---------------------------------------------------------
    # Generic fallback
    # ---------------------------------------------------------

    service_name = request.service or "the affected service"

    return {
        "possible_cause": (
            f"The issue requires further investigation in "
            f"{service_name}."
        ),
        "troubleshooting_steps": [
            "Review the affected service health.",
            "Check recent deployments or configuration changes.",
            "Review application and error logs.",
            "Determine whether the issue affects multiple users.",
        ],
        "recommended_action": (
            "Investigate the service and escalate to the "
            "responsible engineering team if the issue persists."
        ),
        "confidence": "Low",
    }