import json
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = BASE_DIR / "training_data.json"
MODEL_FILE = BASE_DIR / "artifacts" / "enterprise_knowledge_model.joblib"


def load_training_data():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    texts = [item["text"] for item in data]
    categories = [item["category"] for item in data]

    return texts, categories


def train_model():
    texts, categories = load_training_data()

    model = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 2),
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

    model.fit(texts, categories)

    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODEL_FILE)

    print("Enterprise Knowledge local ML model trained successfully.")
    print(f"Training samples: {len(texts)}")
    print(f"Categories: {sorted(set(categories))}")
    print(f"Model saved to: {MODEL_FILE}")


if __name__ == "__main__":
    train_model()