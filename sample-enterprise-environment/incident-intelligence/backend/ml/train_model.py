import json
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "training_data.json"
MODEL_DIR = BASE_DIR / "ml" / "artifacts"


def load_training_data():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def train_model(texts, labels):
    model = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 2),
                    sublinear_tf=True,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                ),
            ),
        ]
    )

    model.fit(texts, labels)

    return model


def main():
    print("Loading training data...")

    training_data = load_training_data()

    texts = [item["text"] for item in training_data]

    categories = [
        item["category"]
        for item in training_data
    ]

    severities = [
        item["severity"]
        for item in training_data
    ]

    teams = [
        item["team"]
        for item in training_data
    ]

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    print("Training category model...")
    category_model = train_model(
        texts,
        categories,
    )

    print("Training severity model...")
    severity_model = train_model(
        texts,
        severities,
    )

    print("Training team model...")
    team_model = train_model(
        texts,
        teams,
    )

    joblib.dump(
        category_model,
        MODEL_DIR / "category_model.joblib",
    )

    joblib.dump(
        severity_model,
        MODEL_DIR / "severity_model.joblib",
    )

    joblib.dump(
        team_model,
        MODEL_DIR / "team_model.joblib",
    )

    print()
    print("Training completed successfully.")
    print(f"Models saved to: {MODEL_DIR}")


if __name__ == "__main__":
    main()