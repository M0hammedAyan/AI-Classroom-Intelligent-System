import sqlite3
import os
import uuid
from datetime import datetime, timezone

def setup_subjects_and_class(db_path: str):
    if not os.path.exists(db_path):
        return

    print(f"Setting up 7th sem subjects & class in {db_path}...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    # 1. Ensure department dept-aiml exists
    dept = cur.execute("SELECT id FROM departments WHERE id = 'dept-aiml'").fetchone()
    if not dept:
        cur.execute(
            "INSERT INTO departments (id, school_id, name, code, is_active, created_at) VALUES ('dept-aiml', 'school-cse', 'Artificial Intelligence and Machine Learning', 'AIML', 1, ?)",
            (now,)
        )

    # 2. Rename/Upsert Classroom 'class-aiml-4a' and 'class-ai-2022'
    cur.execute("INSERT OR REPLACE INTO classrooms (classroom_id, name) VALUES ('class-aiml-4a', '4th Year AIML')")
    cur.execute("INSERT OR REPLACE INTO classrooms (classroom_id, name) VALUES ('class-ai-2022', '4th Year AIML')")

    # 3. Rename ClassSection to '4th Year AIML' (Semester 7, code AIML-4A)
    cs = cur.execute("SELECT id FROM class_sections WHERE id = 'class-aiml-4a'").fetchone()
    if cs:
        cur.execute(
            "UPDATE class_sections SET name = '4th Year AIML', code = 'AIML-4A', semester = '7', is_active = 1 WHERE id = 'class-aiml-4a'"
        )
    else:
        cur.execute(
            "INSERT INTO class_sections (id, department_id, name, code, semester, is_active, created_at) VALUES ('class-aiml-4a', 'dept-aiml', '4th Year AIML', 'AIML-4A', '7', 1, ?)",
            (now,)
        )

    # 4. Update the 66 students in students table to class='4th Year AIML', classroom_id='class-aiml-4a'
    cur.execute(
        "UPDATE students SET class = '4th Year AIML', classroom_id = 'class-aiml-4a' WHERE class IN ('AIML-3A', 'AIML 3rd Year', '3rd Year A', '3rd Year') OR classroom_id = 'class-ai-2022'"
    )
    updated_students = cur.rowcount
    print(f"  Updated {updated_students} student records to '4th Year AIML' and 'class-aiml-4a'.")

    # 5. Archive old/inactive subjects (Data Structures)
    cur.execute("UPDATE subjects SET is_active = 0 WHERE code IN ('DSA', '402', 'CS301') OR name LIKE '%Data Structures%'")
    cur.execute("UPDATE teacher_subjects SET is_active = 0 WHERE subject_id IN (SELECT id FROM subjects WHERE is_active = 0)")

    # 6. Verify / match faculty users
    faculty_map = {
        "Mrs. Rajeshwari": "rajeshwari@vista.local",
        "Dr. Ajay Prakash B V": "ajayprakash@vista.local",
        "Mr. Ganesh H J": "ganesh@vista.local",
        "Mr. Bharath V S": "bharat@vista.local",
    }
    faculty_ids = {}
    for name, email in faculty_map.items():
        # Match by email or name substring
        user = cur.execute("SELECT id FROM users WHERE email = ? OR name LIKE ? OR name LIKE ?", (email, f"%{name.split()[-1]}%", f"%{name.split()[1] if len(name.split()) > 1 else name}%")).fetchone()
        if user:
            faculty_ids[name] = user[0]
        else:
            # Create faculty record WITHOUT login credentials (password_hash = 'DISABLED_NO_LOGIN')
            user_id = str(uuid.uuid4())
            cur.execute(
                "INSERT INTO users (id, name, email, password_hash, role, school_id, department_id, is_active, created_at) VALUES (?, ?, ?, 'DISABLED_NO_LOGIN', 'teacher', 'school-cse', 'dept-aiml', 1, ?)",
                (user_id, name, email, now)
            )
            faculty_ids[name] = user_id
            print(f"  Created faculty record for {name} without login credentials.")

    # 7. Upsert the 5 7th-Semester Subjects
    subjects_spec = [
        ("subject-22aiu701", "22AIU701", "Deep Learning", 4.0, "Mrs. Rajeshwari"),
        ("subject-22aiu702", "22AIU702", "Generative AI", 4.0, "Dr. Ajay Prakash B V"),
        ("subject-22ait703", "22AIT703", "Data Engineering and Analytics", 4.0, "Mr. Ganesh H J"),
        ("subject-22ait704c", "22AIT704C", "Data Security and Privacy", 3.0, "Mr. Bharath V S"),
        ("subject-22aip706", "22AIP706", "Major Project Phase-II", 2.0, "Mr. Ganesh H J"),
    ]

    for subj_id, code, title, creds, teacher_key in subjects_spec:
        existing = cur.execute("SELECT id FROM subjects WHERE id = ? OR code = ?", (subj_id, code)).fetchone()
        if existing:
            cur.execute(
                "UPDATE subjects SET name = ?, code = ?, semester = '7', credits = ?, is_active = 1 WHERE id = ?",
                (title, code, creds, existing[0])
            )
            actual_id = existing[0]
        else:
            cur.execute(
                "INSERT INTO subjects (id, department_id, name, code, semester, credits, is_active, created_at) VALUES (?, 'dept-aiml', ?, ?, '7', ?, 1, ?)",
                (subj_id, title, code, creds, now)
            )
            actual_id = subj_id

        # Upsert teacher assignment to class-aiml-4a
        t_id = faculty_ids[teacher_key]
        assign_existing = cur.execute(
            "SELECT id FROM teacher_subjects WHERE subject_id = ? AND class_section_id = 'class-aiml-4a'",
            (actual_id,)
        ).fetchone()
        if assign_existing:
            cur.execute(
                "UPDATE teacher_subjects SET teacher_id = ?, is_active = 1 WHERE id = ?",
                (t_id, assign_existing[0])
            )
        else:
            cur.execute(
                "INSERT INTO teacher_subjects (id, teacher_id, subject_id, class_section_id, assigned_at, is_active) VALUES (?, ?, ?, 'class-aiml-4a', ?, 1)",
                (str(uuid.uuid4()), t_id, actual_id, now)
            )

    conn.commit()
    conn.close()
    print(f"Finished setting up subjects in {db_path}.")

if __name__ == "__main__":
    setup_subjects_and_class("d:/CipherTECH/Projects/AI-Classroom-Intelligent-System/vista_dev.db")
    setup_subjects_and_class("d:/CipherTECH/Projects/AI-Classroom-Intelligent-System/vista/backend/vista_dev.db")
