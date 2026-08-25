from pathlib import Path
import json
import joblib

from app.models.assist import AssistRequest, AssistResponse


# =========================================================
# PATHS
# =========================================================

# ai-assist/backend
BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BASE_DIR
    / "ml"
    / "artifacts"
    / "ai_assist_model.joblib"
)

TRAINING_DATA_PATH = (
    BASE_DIR
    / "ml"
    / "training_data.json"
)


# =========================================================
# CONFIGURATION
# =========================================================

# Minimum probability required for the local ML
# prediction to be considered reliable.
MODEL_CONFIDENCE_THRESHOLD = 0.60

DOMAIN_SIMILARITY_THRESHOLD = 0.35
# =========================================================
# LOCAL MODEL CACHE
# =========================================================

_model = None
_training_data = []


# =========================================================
# LOAD LOCAL ML MODEL
# =========================================================

def load_model():
    """
    Load the locally trained ML model.

    The model is loaded only once and then cached
    in memory for subsequent requests.
    """

    global _model

    # Already loaded
    if _model is not None:
        return _model

    # Model file does not exist
    if not MODEL_PATH.exists():

        print(
            f"WARNING: Local ML model not found at: "
            f"{MODEL_PATH}"
        )

        return None

    try:

        _model = joblib.load(MODEL_PATH)

        print(
            f"Local AI Assist model loaded from: "
            f"{MODEL_PATH}"
        )

        return _model

    except Exception as exc:

        print(
            f"WARNING: Could not load local ML model: "
            f"{exc}"
        )

        return None


# =========================================================
# LOAD TRAINING KNOWLEDGE
# =========================================================

def load_training_data():
    """
    Load the local training knowledge used to map
    predicted categories to troubleshooting responses.
    """

    global _training_data

    # Already loaded
    if _training_data:
        return _training_data

    # Training data does not exist
    if not TRAINING_DATA_PATH.exists():

        print(
            f"WARNING: Training data not found at: "
            f"{TRAINING_DATA_PATH}"
        )

        return []

    try:

        with open(
            TRAINING_DATA_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            _training_data = json.load(file)

        return _training_data

    except Exception as exc:

        print(
            f"WARNING: Could not load training data: "
            f"{exc}"
        )

        return []


# =========================================================
# GET TRUSTED CATEGORIES
# =========================================================

def get_trusted_categories():
    """
    Return categories explicitly present in the local
    training knowledge.

    A model prediction is only accepted when the
    predicted category is also known to the application.
    """

    data = load_training_data()

    return {
        item.get("category")
        for item in data
        if item.get("category")
    }


# =========================================================
# FIND RESPONSE FOR CATEGORY
# =========================================================

def get_category_response(category: str):
    """
    Find the troubleshooting knowledge associated
    with a predicted ML category.
    """

    data = load_training_data()

    matches = [
        item
        for item in data
        if item.get("category") == category
    ]

    if not matches:
        return None

    item = matches[0]

    return {
        "possible_cause": item.get(
            "possible_cause",
            "The issue requires further investigation."
        ),

        "troubleshooting_steps": item.get(
            "troubleshooting_steps",
            [
                "Check the affected service health.",
                "Review application logs.",
                "Review recent deployments."
            ]
        ),

        "recommended_action": item.get(
            "recommended_action",
            "Investigate the affected service."
        )
    }


# =========================================================
# DETERMINISTIC FALLBACK
# =========================================================

def deterministic_fallback(
    issue: str,
    service: str,
    confidence_score: float = 0.0
) -> AssistResponse:
    """
    Provide deterministic troubleshooting guidance
    when the local ML model is unavailable, uncertain,
    or unable to provide a trusted category.
    """

    issue_lower = issue.lower()
    service_lower = service.lower()

    # -----------------------------------------------------
    # PAYMENT
    # -----------------------------------------------------

    if (
        "payment" in issue_lower
        or "payment" in service_lower
    ):

        return AssistResponse(
            possible_cause=(
                "The payment issue may be caused by "
                "an application, configuration, or "
                "dependency problem."
            ),

            troubleshooting_steps=[
                "Check the payment service health.",
                "Review recent deployments or configuration changes.",
                "Review application and error logs.",
                "Check payment API latency and error rates.",
                "Determine whether the issue affects multiple users."
            ],

            recommended_action=(
                "Investigate the payment service and "
                "escalate to the responsible engineering "
                "team if the issue persists."
            ),

            confidence="Low",
            confidence_score=confidence_score
        )

    # -----------------------------------------------------
    # DATABASE
    # -----------------------------------------------------

    if (
        "database" in issue_lower
        or "database" in service_lower
        or service_lower == "db"
        or " db " in f" {service_lower} "
    ):

        return AssistResponse(
            possible_cause=(
                "The application may be experiencing "
                "database availability or connection problems."
            ),

            troubleshooting_steps=[
                "Check database availability.",
                "Review database connection pool usage.",
                "Review database error logs.",
                "Check network connectivity.",
                "Review recent database configuration changes."
            ],

            recommended_action=(
                "Investigate database health and "
                "connection availability."
            ),

            confidence="Low",
            confidence_score=confidence_score
        )

    # -----------------------------------------------------
    # AUTHENTICATION
    # -----------------------------------------------------

    if (
        "login" in issue_lower
        or "authentication" in issue_lower
        or "authorization" in issue_lower
        or "auth" in service_lower
    ):

        return AssistResponse(
            possible_cause=(
                "The authentication service may be "
                "rejecting requests or experiencing "
                "an availability issue."
            ),

            troubleshooting_steps=[
                "Check authentication service health.",
                "Review authentication logs.",
                "Verify recent authentication configuration changes.",
                "Check identity provider availability.",
                "Determine whether multiple users are affected."
            ],

            recommended_action=(
                "Investigate authentication service health "
                "and identity provider connectivity."
            ),

            confidence="Low",
            confidence_score=confidence_score
        )

    # -----------------------------------------------------
    # PERFORMANCE
    # -----------------------------------------------------

    if (
        "slow" in issue_lower
        or "latency" in issue_lower
        or "performance" in issue_lower
        or "timeout" in issue_lower
    ):

        return AssistResponse(
            possible_cause=(
                "The application may be experiencing "
                "elevated latency, timeout conditions, "
                "or resource contention."
            ),

            troubleshooting_steps=[
                "Check application response times.",
                "Review CPU and memory utilization.",
                "Review recent deployments.",
                "Check application and infrastructure logs.",
                "Identify whether multiple users are affected."
            ],

            recommended_action=(
                "Investigate application performance metrics "
                "and recent infrastructure changes."
            ),

            confidence="Low",
            confidence_score=confidence_score
        )

    # -----------------------------------------------------
    # GENERIC FALLBACK
    # -----------------------------------------------------

    return AssistResponse(
        possible_cause=(
            f"The issue appears to be a general "
            f"application or service problem requiring "
            f"further investigation in {service}."
        ),

        troubleshooting_steps=[
            "Check the affected service health.",
            "Review recent deployments or configuration changes.",
            "Review application and error logs.",
            "Check service latency and error rates.",
            "Determine whether the issue affects multiple users."
        ],

        recommended_action=(
            "Investigate the affected service and escalate "
            "to the responsible engineering team if the "
            "issue persists."
        ),

        confidence="Low",
        confidence_score=confidence_score
    )

# =========================================================
# GET MODEL CONFIDENCE
# =========================================================

def get_model_confidence(
    model,
    model_input: str
) -> float:
    """
    Calculate the highest class probability returned
    by the local ML model.

    Returns 0.0 when probability information is
    unavailable.
    """

    if not hasattr(model, "predict_proba"):
        return 0.0

    try:

        probabilities = model.predict_proba(
            [model_input]
        )[0]

        if len(probabilities) == 0:
            return 0.0

        return float(max(probabilities))

    except Exception as exc:

        print(
            f"WARNING: Could not calculate model confidence: "
            f"{exc}"
        )

        return 0.0

# =========================================================
# DOMAIN SIMILARITY CHECK
# =========================================================

def get_domain_similarity(
    model,
    issue: str
) -> float:
    """
    Measure how similar the incoming issue is to the
    known AI Assist training issues.

    The service name is intentionally excluded from
    this check so that a generic service such as
    "general" cannot make an unrelated question appear
    similar to the training domain.

    Returns a value between 0.0 and 1.0.
    """

    data = load_training_data()

    if not data:
        return 0.0

    try:

        # Get the TF-IDF vectorizer from the trained pipeline
        vectorizer = model.named_steps.get("vectorizer")

        if vectorizer is None:
            return 0.0

        # -------------------------------------------------
        # Build training issue texts
        # -------------------------------------------------

        training_issues = []

        for item in data:

            training_issue = str(
                item.get("issue", "")
            ).strip()

            if training_issue:
                training_issues.append(training_issue)

        if not training_issues:
            return 0.0

        # -------------------------------------------------
        # Transform incoming issue
        # -------------------------------------------------

        input_vector = vectorizer.transform(
            [issue]
        )

        # -------------------------------------------------
        # Transform known training issues
        # -------------------------------------------------

        training_vectors = vectorizer.transform(
            training_issues
        )

        # -------------------------------------------------
        # Calculate cosine similarity
        # -------------------------------------------------

        similarities = (
            training_vectors @ input_vector.T
        ).toarray().flatten()

        if len(similarities) == 0:
            return 0.0

        return float(max(similarities))

    except Exception as exc:

        print(
            f"WARNING: Could not calculate domain similarity: "
            f"{exc}"
        )

        return 0.0
# =========================================================
# OUT-OF-DOMAIN FALLBACK
# =========================================================

def out_of_domain_fallback(
    confidence_score: float = 0.0
) -> AssistResponse:
    """
    Handle requests that are outside the supported
    IT / enterprise-service domain.

    No troubleshooting steps are provided because
    the request is not an IT-supported issue.
    """

    return AssistResponse(
        possible_cause=(
            "This request is outside the scope of "
            "AI Assist, which supports IT and enterprise "
            "service issues."
        ),

        troubleshooting_steps=[],

        recommended_action=(
            "Please contact the appropriate support or "
            "facilities team for this issue."
        ),

        confidence="Low",
        confidence_score=confidence_score
    )        
# =========================================================
# MAIN AI ASSIST FUNCTION
# =========================================================

def generate_assistance(
    request: AssistRequest
) -> AssistResponse:
    """
    Generate troubleshooting guidance.

    Processing flow:

        User issue
             |
             v
        Local ML model
             |
             v
        Prediction + confidence
             |
             v
        Domain similarity
             |
       +-----+------+
       |            |
   Supported     Out-of-domain
       |            |
       v            v
   ML / fallback   Low confidence
       |            |
       +-----+------+
             |
             v
        Final response
    """

    # =====================================================
    # 1. NORMALIZE INPUT
    # =====================================================

    issue = (request.issue or "").strip()
    service = (request.service or "").strip()

    # Empty issue
    if not issue:
        return deterministic_fallback(
            issue,
            service
        )

    # =====================================================
    # 2. BUILD MODEL INPUT
    # =====================================================

    model_input = f"{issue} {service}".strip()

    # =====================================================
    # 3. LOAD LOCAL MODEL
    # =====================================================

    model = load_model()

    if model is None:

        print(
            "AI Assist: Using deterministic fallback "
            "because local model is unavailable."
        )

        return deterministic_fallback(
            issue,
            service
        )

    # =====================================================
    # 4. LOAD TRUSTED CATEGORIES
    # =====================================================

    trusted_categories = get_trusted_categories()

    if not trusted_categories:

        print(
            "AI Assist: No trusted training categories "
            "available. Using deterministic fallback."
        )

        return deterministic_fallback(
            issue,
            service
        )

    # =====================================================
    # 5. LOCAL ML PREDICTION
    # =====================================================

    try:

        predicted_category = model.predict(
            [model_input]
        )[0]

        predicted_category = str(
            predicted_category
        )

        print(
            f"AI Assist ML prediction: "
            f"{predicted_category}"
        )

        # =================================================
        # 6. CALCULATE CONFIDENCE
        # =================================================

        confidence_score = get_model_confidence(
            model,
            model_input
        )

        print(
            f"AI Assist ML confidence: "
            f"{confidence_score:.3f}"
        )

        # =================================================
        # 7. CALCULATE DOMAIN SIMILARITY
        # =================================================

        domain_similarity = get_domain_similarity(
            model,
            issue
        )

        print(
            f"AI Assist domain similarity: "
            f"{domain_similarity:.3f}"
        )

        # =================================================
        # 8. CONFIDENCE / DOMAIN CHECK
        # =================================================

        if (
            confidence_score < MODEL_CONFIDENCE_THRESHOLD
            or domain_similarity < DOMAIN_SIMILARITY_THRESHOLD
        ):

            print(
                "AI Assist: ML prediction rejected because "
                "confidence or domain similarity is too low."
            )

            # -------------------------------------------------
            # Explicitly out-of-domain request
            # -------------------------------------------------

            if (
                service.lower() == "other"
                and domain_similarity < DOMAIN_SIMILARITY_THRESHOLD
            ):

                print(
                    "AI Assist: Request appears to be "
                    "outside the supported IT domain."
                )

                return out_of_domain_fallback(
                    confidence_score
                )

            # -------------------------------------------------
            # Unknown but potentially IT-related request
            # -------------------------------------------------

            return deterministic_fallback(
                issue,
                service,
                confidence_score
            )

        # =================================================
        # 9. TRUSTED CATEGORY CHECK
        # =================================================

        if predicted_category not in trusted_categories:

            print(
                f"AI Assist: Predicted category "
                f"'{predicted_category}' is not trusted. "
                f"Using deterministic fallback."
            )

            return deterministic_fallback(
                issue,
                service,
                confidence_score
            )

        # =================================================
        # 10. GET KNOWLEDGE FOR CATEGORY
        # =================================================

        response = get_category_response(
            predicted_category
        )

        if response is None:

            print(
                f"AI Assist: No troubleshooting knowledge "
                f"found for category '{predicted_category}'. "
                f"Using deterministic fallback."
            )

            return deterministic_fallback(
                issue,
                service,
                confidence_score
            )

        # =================================================
        # 11. HIGH-CONFIDENCE ML RESPONSE
        # =================================================

        print(
            "AI Assist: Returning high-confidence "
            "local ML response."
        )

        return AssistResponse(
            possible_cause=response[
                "possible_cause"
            ],

            troubleshooting_steps=response[
                "troubleshooting_steps"
            ],

            recommended_action=response[
                "recommended_action"
            ],

            confidence="High",

            confidence_score=confidence_score
        )

    # =====================================================
    # 12. SAFE FALLBACK ON ANY ML ERROR
    # =====================================================

    except Exception as exc:

        print(
            f"WARNING: Local ML prediction failed: "
            f"{exc}"
        )

        return deterministic_fallback(
            issue,
            service
        )