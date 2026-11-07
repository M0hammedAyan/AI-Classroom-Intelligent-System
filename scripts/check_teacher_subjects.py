import sys
sys.path.insert(0, 'vista/backend')
from app.db import SessionLocal
from app.models.user import User
from app.routes.admin import teacher_get_subjects

db = SessionLocal()
teachers = db.query(User).filter(User.role == 'teacher').all()
for t in teachers:
    try:
        res = teacher_get_subjects(db=db, current_user=t)
        sub_list = res.get("subjects", [])
        print(f"Teacher: {t.name} ({t.email}) -> {len(sub_list)} subjects")
        for s in sub_list:
            print(f"   {s['subject_name']} ({s['subject_code']}) - class_section: '{s['class_section']}' - {s['student_count']} students")
    except Exception as e:
        print(f"Teacher: {t.name} ({t.email}) ERROR: {e}")
