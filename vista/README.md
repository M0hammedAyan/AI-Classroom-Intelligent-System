# VISTA — AI Classroom Intelligent System

End-to-end student risk prediction, face-recognition attendance, and teacher dashboard.

## Module Overview

| Folder | Purpose |
|---|---|
| `vision/` | Face detection, embedding, matching, liveness, recognition |
| `backend/` | FastAPI app — auth, attendance, students, risk routes |
| `frontend/` | React dashboard — login, attendance log, risk flags |
| `ml/` | Risk engine: feature engineering, prediction, SHAP explanation |
| `docs/` | API contract, DB schema, integration log |

## ML Quick Start

Install dependencies:

```powershell
pip install numpy pandas scikit-learn xgboost shap
```

Generate training data, train, and test from the project root:

```powershell
python ml/data/generate_sample_data.py
python -m ml.train
python -m ml.test_risk_engine
```

One-shot prediction demo:

```python
from ml.risk_engine import run_pipeline
import json

result = run_pipeline({
    "student_id": "S001",
    "overall_attendance": 68,
    "recent_attendance": 54,
    "avg_score": 52,
    "recent_score": 45,
    "failed_subjects": 2,
})
print(json.dumps(result, indent=2))
```

## Risk Levels

| Level | Score range |
|---|---|
| LOW | < 0.4 |
| MEDIUM | 0.4 – 0.7 |
| HIGH | ≥ 0.7 |

Confidence: `abs(risk_score - 0.5) * 2`, clamped to `[0, 1]`.

## Pipeline Output Schema

```json
{
  "student_id": "S001",
  "risk_score": 0.61,
  "risk_level": "MEDIUM",
  "confidence": 0.22,
  "reasons": [
    {"text": "Attendance below recommended level", "priority": 1},
    {"text": "Attendance worsening", "priority": 2}
  ],
  "recommended_actions": [
    "Schedule attendance counseling session",
    "Monitor student progress weekly"
  ],
  "summary": "Student is at medium risk due to attendance below recommended level; schedule attendance counseling session.",
  "trend": "WORSENING",
  "risk_change": "NO_PREVIOUS_DATA",
  "validation_flags": []
}
```
