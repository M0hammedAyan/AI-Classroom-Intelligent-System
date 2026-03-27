import numpy as np
import pandas as pd


RNG_SEED = 42
NUM_STUDENTS = 200
OUTPUT_PATH = "ml/data/sample/student_data.csv"
MIN_FAIL_RATE = 0.40


def _clip(values: np.ndarray, low: float, high: float) -> np.ndarray:
    return np.clip(values, low, high)


def generate_student_ids(num_students: int) -> np.ndarray:
    return np.array([f"S{idx:04d}" for idx in range(1, num_students + 1)], dtype=object)


def _build_high_risk_group(count: int, rng: np.random.Generator) -> pd.DataFrame:
    overall_attendance = _clip(rng.normal(loc=49.0, scale=8.0, size=count), 25, 59.8)
    avg_score = _clip(rng.normal(loc=33.0, scale=7.5, size=count), 5, 39.8)

    failed_subjects = _clip(rng.poisson(lam=3.2, size=count), 2, 5).astype(int)
    recent_attendance = _clip(overall_attendance + rng.normal(loc=-5.0, scale=7.0, size=count), 0, 100)
    recent_score = _clip(avg_score + rng.normal(loc=-4.5, scale=6.0, size=count), 0, 100)

    return pd.DataFrame(
        {
            "overall_attendance": np.round(overall_attendance, 2),
            "recent_attendance": np.round(recent_attendance, 2),
            "avg_score": np.round(avg_score, 2),
            "recent_score": np.round(recent_score, 2),
            "failed_subjects": failed_subjects,
        }
    )


def _build_low_risk_group(count: int, rng: np.random.Generator) -> pd.DataFrame:
    overall_attendance = _clip(rng.normal(loc=86.0, scale=6.0, size=count), 75.2, 100)
    avg_score = _clip(rng.normal(loc=76.0, scale=8.0, size=count), 60.2, 100)

    failed_subjects = rng.choice([0, 1], size=count, p=[0.72, 0.28]).astype(int)
    recent_attendance = _clip(overall_attendance + rng.normal(loc=1.2, scale=5.5, size=count), 0, 100)
    recent_score = _clip(avg_score + rng.normal(loc=1.5, scale=6.5, size=count), 0, 100)

    return pd.DataFrame(
        {
            "overall_attendance": np.round(overall_attendance, 2),
            "recent_attendance": np.round(recent_attendance, 2),
            "avg_score": np.round(avg_score, 2),
            "recent_score": np.round(recent_score, 2),
            "failed_subjects": failed_subjects,
        }
    )


def _build_medium_risk_group(count: int, rng: np.random.Generator) -> pd.DataFrame:
    overall_attendance = _clip(rng.normal(loc=68.0, scale=9.0, size=count), 45, 90)
    avg_score = _clip(rng.normal(loc=54.0, scale=10.0, size=count), 28, 85)

    failed_subjects = _clip(rng.poisson(lam=1.3, size=count), 0, 4).astype(int)
    recent_attendance = _clip(overall_attendance + rng.normal(loc=-1.0, scale=7.0, size=count), 0, 100)
    recent_score = _clip(avg_score + rng.normal(loc=-1.0, scale=7.5, size=count), 0, 100)

    return pd.DataFrame(
        {
            "overall_attendance": np.round(overall_attendance, 2),
            "recent_attendance": np.round(recent_attendance, 2),
            "avg_score": np.round(avg_score, 2),
            "recent_score": np.round(recent_score, 2),
            "failed_subjects": failed_subjects,
        }
    )


def generate_features(num_students: int, rng: np.random.Generator) -> pd.DataFrame:
    high_risk_count = int(num_students * 0.45)
    low_risk_count = int(num_students * 0.40)
    medium_risk_count = num_students - high_risk_count - low_risk_count

    high_risk_df = _build_high_risk_group(high_risk_count, rng)
    low_risk_df = _build_low_risk_group(low_risk_count, rng)
    medium_risk_df = _build_medium_risk_group(medium_risk_count, rng)

    features_df = pd.concat([high_risk_df, low_risk_df, medium_risk_df], ignore_index=True)
    features_df = features_df.sample(frac=1.0, random_state=int(rng.integers(1, 1_000_000))).reset_index(drop=True)

    features_df.insert(0, "student_id", generate_student_ids(num_students))
    return features_df


def compute_fail_probability(df: pd.DataFrame) -> np.ndarray:
    low_attendance = (60.0 - df["overall_attendance"]) / 12.0
    low_score = (40.0 - df["avg_score"]) / 10.0
    recent_attendance_drop = (df["overall_attendance"] - df["recent_attendance"]) / 15.0
    recent_score_drop = (df["avg_score"] - df["recent_score"]) / 12.0
    failure_burden = (df["failed_subjects"] - 1.0) / 1.2

    high_risk_condition = (
        (df["overall_attendance"] < 60)
        & (df["avg_score"] < 40)
        & (df["failed_subjects"] >= 2)
    )
    low_risk_condition = (
        (df["overall_attendance"] > 75)
        & (df["avg_score"] > 60)
        & (df["failed_subjects"] <= 1)
    )

    risk_logit = (
        -0.55
        + 1.20 * low_attendance
        + 1.35 * low_score
        + 0.65 * recent_attendance_drop
        + 0.75 * recent_score_drop
        + 0.85 * failure_burden
        + np.where(high_risk_condition, 1.35, 0.0)
        + np.where(low_risk_condition, -1.40, 0.0)
        + np.where(high_risk_condition & ~low_risk_condition, 0.35, 0.0)
    )

    probabilities = 1.0 / (1.0 + np.exp(-risk_logit))
    return _clip(probabilities, 0.03, 0.97)


def assign_labels(
    probabilities: np.ndarray,
    rng: np.random.Generator,
    min_fail_rate: float = MIN_FAIL_RATE,
) -> np.ndarray:
    labels = rng.binomial(n=1, p=probabilities).astype(int)

    min_fails = int(np.ceil(len(labels) * min_fail_rate))
    current_fails = int(labels.sum())

    if current_fails < min_fails:
        deficit = min_fails - current_fails
        candidate_indices = np.where(labels == 0)[0]
        if candidate_indices.size > 0:
            candidate_probs = probabilities[candidate_indices]
            promote_order = np.argsort(-candidate_probs)
            promote_indices = candidate_indices[promote_order[:deficit]]
            labels[promote_indices] = 1

    return labels


def print_label_distribution(df: pd.DataFrame) -> None:
    label_counts = df["label"].value_counts().reindex([0, 1], fill_value=0)
    total = len(df)
    fail_rate = label_counts[1] / total if total else 0.0

    print("Label distribution:")
    print(f"  label=0: {int(label_counts[0])}")
    print(f"  label=1: {int(label_counts[1])}")
    print(f"  fail_rate: {fail_rate:.2%}")


def build_dataset(num_students: int, rng_seed: int = RNG_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(rng_seed)
    features_df = generate_features(num_students=num_students, rng=rng)
    probabilities = compute_fail_probability(features_df)
    features_df["label"] = assign_labels(probabilities=probabilities, rng=rng)
    return features_df


def save_dataset(df: pd.DataFrame, output_path: str = OUTPUT_PATH) -> None:
    df.to_csv(output_path, index=False)


def main() -> None:
    dataset = build_dataset(num_students=NUM_STUDENTS)
    save_dataset(dataset)
    print(f"Generated {len(dataset)} rows at {OUTPUT_PATH}")
    print_label_distribution(dataset)


if __name__ == "__main__":
    main()
