from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_PATH = PROJECT_ROOT / "ml" / "data" / "sample" / "student_data.csv"
MODEL_PATH = PROJECT_ROOT / "ml" / "saved_models" / "model.pkl"
TEST_SIZE = 0.2
RANDOM_STATE = 42
MEDIUM_AUGMENT_COPIES = 2


try:
    from ml.src.features.build_features import build_features, load_dataset
except ModuleNotFoundError:
    import sys

    sys.path.append(str(PROJECT_ROOT))
    from ml.src.features.build_features import build_features, load_dataset


def prepare_model_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """Split engineered features into model inputs and target labels."""
    y = df["label"].astype(int)
    x = df.drop(columns=["student_id", "label"])
    return x, y


def augment_medium_risk_examples(
    raw_df: pd.DataFrame,
    copies: int = MEDIUM_AUGMENT_COPIES,
    random_state: int = RANDOM_STATE,
) -> pd.DataFrame:
    """Add slight variations around borderline students to improve medium-risk sensitivity."""
    working_df = raw_df.copy()
    medium_mask = (
        working_df["overall_attendance"].between(60, 75, inclusive="both")
        & working_df["avg_score"].between(40, 60, inclusive="both")
    )

    medium_df = working_df.loc[medium_mask].copy()
    if medium_df.empty:
        return working_df

    rng = np.random.default_rng(random_state)
    augmented_frames = [working_df]

    for _ in range(copies):
        noisy = medium_df.copy()
        noisy["overall_attendance"] = np.clip(
            noisy["overall_attendance"] + rng.normal(0.0, 2.0, size=len(noisy)),
            0,
            100,
        )
        noisy["recent_attendance"] = np.clip(
            noisy["recent_attendance"] + rng.normal(0.0, 2.5, size=len(noisy)),
            0,
            100,
        )
        noisy["avg_score"] = np.clip(
            noisy["avg_score"] + rng.normal(0.0, 3.0, size=len(noisy)),
            0,
            100,
        )
        noisy["recent_score"] = np.clip(
            noisy["recent_score"] + rng.normal(0.0, 3.5, size=len(noisy)),
            0,
            100,
        )
        failed_shift = rng.choice([-1, 0, 1], size=len(noisy), p=[0.2, 0.6, 0.2])
        noisy["failed_subjects"] = np.clip(noisy["failed_subjects"] + failed_shift, 0, 5).astype(int)
        augmented_frames.append(noisy)

    return pd.concat(augmented_frames, ignore_index=True)


def split_data(
    x: pd.DataFrame,
    y: pd.Series,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Create deterministic train/test splits with stratification when possible."""
    stratify = y if y.nunique() > 1 else None
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify,
    )
    return x_train, x_test, y_train, y_test


def _compute_scale_pos_weight(y_train: pd.Series) -> float:
    positives = int((y_train == 1).sum())
    negatives = int((y_train == 0).sum())
    if positives == 0:
        return 1.0
    return max(1.0, negatives / positives)


def get_models(y_train: pd.Series, random_state: int = RANDOM_STATE) -> Dict[str, Any]:
    """Initialize candidate models for risk prediction."""
    scale_pos_weight = _compute_scale_pos_weight(y_train)
    return {
        "logistic_regression": LogisticRegression(
            max_iter=1000,
            random_state=random_state,
            class_weight="balanced",
        ),
        "xgboost": XGBClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.08,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=random_state,
            eval_metric="logloss",
            scale_pos_weight=scale_pos_weight,
        ),
    }


def _predict_probabilities(model: Any, x_test: pd.DataFrame) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(x_test)
        return np.asarray(probs[:, 1], dtype=float)

    if hasattr(model, "decision_function"):
        decision = np.asarray(model.decision_function(x_test), dtype=float)
        return 1.0 / (1.0 + np.exp(-decision))

    predictions = np.asarray(model.predict(x_test), dtype=float)
    return predictions


def evaluate_model(model: Any, x_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
    """Compute classification metrics and diagnostics for a trained model."""
    predicted_probabilities = _predict_probabilities(model, x_test)
    predictions = model.predict(x_test)

    return {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1": float(f1_score(y_test, predictions, zero_division=0)),
        "probability_min": float(predicted_probabilities.min()),
        "probability_max": float(predicted_probabilities.max()),
        "confusion_matrix": confusion_matrix(y_test, predictions),
        "classification_report": classification_report(y_test, predictions, zero_division=0),
    }


def train_and_compare_models(
    models: Dict[str, Any],
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_test: pd.DataFrame,
    y_test: pd.Series,
) -> Tuple[pd.DataFrame, Dict[str, Any], Dict[str, Dict[str, Any]]]:
    """Train all candidate models and return their metric table."""
    trained_models: Dict[str, Any] = {}
    diagnostics: Dict[str, Dict[str, Any]] = {}
    rows = []

    for model_name, model in models.items():
        model.fit(x_train, y_train)
        trained_models[model_name] = model

        metrics = evaluate_model(model, x_test, y_test)
        diagnostics[model_name] = {
            "confusion_matrix": metrics["confusion_matrix"],
            "classification_report": metrics["classification_report"],
            "probability_min": metrics["probability_min"],
            "probability_max": metrics["probability_max"],
        }

        rows.append(
            {
                "model": model_name,
                "accuracy": metrics["accuracy"],
                "precision": metrics["precision"],
                "recall": metrics["recall"],
                "f1": metrics["f1"],
                "probability_min": metrics["probability_min"],
                "probability_max": metrics["probability_max"],
            }
        )

    results_df = pd.DataFrame(rows).sort_values(by="f1", ascending=False).reset_index(drop=True)
    return results_df, trained_models, diagnostics


def select_best_model(results_df: pd.DataFrame, trained_models: Dict[str, Any]) -> Tuple[str, Any]:
    """Pick the best model by F1-score."""
    best_model_name = str(results_df.loc[0, "model"])
    return best_model_name, trained_models[best_model_name]


def _create_model_by_name(model_name: str, y_train: pd.Series, random_state: int = RANDOM_STATE) -> Any:
    models = get_models(y_train=y_train, random_state=random_state)
    if model_name not in models:
        raise ValueError(f"Unsupported model for calibration: {model_name}")
    return models[model_name]


def calibrate_best_model(
    best_model_name: str,
    x_train: pd.DataFrame,
    y_train: pd.Series,
    random_state: int = RANDOM_STATE,
) -> Any:
    base_estimator = _create_model_by_name(best_model_name, y_train=y_train, random_state=random_state)
    calibrated_model = CalibratedClassifierCV(estimator=base_estimator, method="sigmoid", cv=3)
    calibrated_model.fit(x_train, y_train)
    return calibrated_model


def print_probability_comparison(raw_model: Any, calibrated_model: Any, x_test: pd.DataFrame) -> None:
    raw_probs = _predict_probabilities(raw_model, x_test)
    calibrated_probs = _predict_probabilities(calibrated_model, x_test)

    print("\nProbability comparison (raw vs calibrated):")
    print(
        "Raw probability range: "
        f"min={raw_probs.min():.4f}, max={raw_probs.max():.4f}, mean={raw_probs.mean():.4f}"
    )
    print(
        "Calibrated probability range: "
        f"min={calibrated_probs.min():.4f}, max={calibrated_probs.max():.4f}, mean={calibrated_probs.mean():.4f}"
    )


def print_feature_importance_validation(trained_models: Dict[str, Any], feature_columns: list[str]) -> None:
    for model_name, model in trained_models.items():
        if not hasattr(model, "feature_importances_"):
            continue

        importances = np.asarray(model.feature_importances_, dtype=float)
        print(f"\nFeature importance validation for {model_name} (model.feature_importances_):")
        print(importances)

        ranking_df = (
            pd.DataFrame({"feature": feature_columns, "importance": importances})
            .sort_values(by="importance", ascending=False)
            .head(10)
            .reset_index(drop=True)
        )
        print("Top feature importances:")
        print(ranking_df.to_string(index=False, float_format=lambda value: f"{value:.6f}"))


def save_model(model: Any, model_name: str, output_path: Path, feature_columns: list[str]) -> None:
    """Persist model artifact with minimal metadata for inference."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    artifact = {
        "model_name": model_name,
        "model": model,
        "feature_columns": feature_columns,
        "is_calibrated": isinstance(model, CalibratedClassifierCV),
    }
    with output_path.open("wb") as model_file:
        pickle.dump(artifact, model_file)


def run_training_pipeline(
    data_path: Path,
    model_output_path: Path,
) -> Tuple[
    pd.DataFrame,
    str,
    Path,
    Dict[str, Dict[str, Any]],
    Any,
    Any,
    pd.DataFrame,
    Dict[str, Any],
    list[str],
]:
    """Execute end-to-end training, evaluation, selection, and model persistence."""
    raw_df = load_dataset(data_path)
    raw_df = augment_medium_risk_examples(raw_df)
    feature_df = build_features(raw_df)

    x, y = prepare_model_data(feature_df)
    x_train, x_test, y_train, y_test = split_data(x, y)

    models = get_models(y_train=y_train)
    results_df, trained_models, diagnostics = train_and_compare_models(
        models,
        x_train,
        y_train,
        x_test,
        y_test,
    )
    best_model_name, best_model = select_best_model(results_df, trained_models)
    calibrated_best_model = calibrate_best_model(best_model_name, x_train, y_train)

    save_model(
        model=calibrated_best_model,
        model_name=f"{best_model_name}_calibrated",
        output_path=model_output_path,
        feature_columns=list(x.columns),
    )

    return (
        results_df,
        best_model_name,
        model_output_path,
        diagnostics,
        best_model,
        calibrated_best_model,
        x_test,
        trained_models,
        list(x.columns),
    )


def print_model_diagnostics(diagnostics: Dict[str, Dict[str, Any]]) -> None:
    for model_name, model_diagnostics in diagnostics.items():
        print(f"\nDiagnostics for {model_name}:")
        print("Confusion matrix:")
        print(model_diagnostics["confusion_matrix"])
        print("Classification report:")
        print(model_diagnostics["classification_report"])
        print(
            "Predicted probability range: "
            f"min={model_diagnostics['probability_min']:.4f}, "
            f"max={model_diagnostics['probability_max']:.4f}"
        )


def main() -> None:
    (
        results_df,
        best_model_name,
        saved_path,
        diagnostics,
        raw_best_model,
        calibrated_best_model,
        x_test,
        trained_models,
        feature_columns,
    ) = run_training_pipeline(DATA_PATH, MODEL_PATH)

    print("Model comparison:")
    print(results_df.to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    print_model_diagnostics(diagnostics)
    print_probability_comparison(raw_best_model, calibrated_best_model, x_test)
    print_feature_importance_validation(trained_models, feature_columns)
    print(f"\nBest model by F1-score: {best_model_name}")
    print(f"Saved calibrated best model to: {saved_path}")


if __name__ == "__main__":
    main()
