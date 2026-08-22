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
# AI / MODEL API PATTERNS
# =========================================================

STRONG_MODEL_USAGE_PATTERNS = [
    (
        r"\bjoblib\.load\s*\(",
        "Trained model loaded using joblib",
    ),
    (
        r"\b(?:pickle|pkl)\.load\s*\(",
        "Serialized model loaded using pickle",
    ),
    (
        r"\bopenai\.[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*\s*\(",
        "OpenAI API invocation detected",
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
    (
        r"\bAnthropic\b.*\bmessages\.create\s*\(",
        "Anthropic messages API invocation detected",
    ),
]


# =========================================================
# ML MODEL EXECUTION PATTERNS
# =========================================================

ML_EXECUTION_PATTERNS = [
    (
        r"\b[A-Za-z_][A-Za-z0-9_]*\.(?:predict|predict_proba)\s*\(",
        "Machine-learning model prediction invocation detected",
    ),
    (
        r"\b[A-Za-z_][A-Za-z0-9_]*\.(?:fit|fit_transform)\s*\(",
        "Machine-learning model training invocation detected",
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
    ".env",
    "dist",
    "build",
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
    Remove common single-line comments.

    This prevents commented-out AI imports/API calls from
    becoming evidence.

    Note:
    This is intentionally lightweight rather than a full
    language parser because the scanner also handles JS/TS.
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
# NORMALIZE SOURCE
# =========================================================

def normalize_content(content: str) -> str:
    """
    Normalize source code for more reliable regex matching.
    """

    content = content.replace("\r\n", "\n")
    content = content.replace("\r", "\n")

    return content


# =========================================================
# DETECT MODEL NAME
# =========================================================

def detect_model(
    content: str,
    file_path: Path,
) -> str:

    model_patterns = [
        r'\bmodel\s*=\s*["\']([^"\']+)["\']',
        r'\bmodel\s*:\s*["\']([^"\']+)["\']',
    ]

    for pattern in model_patterns:

        match = re.search(
            pattern,
            content,
            re.IGNORECASE,
        )

        if match:

            model_name = match.group(1).strip()

            generic_values = {
                "customer",
                "user",
                "product",
                "default",
                "test",
                "development",
                "production",
                "model",
            }

            if model_name.lower() not in generic_values:
                return model_name

    # -----------------------------------------------------
    # Joblib model
    # -----------------------------------------------------

    joblib_match = re.search(
        r'joblib\.load\s*\(\s*["\']([^"\']+)["\']',
        content,
        re.IGNORECASE,
    )

    if joblib_match:
        return Path(
            joblib_match.group(1)
        ).stem

    # -----------------------------------------------------
    # Pickle model
    # -----------------------------------------------------

    pickle_match = re.search(
        r'(?:pickle|pkl)\.load\s*\(',
        content,
        re.IGNORECASE,
    )

    if pickle_match:

        artifact_match = re.search(
            r'["\']([^"\']+\.(?:pkl|pickle))["\']',
            content,
            re.IGNORECASE,
        )

        if artifact_match:
            return Path(
                artifact_match.group(1)
            ).stem

    # -----------------------------------------------------
    # Model artifact itself
    # -----------------------------------------------------

    if (
        file_path.suffix.lower()
        in MODEL_ARTIFACT_EXTENSIONS
    ):
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

    # -----------------------------------------------------
    # Azure OpenAI
    # -----------------------------------------------------

    if re.search(
        r"\bazure\.identity\b"
        r"|\bazure_openai\b"
        r"|\bAzureOpenAI\b",
        content,
        re.IGNORECASE,
    ):
        providers.append("Azure OpenAI")

    # -----------------------------------------------------
    # Google / Vertex AI
    # -----------------------------------------------------

    if re.search(
        r"\bvertexai\b"
        r"|\bgoogle\.cloud\b"
        r"|\bGenerativeModel\b",
        content,
        re.IGNORECASE,
    ):
        providers.append("Google Vertex AI")

    if providers:
        return ", ".join(
            dict.fromkeys(providers)
        )

    return "Not detected"


# =========================================================
# DETECT LOCATION
# =========================================================

def detect_location(content: str) -> str:

    # -----------------------------------------------------
    # AWS
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Azure
    # -----------------------------------------------------

    azure_patterns = [
        r"\bazure\b",
        r"\bazure_openai\b",
        r"\bazure-ai\b",
        r"\bAzureOpenAI\b",
    ]

    for pattern in azure_patterns:

        if re.search(
            pattern,
            content,
            re.IGNORECASE,
        ):
            return "Azure"

    # -----------------------------------------------------
    # Google Cloud
    # -----------------------------------------------------

    gcp_patterns = [
        r"\bgcp\b",
        r"\bgoogle cloud\b",
        r"\bgoogle\.cloud\b",
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

    # -----------------------------------------------------
    # Embeddings
    # -----------------------------------------------------

    if (
        "embedding" in content_lower
        or "embeddings" in content_lower
    ):

        if (
            "search" in content_lower
            or "document" in content_lower
            or "retrieval" in content_lower
        ):
            return "Generate embeddings for document search"

        return "Generate embeddings"

    # -----------------------------------------------------
    # Chat / response generation
    # -----------------------------------------------------

    if (
        "chat.completions.create" in content_lower
        or "responses.create" in content_lower
        or "messages.create" in content_lower
    ):
        return "Generate AI responses"

    # -----------------------------------------------------
    # Probability prediction
    # -----------------------------------------------------

    if "predict_proba" in content_lower:
        return "Generate model probability predictions"

    # -----------------------------------------------------
    # Model prediction
    # -----------------------------------------------------

    if re.search(
        r"\.[Pp]redict\s*\(",
        content,
    ):
        return "Generate model predictions"

    # -----------------------------------------------------
    # Model training
    # -----------------------------------------------------

    if re.search(
        r"\.(?:fit|fit_transform)\s*\(",
        content,
    ):
        return "Train a machine-learning model"

    # -----------------------------------------------------
    # Model artifact
    # -----------------------------------------------------

    if any(
        item.type == "model_artifact"
        for item in evidence
    ):
        return "Provide a trained machine-learning model"

    return "Not detected"


# =========================================================
# DETECT APPLICATION NAME
# =========================================================

def detect_application(
    file_path: Path,
) -> str:

    name = file_path.stem

    readable = re.sub(
        r"[_\-]+",
        " ",
        name,
    ).strip()

    if not readable:
        return "Not detected"

    return readable.title()


# =========================================================
# FIND MATCH LINE
# =========================================================

def find_match_line(
    content: str,
    pattern: str,
) -> int:

    match = re.search(
        pattern,
        content,
        re.IGNORECASE,
    )

    if not match:
        return 0

    return content[:match.start()].count("\n") + 1


# =========================================================
# ADD EVIDENCE
# =========================================================

def add_evidence(
    evidence: list[Evidence],
    evidence_type: str,
    value: str,
    file_path: Path,
    line_number: int | None = None,
):
    evidence.append(
        Evidence(
            type=evidence_type,
            value=value,
            file=str(file_path),
            line_number=line_number,
        )
    )


# =========================================================
# SCAN SOURCE FILE
# =========================================================

def scan_file(
    file_path: Path,
):

    evidence = []

    content = read_text_file(
        file_path
    )

    content = normalize_content(
        content
    )

    content = remove_comments(
        content
    )

    if not content.strip():
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

            add_evidence(
                evidence,
                "library_usage",
                (
                    f"{display_name} imported or "
                    f"referenced"
                ),
                file_path,
                find_match_line(
                    content,
                    import_pattern,
                ),
            )

    # -----------------------------------------------------
    # Strong AI / model API usage
    # -----------------------------------------------------

    for pattern, description in STRONG_MODEL_USAGE_PATTERNS:

        if re.search(
            pattern,
            content,
            re.IGNORECASE,
        ):

            add_evidence(
                evidence,
                "model_usage",
                description,
                file_path,
                find_match_line(
                    content,
                    pattern,
                ),
            )

    # -----------------------------------------------------
    # ML execution
    # -----------------------------------------------------

    for pattern, description in ML_EXECUTION_PATTERNS:

        if re.search(
            pattern,
            content,
            re.IGNORECASE,
        ):

            add_evidence(
                evidence,
                "model_usage",
                description,
                file_path,
                find_match_line(
                    content,
                    pattern,
                ),
            )

    # -----------------------------------------------------
    # Library detected without recognized AI execution
    # -----------------------------------------------------

    has_library_usage = any(
        item.type == "library_usage"
        for item in evidence
    )

    has_model_usage = any(
        item.type == "model_usage"
        for item in evidence
    )

    if has_library_usage and not has_model_usage:

        library_evidence = next(
            (
                item
                for item in evidence
                if item.type == "library_usage"
            ),
            None,
        )

        add_evidence(
            evidence,
            "usage_analysis",
            (
                "AI/ML library detected, but no recognized "
                "AI API or model execution was found in "
                "this file."
            ),
            file_path,
            (
                library_evidence.line_number
                if library_evidence
                else None
            ),
        )

    return evidence


# =========================================================
# SCAN MODEL ARTIFACT
# =========================================================

def scan_model_artifact(
    file_path: Path,
):

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
            line_number=None,
        )
    ]


# =========================================================
# DETERMINE CONFIDENCE
# =========================================================

def determine_confidence(
    evidence,
):

    evidence_types = {
        item.type
        for item in evidence
    }

    evidence_values = [
        item.value.lower()
        for item in evidence
    ]

    # -----------------------------------------------------
    # Strong API / model execution
    # -----------------------------------------------------

    has_strong_api = any(
        (
            "api invocation" in value
            or "chat completion" in value
            or "embeddings invocation" in value
            or "responses api" in value
            or "messages api" in value
        )
        for value in evidence_values
    )

    # -----------------------------------------------------
    # Model loading + prediction
    # -----------------------------------------------------

    has_model_load = any(
        (
            "model loaded" in value
            or "serialized model loaded" in value
        )
        for value in evidence_values
    )

    has_prediction = any(
        (
            "prediction invocation" in value
            or "probability prediction" in value
        )
        for value in evidence_values
    )

    if (
        has_strong_api
        or (
            has_model_load
            and has_prediction
        )
    ):
        return "High"

    # -----------------------------------------------------
    # Library + genuine ML execution
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
        return "Medium"

    # -----------------------------------------------------
    # Model artifact
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

    has_library = (
        "library_usage"
        in evidence_types
    )

    has_execution = (
        "model_usage"
        in evidence_types
    )

    has_artifact = (
        "model_artifact"
        in evidence_types
    )

    # -----------------------------------------------------
    # Strong AI API execution
    # -----------------------------------------------------

    has_ai_api_call = any(
        (
            "openai api invocation" in value
            or "chat completion" in value
            or "embeddings invocation" in value
            or "responses api" in value
            or "messages api" in value
            or "anthropic messages api" in value
        )
        for value in evidence_values
    )

    if has_ai_api_call:
        return "AI Application"

    # -----------------------------------------------------
    # Genuine model execution
    # -----------------------------------------------------

    if has_execution:
        return "AI Application"

    # -----------------------------------------------------
    # Model artifact
    # -----------------------------------------------------

    if has_artifact:
        return "AI Model Artifact"

    # -----------------------------------------------------
    # Library only
    # -----------------------------------------------------

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

    if confidence in {
        "High",
        "Medium",
    }:
        return "Discovered / Pending Review"

    return "Needs Review"


# =========================================================
# DISCOVER AI ASSETS
# =========================================================

def discover_ai_assets(
    repository_path: str,
) -> list[AIAsset]:

    root = Path(
        repository_path
    )

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

        # -------------------------------------------------
        # Ignore unwanted directories
        # -------------------------------------------------

        if any(
            ignored in file_path.parts
            for ignored in IGNORED_DIRECTORIES
        ):
            continue

        evidence = []

        # -------------------------------------------------
        # Source code
        # -------------------------------------------------

        if (
            file_path.suffix.lower()
            in SOURCE_EXTENSIONS
        ):

            evidence.extend(
                scan_file(
                    file_path
                )
            )

        # -------------------------------------------------
        # Model artifact
        # -------------------------------------------------

        elif (
            file_path.suffix.lower()
            in MODEL_ARTIFACT_EXTENSIONS
        ):

            evidence.extend(
                scan_model_artifact(
                    file_path
                )
            )

        # -------------------------------------------------
        # No evidence
        # -------------------------------------------------

        if not evidence:
            continue

        # -------------------------------------------------
        # Confidence
        # -------------------------------------------------

        confidence = determine_confidence(
            evidence
        )

        # -------------------------------------------------
        # Read content for metadata detection
        # -------------------------------------------------

        content = read_text_file(
            file_path
        )

        content = normalize_content(
            content
        )

        content = remove_comments(
            content
        )

        # -------------------------------------------------
        # Enterprise fields
        # -------------------------------------------------

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
        # Create AI asset
        # -------------------------------------------------

        asset = AIAsset(

            id=(
                f"AI-{len(assets) + 1:04d}"
            ),

            name=file_path.stem,

            asset_type=asset_type,

            model=model,

            provider=provider,

            location=location,

            application=application,

            purpose=purpose,

            discovery_source=(
                "Local Repository"
            ),

            status=status,

            category="AI/ML",

            confidence=confidence,

            evidence=evidence,

            description=(
                "AI asset discovered from "
                "repository source-code usage "
                "and/or trained model artifacts."
            ),
        )

        assets.append(asset)

    return assets