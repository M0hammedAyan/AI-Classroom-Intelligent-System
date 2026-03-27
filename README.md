# ML Module - Student Risk Intelligence

This module provides end-to-end risk prediction for students using engineered academic and attendance features.

## What This Module Does

- Generates sample training data
- Builds interpretable engineered features
- Trains and calibrates classification models
- Predicts student risk score and risk level
- Explains predictions with prioritized reasons
- Produces actionable recommendations for teachers

## Folder Structure

- `data/sample/`: synthetic dataset generator and generated CSV
- `src/features/`: feature engineering
- `src/models/`: training and inference
- `src/explain/`: SHAP-based explanation layer
- `src/pipeline/`: final orchestrated output for one student
- `saved_models/`: trained model artifacts
- `test_pipeline.py`: integration test script

## Requirements

Install dependencies from project root:

```powershell
$PY = "d:/Major Project/AI-Classroom-Intelligent-System/.venv/Scripts/python.exe"
& $PY -m pip install -r "ml/requirements.txt"
```

Main dependencies:

- numpy
- pandas
- scikit-learn
- xgboost
- shap

## Quick Start (End-to-End)

Run from project root:

```powershell
$PY = "d:/Major Project/AI-Classroom-Intelligent-System/.venv/Scripts/python.exe"
& $PY "ml/data/sample/generate_sample_data.py"
& $PY "ml/src/models/train.py"
& $PY "ml/test_pipeline.py"
```

## One-Command Demo Prediction

```powershell
$PY = "d:/Major Project/AI-Classroom-Intelligent-System/.venv/Scripts/python.exe"
& $PY -c "import json; from ml.src.pipeline.pipeline import run_pipeline; sample={'student_id':'RUN_DEMO','overall_attendance':68,'recent_attendance':54,'avg_score':52,'recent_score':45,'failed_subjects':2,'previous_risk_score':0.2}; print(json.dumps(run_pipeline(sample), indent=2))"
```

## Input Contract (Pipeline)

`run_pipeline(student_json)` expects:

```json
{
  "student_id": "S123",
  "overall_attendance": 68,
  "recent_attendance": 54,
  "avg_score": 52,
  "recent_score": 45,
  "failed_subjects": 2,
  "previous_risk_score": 0.2
}
```

Notes:

- `previous_risk_score` is optional
- If omitted, `risk_change` returns `NO_PREVIOUS_DATA`

## Output Contract (Pipeline)

```json
{
  "student_id": "S123",
  "risk_score": 0.30,
  "risk_level": "MEDIUM",
  "confidence": 0.39,
  "reasons": [
    {"text": "Attendance below recommended level", "priority": 1},
    {"text": "Attendance worsening", "priority": 2}
  ],
  "recommended_actions": [
    "Schedule attendance counseling session",
    "Provide academic support and assign remedial work"
  ],
  "summary": "Student is at medium risk due to attendance below recommended level; schedule attendance counseling session.",
  "trend": "WORSENING",
  "risk_change": "RISK_STABLE",
  "validation_flags": []
}
```

## Risk and Confidence Logic

- Risk levels:
  - LOW: probability < 0.4
  - MEDIUM: 0.4 to < 0.7
  - HIGH: >= 0.7
- Confidence:
  - `confidence = abs(risk_score - 0.5) * 2`
  - Clamped to `[0, 1]`
  - Rounded to 2 decimals

## Main Scripts

- Train models and save best calibrated model:

```powershell
$PY = "d:/Major Project/AI-Classroom-Intelligent-System/.venv/Scripts/python.exe"
& $PY "ml/src/models/train.py"
```

- Run integration test:

```powershell
$PY = "d:/Major Project/AI-Classroom-Intelligent-System/.venv/Scripts/python.exe"
& $PY "ml/test_pipeline.py"
```

## Troubleshooting

- If imports fail, reinstall dependencies:

```powershell
$PY = "d:/Major Project/AI-Classroom-Intelligent-System/.venv/Scripts/python.exe"
& $PY -m pip install -r "ml/requirements.txt"
```

- If model file is missing, retrain:

```powershell
$PY = "d:/Major Project/AI-Classroom-Intelligent-System/.venv/Scripts/python.exe"
& $PY "ml/src/models/train.py"
```

- If outputs look stale, regenerate dataset and retrain:

```powershell
$PY = "d:/Major Project/AI-Classroom-Intelligent-System/.venv/Scripts/python.exe"
& $PY "ml/data/sample/generate_sample_data.py"
& $PY "ml/src/models/train.py"
```
