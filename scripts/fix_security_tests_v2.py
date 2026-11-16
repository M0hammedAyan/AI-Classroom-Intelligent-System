"""Fix security test Student fixtures — add required NOT NULL fields."""
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

NOW = "2026-01-01T00:00:00Z"

with open('tests/test_security_part5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all Student inserts to include class_ and created_at
fixes = [
    # POLICY001
    (
        'db.add(Student(student_id="POLICY001", name="Policy Student", class_="AIML-4A",\n'
        '                           classroom_id="class-aiml-4a", is_active=True,\n'
        '                           enrolled_at="2026-01-01"))',
        'db.add(Student(student_id="POLICY001", name="Policy Student", class_="AIML-4A",\n'
        '                           classroom_id="class-aiml-4a", is_active=True,\n'
        '                           enrolled_at="2026-01-01", created_at="2026-01-01T00:00:00Z"))',
    ),
    # POLICY002
    (
        'db.add(Student(student_id="POLICY002", name="Other Student", class_="AIML-3A",\n'
        '                           classroom_id="class-other-999", is_active=True,\n'
        '                           enrolled_at="2026-01-01"))',
        'db.add(Student(student_id="POLICY002", name="Other Student", class_="AIML-3A",\n'
        '                           classroom_id="class-other-999", is_active=True,\n'
        '                           enrolled_at="2026-01-01", created_at="2026-01-01T00:00:00Z"))',
    ),
    # IDOR_A001
    (
        'db.add(Student(student_id="IDOR_A001", name="IDOR A", class_="AIML-4A", classroom_id="class-aiml-4a",\n'
        '                           is_active=True, enrolled_at="2026-01-01"))',
        'db.add(Student(student_id="IDOR_A001", name="IDOR A", class_="AIML-4A", classroom_id="class-aiml-4a",\n'
        '                           is_active=True, enrolled_at="2026-01-01", created_at="2026-01-01T00:00:00Z"))',
    ),
    # IDOR_B002
    (
        'db.add(Student(student_id="IDOR_B002", name="IDOR B", class_="AIML-4A", classroom_id="class-aiml-4a",\n'
        '                           is_active=True, enrolled_at="2026-01-01"))',
        'db.add(Student(student_id="IDOR_B002", name="IDOR B", class_="AIML-4A", classroom_id="class-aiml-4a",\n'
        '                           is_active=True, enrolled_at="2026-01-01", created_at="2026-01-01T00:00:00Z"))',
    ),
]

for old, new in fixes:
    if old in content:
        content = content.replace(old, new)
        print('Fixed:', old[:70].replace('\n', ' '))
    else:
        print('NOT FOUND:', old[:70].replace('\n', ' '))

with open('tests/test_security_part5.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
