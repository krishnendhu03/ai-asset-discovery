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
# LLM MODEL PATTERNS
# =========================================================

LLM_MODEL_PATTERNS = [
    (
        r"\bgpt[-_ ]?(?:4\.1|4o|4(?:\.[0-9]+)?|3\.5)\b",
        "GPT model detected",
    ),
    (
        r"\bclaude(?:[-_ ]?(?:2|3|3\.5|3\.7|4))?\b",
        "Claude model detected",
    ),
    (
        r"\bgemini(?:[-_ ]?(?:pro|flash|1\.5|2\.0|2\.5))?\b",
        "Gemini model detected",
    ),
    (
        r"\bllama(?:[-_ ]?(?:2|3|3\.1|3\.2|3\.3|4))?\b",
        "Llama model detected",
    ),
    (
        r"\bmistral(?:[-_ ]?(?:7b|8x7b|large|medium))?\b",
        "Mistral model detected",
    ),
]


# =========================================================
# LLM EXECUTION PATTERNS
# =========================================================

LLM_EXECUTION_PATTERNS = [
    (
        r"\bchat\.completions\.create\s*\(",
        "LLM chat completion invocation detected",
    ),
    (
        r"\bresponses\.create\s*\(",
        "LLM responses API invocation detected",
    ),
    (
        r"\bmessages\.create\s*\(",
        "LLM messages API invocation detected",
    ),
    (
        r"\b(?:invoke|ainvoke)\s*\(",
        "LLM invocation detected",
    ),
    (
        r"\b(?:generate|agenerate)\s*\(",
        "LLM generation invocation detected",
    ),
]


# =========================================================
# AI AGENT SIGNALS
# =========================================================

AI_AGENT_PATTERNS = [
    (
        r"\b(?:AI)?_?agent\b",
        "AI agent reference detected",
    ),
    (
        r"\bagents?\s*=",
        "AI agent configuration detected",
    ),
    (
        r"\btool_calls?\b",
        "AI agent tool-call pattern detected",
    ),
    (
        r"\bfunction_calls?\b",
        "AI function-call pattern detected",
    ),
    (
        r"\btools\s*=",
        "AI agent tools configuration detected",
    ),
    (
        r"\bfunctions\s*=",
        "AI function configuration detected",
    ),
    (
        r"\bAgent\s*\(",
        "AI Agent object detected",
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
# AI / ML CONFIGURATION & DEPENDENCY FILES
# =========================================================

CONFIGURATION_EXTENSIONS = {
    ".toml",
    ".yaml",
    ".yml",
    ".json",
    ".lock",
}

DEPENDENCY_FILES = {
    "requirements.txt",
    "pyproject.toml",
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "environment.yml",
    "environment.yaml",
    "dockerfile",
    "docker-compose.yml",
    ".env.example",
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

    This is intentionally lightweight because the scanner
    also handles JavaScript/TypeScript.
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

    content = content.replace(
        "\r\n",
        "\n",
    )

    content = content.replace(
        "\r",
        "\n",
    )

    return content


# =========================================================
# DETECT MODEL NAME
# =========================================================

def detect_model(
    content: str,
    file_path: Path,
) -> str:

    # -----------------------------------------------------
    # Known LLM models
    # -----------------------------------------------------

    llm_patterns = [
        (
            r"\bgpt[-_ ]?(?:4\.1|4o|4(?:\.[0-9]+)?|3\.5)\b",
            "GPT-4.x",
        ),
        (
            r"\bclaude(?:[-_ ]?(?:2|3|3\.5|3\.7|4))?\b",
            "Claude",
        ),
        (
            r"\bgemini(?:[-_ ]?(?:pro|flash|1\.5|2\.0|2\.5))?\b",
            "Gemini",
        ),
        (
            r"\bllama(?:[-_ ]?(?:2|3|3\.1|3\.2|3\.3|4))?\b",
            "Llama",
        ),
        (
            r"\bmistral(?:[-_ ]?(?:7b|8x7b|large|medium))?\b",
            "Mistral",
        ),
    ]

    for pattern, display_name in llm_patterns:

        if re.search(
            pattern,
            content,
            re.IGNORECASE,
        ):

            return display_name

    # -----------------------------------------------------
    # Explicit model assignment
    # -----------------------------------------------------

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
                "raw",
            }

            if (
                model_name.lower()
                not in generic_values and len(model_name) >= 3
            ):

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

    # -----------------------------------------------------
    # OpenAI
    # -----------------------------------------------------

    if re.search(
        r"\bopenai\b"
        r"|\bfrom\s+openai\s+import\b"
        r"|\bOpenAI\s*\(",
        content,
        re.IGNORECASE,
    ):
        providers.append("OpenAI")

    # -----------------------------------------------------
    # Azure OpenAI
    # -----------------------------------------------------

    if re.search(
        r"\bazure\.identity\b"
        r"|\bazure[-_]openai\b"
        r"|\bAzureOpenAI\b"
        r"|\bazure_endpoint\b",
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
        r"|\bGenerativeModel\b"
        r"|\bgoogle-generativeai\b",
        content,
        re.IGNORECASE,
    ):
        providers.append("Google Vertex AI")

    # -----------------------------------------------------
    # Standard AI libraries
    # -----------------------------------------------------

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
            providers.append(
                display_name
            )

    if providers:

        return ", ".join(
            dict.fromkeys(providers)
        )

    return "Not detected"


# =========================================================
# DETECT LOCATION
# =========================================================

def detect_location(content: str) -> str:

    locations = []

    # -----------------------------------------------------
    # OpenAI / Anthropic cloud
    # -----------------------------------------------------

    if re.search(
        r"\bopenai\b"
        r"|\bchat\.completions\b"
        r"|\bresponses\.create\b"
        r"|\bembeddings\.create\b"
        r"|\banthropic\b"
        r"|\bmessages\.create\b",
        content,
        re.IGNORECASE,
    ):
        locations.append("Cloud")

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
            locations.append("AWS")
            break

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
            locations.append("Azure")
            break

    # -----------------------------------------------------
    # Google Cloud
    # -----------------------------------------------------

    gcp_patterns = [
        r"\bgcp\b",
        r"\bgoogle cloud\b",
        r"\bgoogle\.cloud\b",
        r"\bvertexai\b",
        r"\bGenerativeModel\b",
    ]

    for pattern in gcp_patterns:

        if re.search(
            pattern,
            content,
            re.IGNORECASE,
        ):
            locations.append("Google Cloud")
            break

    # -----------------------------------------------------
    # Remove duplicates
    # -----------------------------------------------------

    locations = list(
        dict.fromkeys(locations)
    )

    if locations:
        return " / ".join(locations)

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
    # Customer support
    # -----------------------------------------------------

    if (
        "customer support" in content_lower
        or "customer-support" in content_lower
    ):

        if (
            "summar" in content_lower
            or "response" in content_lower
        ):

            return (
                "Generate and summarize "
                "customer-support responses"
            )

        return "Provide customer-support assistance"

    # -----------------------------------------------------
    # Incident intelligence
    # -----------------------------------------------------

    if (
        "incident" in content_lower
        and (
            "classif" in content_lower
            or "severity" in content_lower
        )
    ):

        return "Investigate and classify incidents"

    # -----------------------------------------------------
    # Enterprise knowledge
    # -----------------------------------------------------

    if (
        "enterprise" in content_lower
        and (
            "knowledge" in content_lower
            or "search" in content_lower
        )
    ):

        return "Search and analyze enterprise knowledge"

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

            return (
                "Generate embeddings for document search"
            )

        return "Generate embeddings"

    # -----------------------------------------------------
    # Chat / response generation
    # -----------------------------------------------------

    if (
        "chat.completions.create" in content_lower
        or "responses.create" in content_lower
        or "messages.create" in content_lower
        or "llm invocation detected" in content_lower
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

        return (
            "Provide a trained "
            "machine-learning model"
        )

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

    return (
        content[:match.start()].count("\n")
        + 1
    )


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

    # =====================================================
    # AI / ML LIBRARY IMPORTS
    # =====================================================

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

    # =====================================================
    # STRONG AI / MODEL API USAGE
    # =====================================================

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

    # =====================================================
    # LLM MODEL DETECTION
    # =====================================================

    for pattern, description in LLM_MODEL_PATTERNS:

        if re.search(
            pattern,
            content,
            re.IGNORECASE,
        ):

            add_evidence(
                evidence,
                "llm_detection",
                description,
                file_path,
                find_match_line(
                    content,
                    pattern,
                ),
            )

    # =====================================================
    # LLM EXECUTION
    # =====================================================

    for pattern, description in LLM_EXECUTION_PATTERNS:

        if re.search(
            pattern,
            content,
            re.IGNORECASE,
        ):

            add_evidence(
                evidence,
                "llm_usage",
                description,
                file_path,
                find_match_line(
                    content,
                    pattern,
                ),
            )

    # =====================================================
    # AI AGENT SIGNALS
    # =====================================================

    for pattern, description in AI_AGENT_PATTERNS:

        if re.search(
            pattern,
            content,
            re.IGNORECASE,
        ):

            add_evidence(
                evidence,
                "agent_signal",
                description,
                file_path,
                find_match_line(
                    content,
                    pattern,
                ),
            )

    # =====================================================
    # ML EXECUTION
    # =====================================================

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

    # =====================================================
    # LIBRARY WITHOUT RECOGNIZED EXECUTION
    # =====================================================

    has_library_usage = any(
        item.type == "library_usage"
        for item in evidence
    )

    has_model_usage = any(
        item.type == "model_usage"
        for item in evidence
    )

    has_llm_usage = any(
        item.type == "llm_usage"
        for item in evidence
    )

    if (
        has_library_usage
        and not has_model_usage
        and not has_llm_usage
    ):

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
                "AI/ML library detected, but no "
                "recognized AI API or model execution "
                "was found in this file."
            ),
            file_path,
            (
                library_evidence.line_number
                if library_evidence
                else None
            ),
        )

    return evidence


def scan_model_artifact(
    file_path: Path,
):

    if (
        file_path.suffix.lower()
        not in MODEL_ARTIFACT_EXTENSIONS
    ):
        return []

    # -----------------------------------------------------
    # Ignore backup / test / copy / old model artifacts
    # -----------------------------------------------------

    model_name = file_path.stem.lower()

    ignored_keywords = {
        "backup",
        "test",
        "copy",
        "old",
    }

    if any(
        keyword in model_name
        for keyword in ignored_keywords
    ):
        return []

    # -----------------------------------------------------
    # Valid model artifact
    # -----------------------------------------------------

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

    # =====================================================
    # STRONG API / MODEL EXECUTION
    # =====================================================

    has_strong_api = any(
        (
            "api invocation" in value
            or "chat completion" in value
            or "embeddings invocation" in value
            or "responses api" in value
            or "messages api" in value
            or "llm invocation" in value
            or "llm generation" in value
        )
        for value in evidence_values
    )

    # =====================================================
    # LLM / AGENT EXECUTION
    # =====================================================

    has_llm_usage = (
        "llm_usage"
        in evidence_types
    )

    has_agent_signal = (
        "agent_signal"
        in evidence_types
    )

    if (
        has_llm_usage
        and has_agent_signal
    ):

        return "High"

    if has_llm_usage:

        return "High"

    if has_strong_api:

        return "High"

    # =====================================================
    # MODEL LOADING + PREDICTION
    # =====================================================

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
        has_model_load
        and has_prediction
    ):

        return "High"

    # =====================================================
    # LIBRARY + GENUINE ML EXECUTION
    # =====================================================

    if (
        "library_usage" in evidence_types
        and "model_usage" in evidence_types
    ):

        return "High"

    # =====================================================
    # MODEL EXECUTION ONLY
    # =====================================================

    if "model_usage" in evidence_types:

        return "Medium"

    # =====================================================
    # MODEL ARTIFACT
    # =====================================================

    if "model_artifact" in evidence_types:

        return "Medium"

    # =====================================================
    # LIBRARY ONLY
    # =====================================================

    if (
        "library_usage" in evidence_types
        or "dependency_usage" in evidence_types
    ):

        return "Low"

    # =====================================================
    # LLM MODEL REFERENCE ONLY
    # =====================================================

    if "llm_detection" in evidence_types:

        return "Medium"

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
        or "dependency_usage" in evidence_types
    )

    has_execution = (
        "model_usage"
        in evidence_types
    )

    has_artifact = (
        "model_artifact"
        in evidence_types
    )

    has_llm = (
        "llm_detection"
        in evidence_types
        or "llm_usage"
        in evidence_types
    )

    has_agent_signal = (
        "agent_signal"
        in evidence_types
    )

    # =====================================================
    # AI AGENT
    # =====================================================

    if (
        has_llm
        and has_agent_signal
    ):

        return "AI Agent"

    # =====================================================
    # LLM APPLICATION
    # =====================================================

    if has_llm:

        return "AI Application"

    # =====================================================
    # STRONG AI API EXECUTION
    # =====================================================

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

    # =====================================================
    # GENUINE MODEL EXECUTION
    # =====================================================

    if has_execution:

        return "AI Application"

    # =====================================================
    # MODEL ARTIFACT
    # =====================================================

    if has_artifact:

        return "AI Model Artifact"

    # =====================================================
    # LIBRARY ONLY
    # =====================================================

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

    if (
        asset_type
        == "Potential AI Reference"
    ):

        return "Needs Review"

    if confidence in {
        "High",
        "Medium",
    }:

        return "Discovered / Pending Review"

    return "Needs Review"



# =========================================================
# DETECT AI DEPENDENCIES
# =========================================================

AI_DEPENDENCY_PATTERNS = {
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "transformers": "Hugging Face Transformers",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "scikit-learn": "Scikit-learn",
    "sklearn": "Scikit-learn",
    "langchain": "LangChain",
    "langchain-openai": "LangChain OpenAI",
    "langchain-anthropic": "LangChain Anthropic",
    "google-generativeai": "Google Generative AI",
    "google-cloud-aiplatform": "Google Vertex AI",
    "vertexai": "Google Vertex AI",
    "azure-ai": "Azure AI",
    "azure-ai-inference": "Azure AI Inference",
}


def detect_dependency_usage(
    file_path: Path,
    content: str,
) -> list[Evidence]:

    evidence = []

    file_name = file_path.name.lower()

    if file_name not in DEPENDENCY_FILES:
        return evidence

    for package_name, display_name in AI_DEPENDENCY_PATTERNS.items():

        pattern = re.escape(package_name)

        if not re.search(
            pattern,
            content,
            re.IGNORECASE,
        ):
            continue

        add_evidence(
            evidence,
            "dependency_usage",
            (
                f"{display_name} dependency detected "
                f"in {file_path.name}"
            ),
            file_path,
            find_match_line(
                content,
                pattern,
            ),
        )

    # -----------------------------------------------------
    # Azure OpenAI
    # -----------------------------------------------------

    azure_openai_pattern = (
        r"\bazure[-_]openai\b"
        r"|\bAzureOpenAI\b"
    )

    if re.search(
        azure_openai_pattern,
        content,
        re.IGNORECASE,
    ):

        add_evidence(
            evidence,
            "dependency_usage",
            (
                "Azure OpenAI dependency or configuration "
                f"detected in {file_path.name}"
            ),
            file_path,
            find_match_line(
                content,
                azure_openai_pattern,
            ),
        )

    # -----------------------------------------------------
    # Google / Vertex AI
    # -----------------------------------------------------

    google_pattern = (
        r"\bvertexai\b"
        r"|\bgoogle-generativeai\b"
        r"|\bgoogle\.cloud\b"
        r"|\bgoogle-cloud-aiplatform\b"
    )

    if re.search(
        google_pattern,
        content,
        re.IGNORECASE,
    ):

        add_evidence(
            evidence,
            "dependency_usage",
            (
                "Google / Vertex AI dependency or "
                f"configuration detected in {file_path.name}"
            ),
            file_path,
            find_match_line(
                content,
                google_pattern,
            ),
        )

    # -----------------------------------------------------
    # Remove duplicate dependency evidence
    # -----------------------------------------------------

    unique = []
    seen = set()

    for item in evidence:

        key = (
            item.type,
            item.value,
            item.file,
            item.line_number,
        )

        if key in seen:
            continue

        seen.add(key)
        unique.append(item)

    return unique


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

    # =====================================================
    # WALK REPOSITORY
    # =====================================================

    for file_path in root.rglob("*"):

        if not file_path.is_file():

            continue

        # =================================================
        # IGNORE UNWANTED DIRECTORIES
        # =================================================

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
        # Dependency / configuration files
        # -------------------------------------------------

        elif (
            file_path.name.lower()
            in DEPENDENCY_FILES
        ):

            dependency_content = read_text_file(
                file_path
            )

            dependency_content = normalize_content(
                dependency_content
            )

            dependency_content = remove_comments(
                dependency_content
            )

            evidence.extend(
                detect_dependency_usage(
                    file_path,
                    dependency_content,
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

        # =================================================
        # NO EVIDENCE
        # =================================================

        if not evidence:

            continue

        # =================================================
        # CONFIDENCE
        # =================================================

        confidence = determine_confidence(
            evidence
        )

        # =================================================
        # READ CONTENT FOR METADATA
        # =================================================

        content = read_text_file(
            file_path
        )

        content = normalize_content(
            content
        )

        content = remove_comments(
            content
        )

        # =================================================
        # ENTERPRISE FIELDS
        # =================================================

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

        # =================================================
        # CREATE AI ASSET
        # =================================================

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

            tools=[],

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


# =========================================================
# NORMALIZE EVIDENCE PATH
# =========================================================

def normalize_evidence_path(
    file_path: str,
    repository_root: str | Path | None = None,
) -> str:

    if not file_path:

        return "Unknown file"

    if repository_root:

        try:

            root = Path(
                repository_root
            ).resolve()

            path = Path(
                file_path
            ).resolve()

            relative_path = path.relative_to(
                root
            )

            # Always return a clean UI path
            return relative_path.as_posix()

        except (
            ValueError,
            OSError,
        ):

            pass

    # Fallback
    return Path(
        file_path
    ).name

# =========================================================
# AGGREGATE PROVIDERS
# =========================================================

def aggregate_providers(
    findings: list[AIAsset],
) -> str:

    providers = []

    for finding in findings:

        provider = (
            finding.provider
            if finding.provider
            else ""
        ).strip()

        if not provider:
            continue

        if provider == "Not detected":
            continue

        for item in provider.split(","):

            item = item.strip()

            if item and item not in providers:
                providers.append(item)

    # -----------------------------------------------------
    # Local model evidence
    # -----------------------------------------------------

    has_local_model = any(
        item.type == "model_artifact"
        for finding in findings
        for item in finding.evidence
    )

    if has_local_model:
        if "Internal / Local ML" not in providers:
            providers.append("Internal / Local ML")

    if not providers:
        return "Not detected"

    return " / ".join(providers)


# =========================================================
# AGGREGATE LOCATIONS
# =========================================================

def aggregate_locations(
    findings: list[AIAsset],
) -> str:

    locations = []

    # -----------------------------------------------------
    # Detect locations from individual findings
    # -----------------------------------------------------

    for finding in findings:

        location = (
            finding.location
            if finding.location
            else ""
        ).strip()

        if not location:
            continue

        if location == "Not detected":
            continue

        if location not in locations:
            locations.append(location)

    # -----------------------------------------------------
    # Cloud provider detection
    # -----------------------------------------------------

    cloud_providers = {
        "OpenAI",
        "Azure OpenAI",
        "Anthropic",
        "Google Vertex AI",
    }

    has_cloud_provider = any(
        provider in cloud_providers
        for finding in findings
        for provider in (
            finding.provider.split(",")
            if finding.provider
            else []
        )
    )

    if has_cloud_provider:
        if "Cloud" not in locations:
            locations.insert(0, "Cloud")

    # -----------------------------------------------------
    # Local model artifact detection
    # -----------------------------------------------------

    has_local_model = any(
        item.type == "model_artifact"
        for finding in findings
        for item in finding.evidence
    )

    if has_local_model:
        if "Local Environment" not in locations:
            locations.append(
                "Local Environment"
            )

    if not locations:
        return "Not detected"

    return " / ".join(locations)
# =========================================================
# AGGREGATED PROVIDER
# =========================================================

def determine_aggregated_provider(
    findings: list[AIAsset],
) -> str:

    providers = []

    for finding in findings:

        provider = (
            finding.provider or ""
        ).strip()

        if not provider:
            continue

        if provider == "Not detected":
            continue

        for item in provider.split(","):

            item = item.strip()

            if item and item not in providers:
                providers.append(item)

    # -----------------------------------------------------
    # Detect local ML from model artifacts / local models
    # -----------------------------------------------------

    has_local_model = False

    for finding in findings:

        if finding.model != "Not detected":
            has_local_model = True

        if any(
            evidence.type == "model_artifact"
            for evidence in finding.evidence
        ):
            has_local_model = True

    if has_local_model:
        if "Internal / Local ML" not in providers:
            providers.append("Internal / Local ML")

    # -----------------------------------------------------
    # Clean provider naming
    # -----------------------------------------------------

    if not providers:
        return "Not detected"

    return " / ".join(providers)


# =========================================================
# AGGREGATED LOCATION
# =========================================================

def determine_aggregated_location(
    findings: list[AIAsset],
) -> str:

    locations = []

    for finding in findings:

        location = (
            finding.location or ""
        ).strip()

        if not location:
            continue

        if location == "Not detected":
            continue

        for item in location.split("/"):

            item = item.strip()

            if item and item not in locations:
                locations.append(item)

    # -----------------------------------------------------
    # Local model evidence
    # -----------------------------------------------------

    has_local_model = False

    for finding in findings:

        if any(
            evidence.type == "model_artifact"
            for evidence in finding.evidence
        ):
            has_local_model = True

        if (
            finding.model
            and finding.model != "Not detected"
        ):
            has_local_model = True

    if has_local_model:

        if "Local Environment" not in locations:
            locations.append(
                "Local Environment"
            )

    # -----------------------------------------------------
    # Normalize cloud location
    # -----------------------------------------------------

    if "Cloud" in locations:
        locations = [
            item
            for item in locations
            if item != "Cloud"
        ]

        locations.insert(0, "Cloud")

    if not locations:
        return "Not detected"

    return " / ".join(locations)    
# =========================================================
# AGGREGATE APPLICATION ASSETS
# =========================================================

def aggregate_application_assets(
    assets: list[AIAsset],
    repository_root: str | Path | None = None,
) -> list[AIAsset]:

    applications = {}

    # =====================================================
    # APPLICATION METADATA
    # =====================================================

    metadata = {

        "ai-assist": {

            "name": "AI Assist",

            "purpose": (
                "Provide AI-powered employee assistance"
            ),

            "tools": [
                "Employee Support",
                "Internal ML Models",
            ],
        },

        "enterprise-knowledge": {

            "name": "Enterprise Knowledge",

            "purpose": (
                "Search and analyze enterprise knowledge"
            ),

            "tools": [
                "Knowledge Search",
                "Internal ML Models",
            ],
        },

        "incident-intelligence": {

            "name": "Incident Intelligence",

            "purpose": (
                "Investigate and classify incidents"
            ),

            "tools": [
                "Incident Analysis",
                "Internal ML Models",
            ],
        },
    }

    # =====================================================
    # IDENTIFY APPLICATION
    # =====================================================

    for asset in assets:

        paths = [
            item.file.lower()
            for item in asset.evidence
            if item.file
        ]

        application_key = "other"

        for file_path in paths:

            if (
                "\\ai-assist\\" in file_path
                or "/ai-assist/" in file_path
            ):

                application_key = "ai-assist"

                break

            if (
                "\\enterprise-knowledge\\" in file_path
                or "/enterprise-knowledge/" in file_path
            ):

                application_key = (
                    "enterprise-knowledge"
                )

                break

            if (
                "\\incident-intelligence\\" in file_path
                or "/incident-intelligence/" in file_path
            ):

                application_key = (
                    "incident-intelligence"
                )

                break

        if application_key == "other":

            continue

        if application_key not in applications:

            applications[
                application_key
            ] = []

        applications[
            application_key
        ].append(asset)

    # =====================================================
    # BUILD AGGREGATED ASSETS
    # =====================================================

    aggregated = []

    application_order = [
        "incident-intelligence",
        "enterprise-knowledge",
        "ai-assist",
    ]

    for application_key in application_order:

        if (
            application_key
            not in applications
        ):

            continue

        findings = applications[
            application_key
        ]

        info = metadata[
            application_key
        ]

        # =================================================
        # COLLECT REAL MODEL ARTIFACTS
        # =================================================

        models = []

        for finding in findings:

            for item in finding.evidence:

                if (
                    item.type
                    != "model_artifact"
                ):

                    continue

                match = re.search(
                    r"Trained model artifact detected:\s*(.+)$",
                    item.value,
                    re.IGNORECASE,
                )

                if not match:

                    continue

                artifact_name = (
                    match.group(1).strip()
                )

                model_name = Path(
                    artifact_name
                ).stem

                model_lower = (
                    model_name.lower()
                )

                # -----------------------------------------
                # Ignore backup/test/copy/old artifacts
                # -----------------------------------------

                if any(
                    keyword in model_lower
                    for keyword in [
                        "backup",
                        "test",
                        "copy",
                        "old",
                    ]
                ):

                    continue

                if (
                    model_name
                    not in models
                ):

                    models.append(
                        model_name
                    )

        # =================================================
        # COLLECT LLM MODELS
        # =================================================

        for finding in findings:

            if (
                finding.model
                and finding.model
                != "Not detected"
                and finding.model
                not in models
                and (
                    finding.asset_type
                    in {
                        "AI Agent",
                        "AI Application",
                    }
                )
            ):

                # Do not replace local artifact
                # models with generic local model names.
                if finding.model != "Local ML Model":

                    models.append(
                        finding.model
                    )

        # =================================================
        # COLLECT MEANINGFUL EVIDENCE
        # =================================================

        evidence = []

        for finding in findings:

            # ---------------------------------------------
            # Include supporting evidence from all findings.
            #
            # Potential AI Reference findings are excluded
            # from confidence/type calculation below, but
            # their dependency evidence is still useful to
            # the aggregated application record.
            # ---------------------------------------------

            for item in finding.evidence:

                evidence_file = (
                    item.file.lower()
                    if item.file
                    else ""
                )

                # -----------------------------------------
                # Ignore known false-positive files
                # -----------------------------------------

                test_file_names = {
                    "false_positive_test.py",
                    "model_reference_only.py",
                    "unused_ai_import.py",
                }

                if any(
                    evidence_file.endswith(
                        "\\" + name
                    )
                    or evidence_file.endswith(
                        "/" + name
                    )
                    for name in test_file_names
                ):

                    continue

                # -----------------------------------------
                # Normalize evidence path
                # -----------------------------------------

                clean_file = (
                    normalize_evidence_path(
                        item.file,
                        repository_root,
                    )
                )

                evidence.append(
                    Evidence(
                        type=item.type,
                        value=item.value,
                        file=clean_file,
                        line_number=item.line_number,
                    )
                )

        # =================================================
        # MEANINGFUL FINDINGS
        # =================================================

        meaningful_findings = [
            finding
            for finding in findings
            if finding.asset_type
            != "Potential AI Reference"
        ]

        # =================================================
        # CONFIDENCE
        # =================================================

        confidences = {
            finding.confidence
            for finding in meaningful_findings
        }

        if "High" in confidences:

            confidence = "High"

        elif "Medium" in confidences:

            confidence = "Medium"

        else:

            confidence = "Low"

        # =================================================
        # ASSET TYPE
        # =================================================

        has_ai_agent = any(
            finding.asset_type
            == "AI Agent"
            for finding in meaningful_findings
        )

        if has_ai_agent:

            aggregated_asset_type = (
                "AI Agent"
            )

        else:

            aggregated_asset_type = (
                "AI Application"
            )

        # =================================================
        # MODEL DISPLAY
        # =================================================

        if models:

            model_display = ", ".join(
                models
            )

        else:

            model_display = "Local ML Model"

        # =================================================
        # CREATE ENTERPRISE APPLICATION ASSET
        # =================================================
        provider = determine_aggregated_provider(
        findings
        )

        location = determine_aggregated_location(
        findings
        )
        aggregated.append(
            AIAsset(

                id=(
                    f"AI-{len(aggregated) + 1:04d}"
                ),

                name=info["name"],

                asset_type=(
                    aggregated_asset_type
                ),

                model=model_display,

                provider=provider,

                location=location,

                application=info["name"],

                purpose=info["purpose"],

                tools=info["tools"],

                discovery_source=(
                    "Local Repository"
                ),

                status=(
                    "Discovered / Pending Review"
                ),

                category="AI/ML",

                confidence=confidence,

                evidence=evidence,

                description=(
                    f"{info['name']} contains AI/ML "
                    "functionality discovered through "
                    "source-code analysis and model "
                    "artifacts."
                ),
            )
        )

    return aggregated