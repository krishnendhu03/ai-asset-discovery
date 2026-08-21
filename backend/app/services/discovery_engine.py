from pathlib import Path
import re

from app.models.asset import AIAsset, Evidence


# =========================================================
# AI / ML LIBRARIES
# =========================================================

AI_LIBRARY_PATTERNS = {
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "transformers": "Hugging Face Transformers",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "sklearn": "Scikit-learn",
    "langchain": "LangChain",
}


# =========================================================
# MODEL / AI RUNTIME PATTERNS
# =========================================================

MODEL_USAGE_PATTERNS = [
    (
        r"\bjoblib\.load\s*\(",
        "Trained model loaded using joblib",
    ),
    (
        r"\bpredict\s*\(",
        "Model prediction invocation detected",
    ),
    (
        r"\bpredict_proba\s*\(",
        "Model probability prediction invocation detected",
    ),
    (
        r"\bfit\s*\(",
        "Machine-learning model training invocation detected",
    ),
    (
        r"\btransform\s*\(",
        "Machine-learning transformation invocation detected",
    ),
    (
        r"\bchat\.completions\.create\s*\(",
        "OpenAI chat completion invocation detected",
    ),
    (
        r"\bembeddings\.create\s*\(",
        "OpenAI embeddings invocation detected",
    ),
    (
        r"\bresponses\.create\s*\(",
        "OpenAI responses API invocation detected",
    ),
    (
        r"\bmessages\.create\s*\(",
        "AI model messages API invocation detected",
    ),
]


# =========================================================
# MODEL ARTIFACT EXTENSIONS
# =========================================================

MODEL_ARTIFACT_EXTENSIONS = {
    ".joblib",
    ".pkl",
    ".pickle",
    ".pt",
    ".pth",
    ".h5",
    ".keras",
    ".onnx",
}


# =========================================================
# SOURCE FILE EXTENSIONS
# =========================================================

SOURCE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
}


# =========================================================
# DIRECTORIES TO IGNORE
# =========================================================

IGNORED_DIRECTORIES = {
    "node_modules",
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
}


# =========================================================
# READ TEXT FILE
# =========================================================

def read_text_file(file_path: Path) -> str:
    try:
        return file_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )
    except Exception:
        return ""


# =========================================================
# REMOVE COMMENTS
# =========================================================

def remove_comments(content: str) -> str:
    """
    Remove common Python comments so commented-out
    AI imports are not treated as real usage.
    """

    lines = []

    for line in content.splitlines():

        stripped = line.strip()

        if stripped.startswith("#"):
            continue

        if "#" in line:
            line = line.split("#", 1)[0]

        lines.append(line)

    return "\n".join(lines)


# =========================================================
# DETECT MODEL NAME
# =========================================================

def detect_model(content: str, file_path: Path) -> str:

    # OpenAI model passed directly to an API call
    openai_model = re.search(
        r'\bmodel\s*=\s*["\']([^"\']+)["\']',
        content,
        re.IGNORECASE,
    )

    if openai_model:
        return openai_model.group(1)

    # Model loaded from a file
    joblib_match = re.search(
        r'joblib\.load\s*\(\s*["\']([^"\']+)["\']',
        content,
        re.IGNORECASE,
    )

    if joblib_match:
        return Path(joblib_match.group(1)).stem

    # If this is itself a model artifact
    if file_path.suffix.lower() in MODEL_ARTIFACT_EXTENSIONS:
        return file_path.stem

    return "Not detected"


# =========================================================
# DETECT PROVIDER
# =========================================================

def detect_provider(content: str) -> str:

    providers = []

    for library, display_name in AI_LIBRARY_PATTERNS.items():

        pattern = (
            rf"\b("
            rf"import\s+{re.escape(library)}"
            rf"|from\s+{re.escape(library)}\s+import"
            rf")\b"
        )

        if re.search(
            pattern,
            content,
            re.IGNORECASE,
        ):
            providers.append(display_name)

    if providers:
        return ", ".join(dict.fromkeys(providers))

    return "Not detected"


# =========================================================
# DETECT LOCATION
# =========================================================

def detect_location(content: str) -> str:

    aws_patterns = [
        r"\bboto3\b",
        r"\baws\b",
        r"\bbedrock\b",
        r"\bs3\b",
        r"\baws_access_key\b",
        r"\baws_secret_access_key\b",
        r"\bamazon\b",
    ]

    for pattern in aws_patterns:

        if re.search(
            pattern,
            content,
            re.IGNORECASE,
        ):
            return "AWS"

    azure_patterns = [
        r"\bazure\b",
        r"\bazure_openai\b",
        r"\bazure-ai\b",
    ]

    for pattern in azure_patterns:

        if re.search(
            pattern,
            content,
            re.IGNORECASE,
        ):
            return "Azure"

    gcp_patterns = [
        r"\bgcp\b",
        r"\bgoogle cloud\b",
        r"\bvertexai\b",
    ]

    for pattern in gcp_patterns:

        if re.search(
            pattern,
            content,
            re.IGNORECASE,
        ):
            return "Google Cloud"

    return "Not detected"


# =========================================================
# DETECT PURPOSE
# =========================================================

def detect_purpose(
    content: str,
    evidence: list[Evidence],
) -> str:

    content_lower = content.lower()

    if (
        "embedding" in content_lower
        or "embeddings" in content_lower
    ):
        if (
            "search" in content_lower
            or "document" in content_lower
        ):
            return "Generate embeddings for document search"

        return "Generate embeddings"

    if (
        "chat.completions.create" in content_lower
        or "responses.create" in content_lower
    ):
        return "Generate AI responses"

    if "predict_proba" in content_lower:
        return "Generate model probability predictions"

    if "predict(" in content_lower:
        return "Generate model predictions"

    if "fit(" in content_lower:
        return "Train a machine-learning model"

    if "transform(" in content_lower:
        return "Transform data using a machine-learning model"

    if any(
        item.type == "model_artifact"
        for item in evidence
    ):
        return "Provide a trained machine-learning model"

    return "Not detected"


# =========================================================
# DETECT APPLICATION NAME
# =========================================================

def detect_application(file_path: Path) -> str:

    name = file_path.stem

    # Convert snake_case / kebab-case into readable text
    readable = re.sub(
        r"[_\-]+",
        " ",
        name,
    ).strip()

    if not readable:
        return "Not detected"

    return readable.title()


# =========================================================
# SCAN SOURCE FILE
# =========================================================

def scan_file(file_path: Path):

    evidence = []

    content = read_text_file(file_path)

    content = remove_comments(content)

    if not content:
        return evidence

    # -----------------------------------------------------
    # Detect AI / ML library imports
    # -----------------------------------------------------

    for library, display_name in AI_LIBRARY_PATTERNS.items():

        import_pattern = (
            rf"\b("
            rf"import\s+{re.escape(library)}"
            rf"|from\s+{re.escape(library)}\s+import"
            rf")\b"
        )

        if re.search(
            import_pattern,
            content,
            re.IGNORECASE,
        ):

            evidence.append(
                Evidence(
                    type="library_usage",
                    value=f"{display_name} imported or referenced",
                    file=str(file_path),
                )
            )

    # -----------------------------------------------------
    # Detect model loading / ML execution
    # -----------------------------------------------------

    for pattern, description in MODEL_USAGE_PATTERNS:

        if re.search(
            pattern,
            content,
            re.IGNORECASE,
        ):

            evidence.append(
                Evidence(
                    type="model_usage",
                    value=description,
                    file=str(file_path),
                )
            )

    return evidence


# =========================================================
# SCAN MODEL ARTIFACT
# =========================================================

def scan_model_artifact(file_path: Path):

    if (
        file_path.suffix.lower()
        not in MODEL_ARTIFACT_EXTENSIONS
    ):
        return []

    return [
        Evidence(
            type="model_artifact",
            value=(
                f"Trained model artifact detected: "
                f"{file_path.name}"
            ),
            file=str(file_path),
        )
    ]


# =========================================================
# DETERMINE CONFIDENCE
# =========================================================

def determine_confidence(evidence):

    evidence_types = {
        item.type
        for item in evidence
    }

    evidence_values = [
        item.value.lower()
        for item in evidence
    ]

    # -----------------------------------------------------
    # Strong model execution
    # -----------------------------------------------------

    has_model_load = any(
        "model loaded" in value
        or "model loaded using joblib" in value
        for value in evidence_values
    )

    has_prediction = any(
        "prediction invocation" in value
        or "probability prediction invocation" in value
        for value in evidence_values
    )

    if has_model_load and has_prediction:
        return "High"

    # -----------------------------------------------------
    # AI library + model execution
    # -----------------------------------------------------

    if (
        "library_usage" in evidence_types
        and "model_usage" in evidence_types
    ):
        return "High"

    # -----------------------------------------------------
    # Model execution only
    # -----------------------------------------------------

    if "model_usage" in evidence_types:

        if any(
            "training invocation" in value
            for value in evidence_values
        ):
            return "Medium"

        return "Medium"

    # -----------------------------------------------------
    # Model artifact only
    # -----------------------------------------------------

    if "model_artifact" in evidence_types:
        return "Medium"

    # -----------------------------------------------------
    # Library only
    # -----------------------------------------------------

    if "library_usage" in evidence_types:
        return "Low"

    return "Low"


# =========================================================
# DETERMINE ASSET TYPE
# =========================================================

def determine_asset_type(
    evidence,
    confidence,
):

    evidence_types = {
        item.type
        for item in evidence
    }

    evidence_values = [
        item.value.lower()
        for item in evidence
    ]

    has_library = "library_usage" in evidence_types
    has_execution = "model_usage" in evidence_types
    has_artifact = "model_artifact" in evidence_types

    # -----------------------------------------------------
    # REAL AI EXECUTION
    # -----------------------------------------------------
    # An actual AI/model API invocation is stronger
    # evidence than simply importing an AI library.

    has_ai_api_call = any(
        "openai" in value
        or "ai model" in value
        or "chat completion" in value
        or "responses api" in value
        or "messages api" in value
        for value in evidence_values
    )

    if has_execution and has_ai_api_call:
        return "AI Application"

    # -----------------------------------------------------
    # ML MODEL EXECUTION
    # -----------------------------------------------------

    if has_execution:
        return "AI Application"

    # -----------------------------------------------------
    # TRAINED MODEL ARTIFACT
    # -----------------------------------------------------

    if has_artifact:
        return "AI Model Artifact"

    # -----------------------------------------------------
    # LIBRARY ONLY
    # -----------------------------------------------------
    # Example:
    #
    # import openai
    #
    # but no API invocation.
    #
    # This is intentionally NOT classified as an
    # AI Application.

    if has_library:
        return "Potential AI Reference"

    return "AI Asset"

# =========================================================
# DETERMINE STATUS
# =========================================================

def determine_status(
    confidence,
    asset_type,
):

    if asset_type == "Potential AI Reference":
        return "Needs Review"

    if confidence == "High":
        return "Discovered / Pending Review"

    if confidence == "Medium":
        return "Discovered / Pending Review"

    return "Needs Review"


# =========================================================
# DISCOVER AI ASSETS
# =========================================================

def discover_ai_assets(
    repository_path: str,
) -> list[AIAsset]:

    root = Path(repository_path)

    if not root.exists():
        raise ValueError(
            "Repository path does not exist."
        )

    if not root.is_dir():
        raise ValueError(
            "Repository path must be a directory."
        )

    assets = []

    # -----------------------------------------------------
    # Walk repository
    # -----------------------------------------------------

    for file_path in root.rglob("*"):

        if not file_path.is_file():
            continue

        # Ignore unwanted directories
        if any(
            ignored in file_path.parts
            for ignored in IGNORED_DIRECTORIES
        ):
            continue

        evidence = []

        # -------------------------------------------------
        # Source-code scanning
        # -------------------------------------------------

        if (
            file_path.suffix.lower()
            in SOURCE_EXTENSIONS
        ):

            evidence.extend(
                scan_file(file_path)
            )

        # -------------------------------------------------
        # Model artifact scanning
        # -------------------------------------------------

        elif (
            file_path.suffix.lower()
            in MODEL_ARTIFACT_EXTENSIONS
        ):

            evidence.extend(
                scan_model_artifact(file_path)
            )

        # -------------------------------------------------
        # No evidence = not an AI asset
        # -------------------------------------------------

        if not evidence:
            continue

        # -------------------------------------------------
        # Determine confidence
        # -------------------------------------------------

        confidence = determine_confidence(
            evidence
        )

        # -------------------------------------------------
        # Determine enterprise fields
        # -------------------------------------------------

        content = read_text_file(file_path)

        content = remove_comments(content)

        model = detect_model(
            content,
            file_path,
        )

        provider = detect_provider(
            content,
        )

        location = detect_location(
            content,
        )

        purpose = detect_purpose(
            content,
            evidence,
        )

        application = detect_application(
            file_path,
        )

        asset_type = determine_asset_type(
            evidence,
            confidence,
        )

        status = determine_status(
            confidence,
            asset_type,
        )

        # -------------------------------------------------
        # Create asset
        # -------------------------------------------------

        asset = AIAsset(

            id=f"AI-{len(assets) + 1:04d}",

            name=file_path.stem,

            asset_type=asset_type,

            model=model,

            provider=provider,

            location=location,

            application=application,

            purpose=purpose,

            discovery_source="Local Repository",

            status=status,

            category="AI/ML",

            confidence=confidence,

            evidence=evidence,

            description=(
                "AI asset discovered from repository "
                "source-code usage and/or trained "
                "model artifacts."
            ),
        )

        assets.append(asset)

    return assets