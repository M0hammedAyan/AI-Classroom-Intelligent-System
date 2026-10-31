"""
VISTA — Centralized Continuous Internal Evaluation (CIE) Policy
================================================================
Institutional Assessment Rules (3 Tests Architecture):
- Each CIE is evaluated out of CIE_MAX = 25.0 marks.
- Regular tests: CIE 1 and CIE 2.
- Re-attempt / Improvement test: CIE 3.

Thresholds:
- CIE_MAX = 25.0
- CIE_ELIGIBILITY_AVG = 20.0

Rules:
1. Statuses: 'scored' | 'absent'.
   - Absent is stored with score = None (NULL marks).
   - Absent tests are NEVER counted as 0 in averages, trends, or risk calculations.
2. Eligibility for CIE 3:
   - Eligible if:
     a) Both CIE 1 and CIE 2 were attempted, and their average is < 20.0
     b) Exactly one of CIE 1 / CIE 2 was taken (absent for the other) to satisfy the 2-test requirement.
     c) Neither was taken (flagged incomplete: contact teacher).
   - NOT eligible if:
     Both CIE 1 and CIE 2 were attempted, and their average is >= 20.0.
3. Final CIE Mark:
   - If CIE 3 is not applicable / not taken: average of CIE 1 and CIE 2 (out of 25), and sum (out of 50).
   - If CIE 3 is taken: average of the BEST TWO scores available (out of 25), and sum of best two (out of 50).
   - Fewer than 2 attempted scores: final = None, status = 'incomplete'.
"""
from __future__ import annotations

from typing import Any
from sqlalchemy.orm import Session

# Centralized Policy Thresholds
CIE_MAX: float = 25.0
CIE_ELIGIBILITY_AVG: float = 20.0


def evaluate_cie(
    student_id: str | None = None,
    subject: str | None = None,
    db: Session | None = None,
    scores_records: list[Any] | None = None,
) -> dict[str, Any]:
    """
    Evaluate CIE performance for a student in a specific subject.
    Accepts either (student_id, subject, db) to query from database,
    or pre-fetched `scores_records` (list of Score models or dicts).
    """
    records = []
    if scores_records is not None:
        records = scores_records
    elif db is not None and student_id and subject:
        from .models.attendance import Score
        from .models.organization import Subject
        # Resolve subject name/code/id
        subj_row = db.query(Subject).filter(
            (Subject.id == subject) | (Subject.code == subject) | (Subject.name == subject)
        ).first()
        subj_name = subj_row.name if subj_row else subject
        subj_code = subj_row.code if subj_row else subject
        subj_id = subj_row.id if subj_row else subject

        records = (
            db.query(Score)
            .filter(
                Score.student_id == student_id,
                (Score.subject == subj_name) | (Score.subject == subj_code) | (Score.subject == subj_id),
            )
            .all()
        )

    # Map scores and statuses for CIE 1, CIE 2, CIE 3
    # Default state: None score, status 'not_scheduled'
    c1_score, c1_status = None, "not_scheduled"
    c2_score, c2_status = None, "not_scheduled"
    c3_score, c3_status = None, "not_scheduled"

    for r in records:
        # Support both ORM objects and dicts
        atype = getattr(r, "assessment_type", None) or (r.get("assessment_type") if isinstance(r, dict) else None)
        sub_name = getattr(r, "subject", "") or (r.get("subject", "") if isinstance(r, dict) else "")
        sc = getattr(r, "score", None) if not isinstance(r, dict) else r.get("score")
        st = getattr(r, "status", None) if not isinstance(r, dict) else r.get("status")

        # Normalize score and status
        if st == "absent" or sc is None:
            normalized_status = "absent"
            normalized_score = None
        else:
            try:
                normalized_score = float(sc)
                normalized_status = "scored"
            except (ValueError, TypeError):
                normalized_score = None
                normalized_status = "absent"

        atype_str = str(atype or "").upper()
        if "CIE 1" in atype_str or "CIE-1" in atype_str or "CIE 1" in sub_name.upper():
            c1_score = normalized_score
            c1_status = normalized_status
        elif "CIE 2" in atype_str or "CIE-2" in atype_str or "CIE 2" in sub_name.upper():
            c2_score = normalized_score
            c2_status = normalized_status
        elif "CIE 3" in atype_str or "CIE-3" in atype_str or "CIE 3" in sub_name.upper():
            c3_score = normalized_score
            c3_status = normalized_status

    scores = {"cie1": c1_score, "cie2": c2_score, "cie3": c3_score}
    statuses = {"cie1": c1_status, "cie2": c2_status, "cie3": c3_status}

    # Count attempted (scored) tests
    attempted_scores = [s for s in [c1_score, c2_score, c3_score] if s is not None]
    attempted_count = len(attempted_scores)

    # 1. Evaluate CIE 1 and CIE 2
    avg_1_2 = None
    cie3_eligible = False
    cie3_reason = ""

    c1_taken = c1_status == "scored" and c1_score is not None
    c2_taken = c2_status == "scored" and c2_score is not None
    c1_absent = c1_status == "absent"
    c2_absent = c2_status == "absent"

    if c1_taken and c2_taken:
        avg_1_2 = round((c1_score + c2_score) / 2.0, 2)
        if avg_1_2 < CIE_ELIGIBILITY_AVG:
            cie3_eligible = True
            cie3_reason = f"Average of CIE 1 and CIE 2 ({avg_1_2:.1f}/25) is below {CIE_ELIGIBILITY_AVG:.1f}. Eligible for improvement."
        else:
            cie3_eligible = False
            cie3_reason = f"Average of CIE 1 and CIE 2 ({avg_1_2:.1f}/25) meets benchmark (>={CIE_ELIGIBILITY_AVG:.1f}). Exempt from CIE 3."
    elif (c1_taken and not c2_taken) or (c2_taken and not c1_taken):
        cie3_eligible = True
        missed = "CIE 2" if c1_taken else "CIE 1"
        taken_score = c1_score if c1_taken else c2_score
        cie3_reason = f"Missed {missed}; re-attempt required to satisfy 2-assessment institutional minimum (Attempted score: {taken_score}/25)."
    elif (c1_absent or c1_status == "not_scheduled") and (c2_absent or c2_status == "not_scheduled"):
        if c1_absent and c2_absent:
            cie3_eligible = True
            cie3_reason = "Incomplete: Absent for both CIE 1 and CIE 2. Immediate instructor remediation required."
        else:
            cie3_eligible = False
            cie3_reason = "Assessments pending / not yet scheduled."

    # 2. Final CIE Score Calculation
    c3_taken = c3_status == "scored" and c3_score is not None
    best_two: list[float] = []
    final_out_of_25: float | None = None
    final_out_of_50: float | None = None
    status: str = "incomplete"

    if c3_taken:
        # Best two of all available scored attempts
        sorted_attempts = sorted(attempted_scores, reverse=True)
        if len(sorted_attempts) >= 2:
            best_two = sorted_attempts[:2]
            final_out_of_50 = round(sum(best_two), 1)
            final_out_of_25 = round(sum(best_two) / 2.0, 1)
            status = "completed"
        elif len(sorted_attempts) == 1:
            best_two = sorted_attempts
            status = "incomplete"
    elif c1_taken and c2_taken:
        # Standard CIE 1 and CIE 2 average
        best_two = sorted([c1_score, c2_score], reverse=True)
        final_out_of_50 = round(c1_score + c2_score, 1)
        final_out_of_25 = round((c1_score + c2_score) / 2.0, 1)
        status = "completed"
    else:
        status = "eligible" if cie3_eligible else "incomplete"

    return {
        "cie1": c1_score,
        "cie2": c2_score,
        "cie3": c3_score,
        "cie1_status": c1_status,
        "cie2_status": c2_status,
        "cie3_status": c3_status,
        "scores": scores,
        "statuses": statuses,
        "attempted_count": attempted_count,
        "average_cie1_cie2": avg_1_2,
        "cie3_eligible": cie3_eligible,
        "cie3_reason": cie3_reason,
        "best_two": best_two,
        "final_out_of_25": final_out_of_25,
        "final_out_of_50": final_out_of_50,
        "final_cie_25": final_out_of_25,
        "final_cie_50": final_out_of_50,
        "status": status,
    }


def calculate_cie2_needed_to_avoid_cie3(cie1_score: float | None) -> dict[str, Any]:
    """
    Computes required CIE 2 score to achieve average >= 20.0 and avoid CIE 3:
    Formula: required = 2 * CIE_ELIGIBILITY_AVG - CIE 1
    """
    if cie1_score is None:
        return {
            "needed": None,
            "is_reachable": False,
            "message": "CIE 1 score is not recorded or student was absent.",
        }

    needed = round(2 * CIE_ELIGIBILITY_AVG - cie1_score, 1)
    if needed <= 0.0:
        return {
            "needed": 0.0,
            "is_reachable": True,
            "message": f"With {cie1_score}/25 in CIE 1, your average is already secure.",
        }
    elif needed > CIE_MAX:
        return {
            "needed": needed,
            "is_reachable": False,
            "message": f"Need {needed}/25 in CIE 2 to reach a 20.0 average (exceeds maximum of {CIE_MAX}). You will need to take CIE 3.",
        }
    else:
        return {
            "needed": needed,
            "is_reachable": True,
            "message": f"Need at least {needed}/25 in CIE 2 to secure a 20.0 average and avoid CIE 3.",
        }
