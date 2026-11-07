with open('tests/test_audit_fixes.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''    def test_attendance_pct_never_exceeds_100(self):
        """Fetch all students (admin scope) and assert every attendance_pct <= 100.0."""
        res = list_students(page=1, page_size=100, db=self.db, current_user=self.admin_user)
        students = res["students"]
        self.assertGreater(len(students), 0, "Seeded DB should contain students")
        for s in students:
            self.assertIsNotNone(s["attendance_pct"], f"{s['student_id']} returned None attendance_pct")
            self.assertLessEqual(
                s["attendance_pct"], 100.0,
                f"{s['student_id']} ({s['name']}) attendance_pct={s['attendance_pct']} exceeds 100",
            )'''

replacement = '''    def test_attendance_pct_never_exceeds_100(self):
        """Fetch all students (admin scope) and assert every attendance_pct <= 100.0."""
        res = list_students(page=1, page_size=100, db=self.db, current_user=self.admin_user)
        students = res["students"]
        self.assertGreater(len(students), 0, "Seeded DB should contain students")
        for s in students:
            self.assertIsNotNone(s["attendance_pct"], f"{s['student_id']} returned None attendance_pct")
            self.assertLessEqual(
                s["attendance_pct"], 100.0,
                f"{s['student_id']} ({s['name']}) attendance_pct={s['attendance_pct']} exceeds 100",
            )
            self.assertGreaterEqual(
                s["attendance_pct"], 0.0,
                f"{s['student_id']} ({s['name']}) attendance_pct={s['attendance_pct']} below 0",
            )

    def test_academic_record_attendance_pct_bounds(self):
        """Fetch academic-record for all active students and assert attendance_pct is strictly 0..100."""
        from app.routes.students import academic_record
        from app.models.student import Student

        active_students = self.db.query(Student).filter(Student.is_active == True).all()
        self.assertGreater(len(active_students), 0)
        for s in active_students:
            record = academic_record(s.student_id, db=self.db, current_user=self.admin_user)
            pct = record["student"]["attendance_pct"]
            self.assertIsNotNone(pct)
            self.assertGreaterEqual(pct, 0.0, f"{s.student_id} attendance_pct < 0: {pct}")
            self.assertLessEqual(pct, 100.0, f"{s.student_id} attendance_pct > 100: {pct}")'''

text_n = text.replace('\r\n', '\n')
target_n = target.replace('\r\n', '\n')
replacement_n = replacement.replace('\r\n', '\n')

assert target_n in text_n
text_n = text_n.replace(target_n, replacement_n, 1)
with open('tests/test_audit_fixes.py', 'w', encoding='utf-8') as f:
    f.write(text_n)
print('Updated test_audit_fixes.py successfully')
