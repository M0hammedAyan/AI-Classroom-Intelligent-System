with open('vista/backend/app/routes/students.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix 1: row.score is None check in academic_record marks
t_old1 = '"percentage": round(row.score / row.max_score * 100, 1) if row.max_score else 0,'
t_new1 = '"percentage": round(row.score / row.max_score * 100, 1) if (row.max_score and row.score is not None) else 0,'

# Fix 2: attendance calculation in _student_dict (same sessions for numerator and denominator)
t_old2 = '''    attendance = db.query(Attendance).filter(Attendance.student_id == s.student_id).all()
    session_dates = {row[0] for row in db.query(Attendance.session_date).filter(Attendance.classroom_id == s.classroom_id).distinct().all()}
    present = sum(1 for row in attendance if row.status == "present")
    scores = db.query(Score).filter(Score.student_id == s.student_id).all()
    percentages = [row.score / row.max_score * 100 for row in scores if row.max_score and row.score is not None]
    risk = db.query(RiskFlag).filter(RiskFlag.student_id == s.student_id).order_by(RiskFlag.calculated_at.desc()).first()
    result.update({
        "attendance_pct": min(100.0, round(present / len(session_dates) * 100, 1)) if session_dates else 0,'''

t_new2 = '''    attendance = db.query(Attendance).filter(Attendance.student_id == s.student_id).all()
    total_sessions = len(attendance)
    present = sum(1 for row in attendance if row.status == "present")
    scores = db.query(Score).filter(Score.student_id == s.student_id).all()
    percentages = [row.score / row.max_score * 100 for row in scores if row.max_score and row.score is not None]
    risk = db.query(RiskFlag).filter(RiskFlag.student_id == s.student_id).order_by(RiskFlag.calculated_at.desc()).first()
    result.update({
        "attendance_pct": min(100.0, max(0.0, round(present / total_sessions * 100, 1))) if total_sessions > 0 else 0.0,'''

# Normalize newlines
text = text.replace('\r\n', '\n')
t_old2 = t_old2.replace('\r\n', '\n')
t_new2 = t_new2.replace('\r\n', '\n')

assert t_old1 in text, "t_old1 not found"
assert t_old2 in text, "t_old2 not found"

text = text.replace(t_old1, t_new1, 1)
text = text.replace(t_old2, t_new2, 1)

with open('vista/backend/app/routes/students.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Applied fix successfully to students.py")
