import sqlite3

conn = sqlite3.connect('vista/backend/vista_dev.db')
c = conn.cursor()

print("=== CLASS SECTIONS ===")
c.execute("SELECT * FROM class_sections")
for r in c.fetchall():
    print(r)

print("\n=== CLASSROOMS ===")
c.execute("SELECT * FROM classrooms")
for r in c.fetchall():
    print(r)

print("\n=== TEACHER SUBJECT ASSIGNMENTS ===")
c.execute("""
    SELECT tsa.id, tsa.teacher_id, tsa.subject_id, s.name, s.code, tsa.class_section_id, tsa.is_active
    FROM teacher_subjects tsa
    JOIN subjects s ON s.id = tsa.subject_id
""")
for r in c.fetchall():
    print(r)
