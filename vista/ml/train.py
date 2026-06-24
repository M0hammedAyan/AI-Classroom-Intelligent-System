"""
VISTA ML Training Script
========================
Trains XGBoost and Logistic Regression classifiers on student_data.csv.
Selects the winner by macro-averaged F1 and saves it as model.pkl.

Usage (from project root):
    python -m vista.ml.train
    python vista/ml/train.py

Dependencies: numpy, pandas, scikit-learn, xgboost
"""
from __future__ import annotations

import pickle
import sys
from pathlib import Path

DATA_PATH = Path(__file__).parent / "data" / "student_data.csv"
MODEL_PATH = Path(__file__).parent / "model.pkl"

LABEL_MAP = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
LABEL_NAMES = ["LOW", "MEDIUM", "HIGH"]

FEATURES = [
    "overall_attendance",
    "recent_attendance",
    "avg_score",
    "recent_score",
    "failed_subjects",
]


def _load_data():
    try:
        import pandas as pd
    except ImportError:
        print("pandas is required: pip install pandas")
        sys.exit(1)

    if not DATA_PATH.exists():
        print(f"Training data not found: {DATA_PATH}")
        print("Run first: python -m vista.ml.data.generate_sample_data")
        sys.exit(1)

    df = pd.read_csv(DATA_PATH)
    missing = set(FEATURES + ["risk_label"]) - set(df.columns)
    if missing:
        print(f"Missing columns in training data: {missing}")
        sys.exit(1)

    X = df[FEATURES].values
    y = df["risk_label"].map(LABEL_MAP).values
    return X, y


def _train_and_eval(X_train, X_test, y_train, y_test):
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import classification_report, f1_score
    from sklearn.preprocessing import StandardScaler

    try:
        from xgboost import XGBClassifier
        has_xgb = True
    except ImportError:
        has_xgb = False
        print("xgboost not found — training Logistic Regression only.")
        print("Install with: pip install xgboost")

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    results = {}

    # Logistic Regression
    lr = LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced")
    lr.fit(X_train_s, y_train)
    lr_preds = lr.predict(X_test_s)
    lr_f1 = f1_score(y_test, lr_preds, average="macro")
    results["LogisticRegression"] = {
        "model": lr,
        "scaler": scaler,
        "f1": lr_f1,
        "preds": lr_preds,
        "needs_scaling": True,
    }
    print("\nLogistic Regression:")
    print(classification_report(y_test, lr_preds, target_names=LABEL_NAMES))

    # XGBoost
    if has_xgb:
        xgb = XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            eval_metric="mlogloss",
            random_state=42,
        )
        xgb.fit(X_train, y_train)
        xgb_preds = xgb.predict(X_test)
        xgb_f1 = f1_score(y_test, xgb_preds, average="macro")
        results["XGBoost"] = {
            "model": xgb,
            "scaler": None,
            "f1": xgb_f1,
            "preds": xgb_preds,
            "needs_scaling": False,
        }
        print("XGBoost:")
        print(classification_report(y_test, xgb_preds, target_names=LABEL_NAMES))

    return results


def _select_winner(results: dict) -> tuple[str, dict]:
    best_name = max(results, key=lambda k: results[k]["f1"])
    return best_name, results[best_name]


def _save_model(name: str, result: dict) -> None:
    artifact = {
        "model_name": name,
        "model": result["model"],
        "scaler": result["scaler"],
        "needs_scaling": result["needs_scaling"],
        "features": FEATURES,
        "label_map": LABEL_MAP,
        "label_names": LABEL_NAMES,
    }
    with MODEL_PATH.open("wb") as f:
        pickle.dump(artifact, f)
    print(f"\nSaved model artifact: {MODEL_PATH}")


def main() -> None:
    try:
        from sklearn.model_selection import train_test_split
    except ImportError:
        print("scikit-learn is required: pip install scikit-learn")
        sys.exit(1)

    print("=" * 55)
    print("  VISTA Risk Engine — Training")
    print("=" * 55)
    print(f"  Data   : {DATA_PATH}")
    print(f"  Output : {MODEL_PATH}")

    X, y = _load_data()
    print(f"\n  Loaded {len(X)} samples.")

    label_counts = {name: int((y == idx).sum()) for idx, name in enumerate(LABEL_NAMES)}
    print("  Label distribution:")
    for level, count in label_counts.items():
        print(f"    {level:6s}: {count:3d}  ({count/len(y)*100:.1f}%)")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\n  Train: {len(X_train)} | Test: {len(X_test)}")
    print("\n" + "=" * 55)

    results = _train_and_eval(X_train, X_test, y_train, y_test)

    best_name, best = _select_winner(results)
    print("=" * 55)
    print(f"  Winner: {best_name}  (macro F1 = {best['f1']:.3f})")
    print("=" * 55)

    _save_model(best_name, best)
    print("\nDone. Run tests with: python -m vista.ml.test_risk_engine")


if __name__ == "__main__":
    main()
