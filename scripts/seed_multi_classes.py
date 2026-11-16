"""
Seed script to add:
1. 3rd Year AIML (class-aiml-3a, AIML-3A) and 2nd Year AIML (class-aiml-2a, AIML-2A)
2. Mock students for AIML-3A and AIML-2A
3. Subject assignments for Demo Teacher and faculty
4. Complete weekly timetable slots for Demo Teacher and all teachers (Mon-Fri S1-S7)
5. Timetable slots for AIML-3A and AIML-2A
"""
import uuid
from datetime import datetime, timezone
from vista.backend.app.db import SessionLocal
from vista.backend.app.models.organization import ClassSection, Subject, TeacherSubjectAssignment
from vista.backend.app.models.student import Student
from vista.backend.app.models.timetable import TimetableSlot
from vista.backend.app.models.user import User

def run_seed():
    db = SessionLocal()
    now = datetime.now(timezone.utc).isoformat()
    print("Starting multi-class & teacher timetable seeding...")

    # 1. Classes
    c3 = db.query(ClassSection).filter(ClassSection.id == "class-aiml-3a").first()
    if not c3:
        c3 = ClassSection(
            id="class-aiml-3a",
            department_id="dept-aiml",
            name="3rd Year AIML",
            code="AIML-3A",
            semester="5",
            is_active=True,
            created_at=now,
        )
        db.add(c3)
        print("Created class-aiml-3a")

    c2 = db.query(ClassSection).filter(ClassSection.id == "class-aiml-2a").first()
    if not c2:
        c2 = ClassSection(
            id="class-aiml-2a",
            department_id="dept-aiml",
            name="2nd Year AIML",
            code="AIML-2A",
            semester="3",
            is_active=True,
            created_at=now,
        )
        db.add(c2)
        print("Created class-aiml-2a")

    db.commit()

    # 2. Demo Teacher & Faculty Subject Assignments
    demo_teacher = db.query(User).filter(User.email == "teacher@vista.local").first()
    kushal = db.query(User).filter(User.email == "kushal@vista.local").first()

    dl_subj = db.query(Subject).filter(Subject.code == "22AIU701").first()
    ml_subj = db.query(Subject).filter(Subject.code == "ML101").first()
    dbms_subj = db.query(Subject).filter(Subject.code == "DBMS").first()
    cn_subj = db.query(Subject).filter(Subject.code == "CN").first()
    os_subj = db.query(Subject).filter(Subject.code == "OS").first()
    se_subj = db.query(Subject).filter(Subject.code == "SE").first()

    def ensure_assignment(teacher_id, subject_id, class_section_id):
        if not teacher_id or not subject_id:
            return
        existing = db.query(TeacherSubjectAssignment).filter(
            TeacherSubjectAssignment.teacher_id == teacher_id,
            TeacherSubjectAssignment.subject_id == subject_id,
            TeacherSubjectAssignment.class_section_id == class_section_id,
        ).first()
        if not existing:
            db.add(TeacherSubjectAssignment(
                id=str(uuid.uuid4()),
                teacher_id=teacher_id,
                subject_id=subject_id,
                class_section_id=class_section_id,
                is_active=True,
                assigned_at=now,
            ))

    if demo_teacher:
        ensure_assignment(demo_teacher.id, dl_subj.id if dl_subj else None, "class-aiml-4a")
        ensure_assignment(demo_teacher.id, ml_subj.id if ml_subj else None, "class-aiml-3a")
        ensure_assignment(demo_teacher.id, dbms_subj.id if dbms_subj else None, "class-aiml-3a")

    if kushal:
        ensure_assignment(kushal.id, cn_subj.id if cn_subj else None, "class-aiml-3a")
        ensure_assignment(kushal.id, os_subj.id if os_subj else None, "class-aiml-2a")
        ensure_assignment(kushal.id, se_subj.id if se_subj else None, "class-aiml-2a")

    db.commit()

    # 3. Mock Students for AIML-3A & AIML-2A
    existing_3a_count = db.query(Student).filter(Student.classroom_id == "class-aiml-3a").count()
    if existing_3a_count == 0:
        students_3a = [
            ("1DA22AI001", "Aarav Sharma", "B1"),
            ("1DA22AI002", "Ananya Iyer", "B1"),
            ("1DA22AI003", "Chirag Hegde", "B1"),
            ("1DA22AI004", "Deepika Rao", "B1"),
            ("1DA22AI005", "Gautam Nair", "B1"),
            ("1DA22AI006", "Harini K", "B2"),
            ("1DA22AI007", "Ishaan Roy", "B2"),
            ("1DA22AI008", "Kavya Patel", "B2"),
            ("1DA22AI009", "Manish V", "B2"),
            ("1DA22AI010", "Neha Pillai", "B2"),
            ("1DA22AI011", "Pranav Deshmukh", "B2"),
            ("1DA22AI012", "Rhea Sengupta", "B2"),
        ]
        for usn, name, batch in students_3a:
            db.add(Student(
                student_id=usn,
                name=name,
                classroom_id="class-aiml-3a",
                class_="3rd Year AIML",
                batch=batch,
                is_active=True,
                created_at=now,
            ))
        print("Added 12 students to class-aiml-3a")

    existing_2a_count = db.query(Student).filter(Student.classroom_id == "class-aiml-2a").count()
    if existing_2a_count == 0:
        students_2a = [
            ("1DA23AI201", "Aditya Kulkarni", "B1"),
            ("1DA23AI202", "Bhavana Gowda", "B1"),
            ("1DA23AI203", "Darshan M", "B1"),
            ("1DA23AI204", "Esha Reddy", "B1"),
            ("1DA23AI205", "Faizan Ahmed", "B1"),
            ("1DA23AI206", "Janani S", "B2"),
            ("1DA23AI207", "Karthik Raja", "B2"),
            ("1DA23AI208", "Lavanya Joshi", "B2"),
            ("1DA23AI209", "Nikhil Bhat", "B2"),
            ("1DA23AI210", "Pooja Hegde", "B2"),
        ]
        for usn, name, batch in students_2a:
            db.add(Student(
                student_id=usn,
                name=name,
                classroom_id="class-aiml-2a",
                class_="2nd Year AIML",
                batch=batch,
                is_active=True,
                created_at=now,
            ))
        print("Added 10 students to class-aiml-2a")

    db.commit()

    # 4. Slots for Demo Teacher (across Monday-Friday)
    if demo_teacher:
        demo_slots_count = db.query(TimetableSlot).filter(TimetableSlot.teacher_id == demo_teacher.id).count()
        if demo_slots_count == 0:
            demo_slots = [
                # Mon S1 (09:00-10:00) DL in 4th Year AIML
                (0, "S1", "09:00", "10:00", "class-aiml-4a", dl_subj.id, "A-302", "teaching", None),
                # Mon S3 (11:15-12:15) ML in 3rd Year AIML
                (0, "S3", "11:15", "12:15", "class-aiml-3a", ml_subj.id, "B-201", "teaching", None),
                # Tue S2 (10:00-11:00) DL in 4th Year AIML
                (1, "S2", "10:00", "11:00", "class-aiml-4a", dl_subj.id, "A-302", "teaching", None),
                # Tue S5-S6 (14:00-16:00) ML Lab in 3rd Year AIML (Batch B1)
                (1, "S5", "14:00", "15:00", "class-aiml-3a", ml_subj.id, "CC-Lab 1", "lab", "B1"),
                (1, "S6", "15:00", "16:00", "class-aiml-3a", ml_subj.id, "CC-Lab 1", "lab", "B1"),
                # Wed S1 (09:00-10:00) DBMS in 3rd Year AIML
                (2, "S1", "09:00", "10:00", "class-aiml-3a", dbms_subj.id, "B-201", "teaching", None),
                # Wed S4 (12:15-13:15) DL Tutorial in 4th Year AIML
                (2, "S4", "12:15", "13:15", "class-aiml-4a", dl_subj.id, "A-302", "teaching", None),
                # Thu S3 (11:15-12:15) ML in 3rd Year AIML
                (3, "S3", "11:15", "12:15", "class-aiml-3a", ml_subj.id, "B-201", "teaching", None),
                # Thu S5-S6 (14:00-16:00) ML Lab in 3rd Year AIML (Batch B2)
                (3, "S5", "14:00", "15:00", "class-aiml-3a", ml_subj.id, "CC-Lab 1", "lab", "B2"),
                (3, "S6", "15:00", "16:00", "class-aiml-3a", ml_subj.id, "CC-Lab 1", "lab", "B2"),
                # Fri S2 (10:00-11:00) DBMS in 3rd Year AIML
                (4, "S2", "10:00", "11:00", "class-aiml-3a", dbms_subj.id, "B-201", "teaching", None),
                # Fri S6 (15:00-16:00) DL in 4th Year AIML
                (4, "S6", "15:00", "16:00", "class-aiml-4a", dl_subj.id, "A-302", "teaching", None),
            ]
            for dow, pl, st, et, cid, sid, room, stype, batch in demo_slots:
                db.add(TimetableSlot(
                    id=f"slot-{uuid.uuid4().hex[:8]}",
                    class_section_id=cid,
                    subject_id=sid,
                    teacher_id=demo_teacher.id,
                    day_of_week=dow,
                    start_time=st,
                    end_time=et,
                    room=room,
                    period_label=pl,
                    slot_type=stype,
                    batch=batch,
                    is_active=True,
                    is_unconfirmed=False,
                    created_at=now,
                ))
            print(f"Added {len(demo_slots)} timetable slots for Demo Teacher")

    # 5. Slots for Kushal in 3rd Year and 2nd Year
    if kushal:
        kushal_slots_count = db.query(TimetableSlot).filter(TimetableSlot.teacher_id == kushal.id, TimetableSlot.is_active == True).count()
        if kushal_slots_count == 0:
            kushal_slots = [
                # Mon S2 (10:00-11:00) CN in 3rd Year AIML
                (0, "S2", "10:00", "11:00", "class-aiml-3a", cn_subj.id, "B-201", "teaching", None),
                # Mon S4 (12:15-13:15) OS in 2nd Year AIML
                (0, "S4", "12:15", "13:15", "class-aiml-2a", os_subj.id, "C-101", "teaching", None),
                # Tue S3 (11:15-12:15) SE in 2nd Year AIML
                (1, "S3", "11:15", "12:15", "class-aiml-2a", se_subj.id, "C-101", "teaching", None),
                # Wed S2 (10:00-11:00) CN in 3rd Year AIML
                (2, "S2", "10:00", "11:00", "class-aiml-3a", cn_subj.id, "B-201", "teaching", None),
                # Thu S1 (09:00-10:00) OS in 2nd Year AIML
                (3, "S1", "09:00", "10:00", "class-aiml-2a", os_subj.id, "C-101", "teaching", None),
                # Fri S1 (09:00-10:00) SE in 2nd Year AIML
                (4, "S1", "09:00", "10:00", "class-aiml-2a", se_subj.id, "C-101", "teaching", None),
            ]
            for dow, pl, st, et, cid, sid, room, stype, batch in kushal_slots:
                db.add(TimetableSlot(
                    id=f"slot-{uuid.uuid4().hex[:8]}",
                    class_section_id=cid,
                    subject_id=sid,
                    teacher_id=kushal.id,
                    day_of_week=dow,
                    start_time=st,
                    end_time=et,
                    room=room,
                    period_label=pl,
                    slot_type=stype,
                    batch=batch,
                    is_active=True,
                    is_unconfirmed=False,
                    created_at=now,
                ))
            print(f"Added {len(kushal_slots)} timetable slots for Kushal")

    db.commit()
    db.close()
    print("Multi-class & teacher timetable seeding completed successfully!")

if __name__ == "__main__":
    run_seed()
