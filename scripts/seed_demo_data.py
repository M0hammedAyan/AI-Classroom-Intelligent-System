"""
VISTA — Demo Attendance and CIE Marks Seeding Script
=====================================================
Generates realistic 3-month attendance and CIE marks for all students in the
4th Year AIML class (Semester 7) across all 5 active subjects from 03-Aug-2026
to 31-Oct-2026.

RULES & SPECIFICATIONS:
- Follows the official 7th-sem weekly timetable pattern (Tue-Fri theory sessions).
- Monday is lab-only (skipped). Weekends are skipped.
- Real face-recognition sessions (e.g., 2026-10-30 for Deep Learning) are STRICTLY PRESERVED and skipped.
- Attendance rates have a realistic distribution (55% to 98%), with selected students below 75% for risk modeling.
- Generates CIE 1 and CIE 2 (out of 25) with integer or half marks (none < 0, none > 25).
- Every seeded row has source='seed'.
- Idempotent (deterministic seed: 42).
- --undo option removes ONLY rows with source='seed'.
- Automatically recomputes student risk flags after seeding.

WARNING:
Seeded values are SYNTHETIC DEMO DATA and must be described as such in reports.
"""

import sys
import os
import argparse
import random
import uuid
import json
from datetime import date, timedelta, datetime, timezone

# Add backend directory and root directory to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_dir = os.path.join(root_dir, "vista", "backend")
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.db import SessionLocal, engine
from app.models.student import Student, Classroom
from app.models.organization import ClassSection, Subject, TeacherSubjectAssignment
from app.models.attendance import Attendance, Score, RiskFlag
from app.models.user import User

# Subject Code Mapping
SUBJECT_CODES = {
    "DL": "22AIU701",
    "GAI": "22AIU702",
    "DEA": "22AIT703",
    "DSP": "22AIT704C",
    "Project": "22AIP706",
}

# Weekly timetable theory pattern
# Tue: DL, GAI, DSP, DEA, Project
# Wed: GAI, DSP, DEA, Project (IDE skipped)
# Thu: DEA, DSP, DL, GAI (IDE skipped)
# Fri: DSP, DEA, DL, Project (IDE skipped)
TIMETABLE_PATTERN = {
    1: ["DL", "GAI", "DSP", "DEA", "Project"],        # Tuesday (weekday 1)
    2: ["GAI", "DSP", "DEA", "Project"],               # Wednesday (weekday 2)
    3: ["DEA", "DSP", "DL", "GAI"],                    # Thursday (weekday 3)
    4: ["DSP", "DEA", "DL", "Project"],                # Friday (weekday 4)
}

def undo_seed(db):
    print("=" * 65)
    print("UNDO SEED: Removing synthetic rows with source='seed'...")
    att_deleted = db.query(Attendance).filter(Attendance.source == "seed").delete(synchronize_session=False)
    scores_deleted = db.query(Score).filter(Score.source == "seed").delete(synchronize_session=False)
    db.commit()
    print(f"Deleted {att_deleted} seeded attendance records.")
    print(f"Deleted {scores_deleted} seeded score records.")
    print("Real face-recognition records and manual overrides remain intact.")
    print("=" * 65)

def run_seed():
    parser = argparse.ArgumentParser(description="Seed 3 months of demo attendance and CIE marks.")
    parser.add_argument("--undo", action="store_true", help="Remove all seeded demo records (source='seed').")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.undo:
            undo_seed(db)
            return

        print("=" * 65)
        print("WARNING: Seeded values are SYNTHETIC DEMO DATA for academic demonstration.")
        print("Real face recognition attendance records are preserved and never overwritten.")
        print("=" * 65)

        random.seed(42)

        # 1. Fetch 4th Year AIML class section & active subjects
        class_section = db.query(ClassSection).filter(
            (ClassSection.id == "class-aiml-4a") | (ClassSection.code == "AIML-4A") | (ClassSection.name == "4th Year AIML")
        ).first()

        if not class_section:
            print("ERROR: Class section '4th Year AIML' not found. Run setup_7th_sem_subjects.py first.")
            return

        subjects = db.query(Subject).filter(Subject.is_active == True).all()
        subj_by_code = {s.code: s for s in subjects}

        for short_code, full_code in SUBJECT_CODES.items():
            if full_code not in subj_by_code:
                print(f"ERROR: Missing subject {full_code} ({short_code}) in database.")
                return

        # 2. Fetch all students in 4th Year AIML
        students = db.query(Student).filter(
            (Student.class_ == "4th Year AIML") | (Student.classroom_id == "class-aiml-4a") | (Student.classroom_id == "class-ai-2022")
        ).all()

        if not students:
            print("ERROR: No students found in 4th Year AIML.")
            return

        print(f"Seeding attendance and CIE marks for {len(students)} students across 5 subjects...")

        # Assign realistic baseline attendance rates per student
        # Spread from 58% to 98%, with ~6 students under 75% for early risk alerts
        student_baselines = {}
        sorted_students = sorted(students, key=lambda s: s.student_id)
        for idx, s in enumerate(sorted_students):
            if idx in (3, 7, 14, 28, 45, 58):
                # At-risk students (< 75%)
                rate = round(random.uniform(0.55, 0.72), 2)
            elif idx % 5 == 0:
                # Moderate attendance (75% - 82%)
                rate = round(random.uniform(0.75, 0.82), 2)
            else:
                # Good to high attendance (83% - 98%)
                rate = round(random.uniform(0.83, 0.98), 2)
            student_baselines[s.student_id] = rate

        # Identify existing real records to NEVER overwrite
        existing_real_sessions = set()
        real_records = db.query(Attendance).filter(Attendance.source.in_(["face", "manual"])).all()
        for r in real_records:
            existing_real_sessions.add((r.student_id, r.session_date, r.subject_id))

        # Check existing seeded rows to guarantee idempotency
        existing_seeded = set()
        for r in db.query(Attendance.student_id, Attendance.session_date, Attendance.subject_id).filter(Attendance.source == "seed").all():
            existing_seeded.add((r[0], r[1], r[2]))

        # Generate attendance dates: 2026-08-03 to 2026-10-31
        start_date = date(2026, 8, 3)
        end_date = date(2026, 10, 31)
        cur_date = start_date

        new_att_records = []
        now_iso = datetime.now(timezone.utc).isoformat()

        session_count = 0
        while cur_date <= end_date:
            weekday = cur_date.weekday() # 0=Mon, 1=Tue, ..., 4=Fri, 5=Sat, 6=Sun
            if weekday in TIMETABLE_PATTERN:
                daily_subjects = TIMETABLE_PATTERN[weekday]
                date_str = cur_date.isoformat()

                for short_code in daily_subjects:
                    subject_code = SUBJECT_CODES[short_code]
                    subject_obj = subj_by_code[subject_code]
                    session_count += 1

                    for student in students:
                        key = (student.student_id, date_str, subject_obj.id)
                        code_key = (student.student_id, date_str, subject_obj.code)

                        # Skip if real face attendance exists
                        if key in existing_real_sessions or code_key in existing_real_sessions:
                            continue

                        # Skip if already seeded (idempotency)
                        if key in existing_seeded or code_key in existing_seeded:
                            continue

                        base_rate = student_baselines[student.student_id]
                        # Add session-level noise +/- 5%
                        is_present = random.random() < base_rate
                        status = "present" if is_present else "absent"

                        # Deterministic UUID from student + date + subject
                        rec_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{student.student_id}_{date_str}_{subject_obj.id}"))

                        new_att_records.append(Attendance(
                            id=rec_id,
                            student_id=student.student_id,
                            classroom_id=student.classroom_id,
                            subject_id=subject_obj.id,
                            session_date=date_str,
                            timestamp=f"{date_str}T09:30:00+00:00",
                            status=status,
                            confidence=round(random.uniform(0.70, 0.98), 2) if is_present else None,
                            is_manual_override=False,
                            source="seed",
                            created_at=now_iso,
                        ))

            cur_date += timedelta(days=1)

        if new_att_records:
            db.bulk_save_objects(new_att_records)
            db.commit()
            print(f"Seeded {len(new_att_records)} attendance records (source='seed').")
        else:
            print("Attendance records are already seeded (idempotent no-op).")

        # 3. Generate CIE 1 and CIE 2 Marks
        # CIE 1 Date: 2026-09-18
        # CIE 2 Date: 2026-10-23
        cie_assessments = [
            ("CIE 1", "2026-09-18"),
            ("CIE 2", "2026-10-23"),
        ]

        existing_scores = set()
        for s in db.query(Score.student_id, Score.subject, Score.assessment_type).filter(Score.source == "seed").all():
            existing_scores.add((s[0], s[1], s[2]))

        new_scores = []
        for assessment_type, cie_date in cie_assessments:
            for s in students:
                # Student baseline academic aptitude (correlated with attendance but with variance)
                base_pct = student_baselines[s.student_id]

                for subject_code in SUBJECT_CODES.values():
                    subj = subj_by_code[subject_code]
                    score_key = (s.student_id, subj.name, assessment_type)
                    if score_key in existing_scores:
                        continue

                    # CIE max marks = 25
                    # Mean marks around 17-18, spread mostly between 12 and 24, a few lower
                    raw_score = (base_pct * 22) + random.uniform(-4.0, 3.5)
                    # Round to nearest 0.5 mark
                    clamped_score = round(max(0.0, min(25.0, raw_score)) * 2) / 2

                    rec_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{s.student_id}_{subj.id}_{assessment_type}"))

                    new_scores.append(Score(
                        id=rec_id,
                        student_id=s.student_id,
                        subject=subj.name,
                        assessment_type=assessment_type,
                        score=clamped_score,
                        max_score=25.0,
                        date=cie_date,
                        source="seed",
                        created_at=now_iso,
                    ))

        if new_scores:
            db.bulk_save_objects(new_scores)
            db.commit()
            print(f"Seeded {len(new_scores)} CIE marks records (source='seed').")
        else:
            print("CIE marks are already seeded (idempotent no-op).")

        # 4. Recompute Risk for all students
        print("Recomputing risk flags for all students with new attendance and scores...")
        try:
            from app.routes.risk import recompute_all_risk
            class DummyAdmin:
                id = "admin-seed"
            res = recompute_all_risk(db=db, _admin=DummyAdmin())
            print(f"Successfully recomputed risk for {res.get('recomputed', 0)} students.")
        except Exception as e:
            print(f"Warning: Risk engine recompute note: {e}")

        print("=" * 65)
        print("SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 65)

    finally:
        db.close()

if __name__ == "__main__":
    run_seed()
