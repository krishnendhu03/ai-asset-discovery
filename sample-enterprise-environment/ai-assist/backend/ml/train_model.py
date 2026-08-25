from pathlib import Path
import json
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

TRAINING_DATA = BASE_DIR / "training_data.json"

ARTIFACTS_DIR = BASE_DIR / "artifacts"

MODEL_PATH = ARTIFACTS_DIR / "ai_assist_model.joblib"


# ---------------------------------------------------------
# Training
# ---------------------------------------------------------

def train_model():

    print("Loading training data...")

    with open(TRAINING_DATA, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not data:
        raise ValueError("Training data is empty.")

    texts = []
    labels = []

    for item in data:

        issue = str(item.get("issue", ""))
        service = str(item.get("service", ""))

        text = f"{issue} {service} {service}".strip()

        category = item.get("category")

        if not text:
            continue

        if not category:
            continue

        texts.append(text)
        labels.append(category)

    if len(texts) < 2:
        raise ValueError("Not enough training examples.")

    if len(set(labels)) < 2:
        raise ValueError(
            "Training data must contain at least two categories."
        )

    print(f"Training examples: {len(texts)}")
    print(f"Categories: {sorted(set(labels))}")

    # -----------------------------------------------------
    # TF-IDF + Logistic Regression
    # -----------------------------------------------------

    model = Pipeline(
        [
            (
                "vectorizer",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 2),
                    sublinear_tf=True
                )
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=3000,
                    class_weight="balanced",
                    C=5.0
                )
            )
        ]
    )

    print("Training local ML model...")

    model.fit(texts, labels)

    # -----------------------------------------------------
    # Save model
    # -----------------------------------------------------

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODEL_PATH)

    print()
    print("==========================================")
    print("Local ML model trained successfully.")
    print("==========================================")
    print(f"Model saved to:")
    print(MODEL_PATH)


if __name__ == "__main__":
    train_model()