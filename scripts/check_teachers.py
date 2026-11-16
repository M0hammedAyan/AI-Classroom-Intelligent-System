import sqlite3

conn = sqlite3.connect('vista/backend/vista_dev.db')
c = conn.cursor()

c.execute("SELECT id, name, email, role FROM users WHERE role='teacher'")
print("Teachers in users:")
for t in c.fetchall():
    print(" ", t)

c.execute("""
    SELECT tsa.id, u.name, s.code, s.name, tsa.class_section_id
    FROM teacher_subjects tsa
    LEFT JOIN users u ON tsa.teacher_id = u.id
    LEFT JOIN subjects s ON tsa.subject_id = s.id
""")
print("Teacher subject assignments:")
for row in c.fetchall():
    print(" ", row)

c.execute("SELECT id, code, name, semester, is_active FROM subjects")
print("Subjects in subjects table:")
for s in c.fetchall():
    print(" ", s)
