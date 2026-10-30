"""
VISTA Risk Model Evaluation & Validation Runner
===============================================
Evaluates XGBoost and Logistic Regression classifiers on student_data.csv.
Computes Confusion Matrix, Precision, Recall, Macro F1, and SHAP explanations.
Outputs results to evaluation/results/risk_model_evaluation.json.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

# Path setup
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

RESULTS_DIR = ROOT_DIR / "evaluation" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def evaluate_risk_models():
    print("Evaluating VISTA Risk Prediction ML Models...")

    try:
        import pandas as pd
        from sklearn.metrics import classification_report, confusion_matrix, f1_score
        from sklearn.model_selection import train_test_split
    except ImportError as e:
        print(f"Scikit-learn / pandas missing: {e}")
        return

    csv_path = ROOT_DIR / "vista" / "ml" / "data" / "student_data.csv"
    if not csv_path.exists():
        print(f"student_data.csv not found at {csv_path}")
        return

    df = pd.read_csv(csv_path)
    print(f"Loaded student data: {len(df)} rows, columns: {list(df.columns)}")

    feature_cols = ["overall_attendance", "recent_attendance", "avg_score", "recent_score", "failed_subjects"]
    X = df[feature_cols].values
    y = df["risk_label"].values

    classes = ["LOW", "MEDIUM", "HIGH"]
    class_to_idx = {c: i for i, c in enumerate(classes)}
    y_idx = np.array([class_to_idx[v] for v in y])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_idx, test_size=0.2, random_state=42, stratify=y_idx
    )

    results = {}

    # 1. XGBoost
    try:
        from xgboost import XGBClassifier
        xgb = XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            eval_metric="mlogloss",
            random_state=42
        )
        xgb.fit(X_train, y_train)
        y_pred_xgb = xgb.predict(X_test)

        report_xgb = classification_report(
            y_test, y_pred_xgb, target_names=classes, output_dict=True
        )
        cm_xgb = confusion_matrix(y_test, y_pred_xgb).tolist()

        results["xgboost"] = {
            "dataset": "student_data.csv (synthetic)",
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "accuracy": round(float(report_xgb["accuracy"]), 4),
            "macro_f1": round(float(report_xgb["macro avg"]["f1-score"]), 4),
            "macro_precision": round(float(report_xgb["macro avg"]["precision"]), 4),
            "macro_recall": round(float(report_xgb["macro avg"]["recall"]), 4),
            "confusion_matrix": cm_xgb,
            "per_class": {
                c: {
                    "precision": round(float(report_xgb[c]["precision"]), 4),
                    "recall": round(float(report_xgb[c]["recall"]), 4),
                    "f1_score": round(float(report_xgb[c]["f1-score"]), 4),
                    "support": int(report_xgb[c]["support"])
                } for c in classes
            }
        }
    except Exception as exc:
        results["xgboost"] = {"status": "error", "error": str(exc)}

    # 2. Logistic Regression (Baseline)
    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        from sklearn.pipeline import Pipeline

        lr_pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("lr", LogisticRegression(max_iter=500, class_weight="balanced", random_state=42))
        ])
        lr_pipe.fit(X_train, y_train)
        y_pred_lr = lr_pipe.predict(X_test)

        report_lr = classification_report(
            y_test, y_pred_lr, target_names=classes, output_dict=True
        )
        cm_lr = confusion_matrix(y_test, y_pred_lr).tolist()

        results["logistic_regression"] = {
            "dataset": "student_data.csv (synthetic)",
            "accuracy": round(float(report_lr["accuracy"]), 4),
            "macro_f1": round(float(report_lr["macro avg"]["f1-score"]), 4),
            "confusion_matrix": cm_lr,
            "per_class": {
                c: {
                    "precision": round(float(report_lr[c]["precision"]), 4),
                    "recall": round(float(report_lr[c]["recall"]), 4),
                    "f1_score": round(float(report_lr[c]["f1-score"]), 4),
                    "support": int(report_lr[c]["support"])
                } for c in classes
            }
        }
    except Exception as exc:
        results["logistic_regression"] = {"status": "error", "error": str(exc)}

    # 3. SHAP Feature Explanations
    try:
        from vista.ml.explainer import explain_prediction
        from vista.ml.features import StudentMetrics, compute_features

        sample_vector = [52.0, 48.0, 45.0, 40.0, 2.0]
        reasons = explain_prediction(sample_vector)
        results["shap_explainer_sample"] = {
            "sample_input": {
                "overall_attendance": 52.0,
                "recent_attendance": 48.0,
                "avg_score": 45.0,
                "recent_score": 40.0,
                "failed_subjects": 2.0
            },
            "generated_reasons": reasons
        }
    except Exception as exc:
        results["shap_explainer_sample"] = {"status": "skipped", "reason": str(exc)}

    out_file = RESULTS_DIR / "risk_model_evaluation.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Saved risk model evaluation to {out_file}")
    return results


if __name__ == "__main__":
    evaluate_risk_models()
