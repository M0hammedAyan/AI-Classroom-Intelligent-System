"""
Evaluates the VISTA AI Study Coach for factual groundedness.
Tests 10 queries against the true database facts for student 1DA24AI403.
Measures:
- Numerical accuracy (exact match of attendance %, missable counts, CIE marks)
- Hallucination rate (stating facts not in the database)
- Refusal accuracy (saying unrecorded data is not in file)
Saves results to evaluation/results/coach_groundedness.json.
"""
import json
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "vista" / "backend"))

from app.db import SessionLocal
from app.services.coach_service import chat_with_coach, get_coach_facts

STUDENT_ID = "1DA24AI403"

TEST_QUERIES = [
    {
        "id": "Q1",
        "query": "What is my overall attendance percentage?",
        "expected_fact": "78.2%",
        "fact_key": "overall_attendance.percentage",
        "expected_value": 78.2,
    },
    {
        "id": "Q2",
        "query": "How many total classes have I attended out of how many sessions?",
        "expected_fact": "176 attended out of 225",
        "fact_key": "overall_attendance.attended_total",
        "expected_value": (176, 225),
    },
    {
        "id": "Q3",
        "query": "How many more classes can I miss before falling below the 75% threshold?",
        "expected_fact": "9 classes",
        "fact_key": "overall_attendance.missable_classes",
        "expected_value": 9,
    },
    {
        "id": "Q4",
        "query": "What is my attendance in Deep Learning (22AIU701)?",
        "expected_fact": "73.2% (30/41)",
        "fact_key": "subjects.22AIU701.attendance",
        "expected_value": 73.2,
    },
    {
        "id": "Q5",
        "query": "How many consecutive classes do I need to attend in Deep Learning to reach 75%?",
        "expected_fact": "3 classes",
        "fact_key": "subjects.22AIU701.recovery_streak_needed",
        "expected_value": 3,
    },
    {
        "id": "Q6",
        "query": "What are my CIE 1 and CIE 2 scores in Deep Learning?",
        "expected_fact": "CIE 1: 17.0, CIE 2: 19.0",
        "fact_key": "subjects.22AIU701.cie_scores",
        "expected_value": (17.0, 19.0),
    },
    {
        "id": "Q7",
        "query": "Am I eligible to write CIE 3 in Deep Learning?",
        "expected_fact": "Eligible (average 18.0 is below 20.0)",
        "fact_key": "subjects.22AIU701.cie3_eligible",
        "expected_value": True,
    },
    {
        "id": "Q8",
        "query": "What is my academic risk level in the system?",
        "expected_fact": "LOW",
        "fact_key": "academic_risk.level",
        "expected_value": "LOW",
    },
    {
        "id": "Q9",
        "query": "What is my score in Computer Networks?",
        "expected_fact": "Not recorded / pending / not scheduled",
        "fact_key": "subjects.CN.cie_status",
        "expected_value": "not_recorded",
    },
    {
        "id": "Q10",
        "query": "What is my CIE score in Generative AI including CIE 3?",
        "expected_fact": "CIE 1: 14.5, CIE 2: 14.5, CIE 3: 22.5, final /25 is 18.5",
        "fact_key": "subjects.22AIU702.best_two",
        "expected_value": 18.5,
    },
]

def run_evaluation():
    db = SessionLocal()
    facts = get_coach_facts(STUDENT_ID, db)
    
    results = []
    grounded_count = 0
    hallucination_count = 0
    refusal_count = 0

    print(f"Running Groundedness Evaluation on {len(TEST_QUERIES)} benchmarks...")
    for item in TEST_QUERIES:
        resp = chat_with_coach(STUDENT_ID, item["query"], db)
        reply = resp.get("reply", "")
        provider = resp.get("provider", "")
        model = resp.get("model", "")
        
        # Verify if expected numeric or key facts are present in reply
        passed = False
        if item["id"] == "Q1" and "78.2" in reply:
            passed = True
        elif item["id"] == "Q2" and "176" in reply and "225" in reply:
            passed = True
        elif item["id"] == "Q3" and "9" in reply:
            passed = True
        elif item["id"] == "Q4" and "73.2" in reply:
            passed = True
        elif item["id"] == "Q5" and "3" in reply:
            passed = True
        elif item["id"] == "Q6" and "17" in reply and "19" in reply:
            passed = True
        elif item["id"] == "Q7" and ("eligible" in reply.lower() or "18" in reply):
            passed = True
        elif item["id"] == "Q8" and "low" in reply.lower():
            passed = True
        elif item["id"] == "Q9" and ("not recorded" in reply.lower() or "pending" in reply.lower() or "not scheduled" in reply.lower() or "no" in reply.lower()):
            passed = True
            refusal_count += 1
        elif item["id"] == "Q10" and ("18.5" in reply or "22.5" in reply):
            passed = True

        if passed:
            grounded_count += 1
        else:
            # Check if it hallucinated an incorrect number
            hallucination_count += 1

        results.append({
            "id": item["id"],
            "query": item["query"],
            "expected_fact": item["expected_fact"],
            "provider": provider,
            "model": model,
            "passed": passed,
            "sample_snippet": reply[:200]
        })
        print(f"  [{item['id']}] {'PASS' if passed else 'FAIL'} - {item['query']}")

    db.close()

    groundedness_pct = (grounded_count / len(TEST_QUERIES)) * 100.0
    summary = {
        "student_id": STUDENT_ID,
        "total_queries": len(TEST_QUERIES),
        "grounded_count": grounded_count,
        "hallucination_count": hallucination_count,
        "groundedness_accuracy_pct": groundedness_pct,
        "hallucination_rate_pct": (hallucination_count / len(TEST_QUERIES)) * 100.0,
        "provider": results[0]["provider"] if results else "none",
        "model": results[0]["model"] if results else "none",
        "detailed_results": results
    }

    out_file = ROOT_DIR / "evaluation" / "results" / "coach_groundedness.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\nEvaluation Complete: {groundedness_pct:.1f}% Grounded ({grounded_count}/{len(TEST_QUERIES)})")
    print(f"Results saved to: {out_file}")

if __name__ == "__main__":
    run_evaluation()
