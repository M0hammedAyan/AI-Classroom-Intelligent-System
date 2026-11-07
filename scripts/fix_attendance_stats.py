with open('vista/backend/app/routes/attendance.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('\r\n', '\n')

old_code = '''    # Per-student summary
    student_summary = []
    for s in students:
        present = student_present.get(s.student_id, 0)
        pct = (present / total_sessions * 100) if total_sessions > 0 else 0
        student_summary.append({
            "student_id": s.student_id,
            "name": s.name,
            "sessions_attended": present,
            "total_sessions": total_sessions,
            "attendance_pct": round(pct, 1),
        })

    student_summary.sort(key=lambda x: x["attendance_pct"])

    # Overall
    total_expected = total_sessions * len(students)
    total_present = sum(student_present.values())
    overall_pct = (total_present / total_expected * 100) if total_expected > 0 else 0'''

new_code = '''    # Per-student summary
    student_sessions_count: dict[str, int] = defaultdict(int)
    for r in att_rows:
        if r.student_id:
            student_sessions_count[r.student_id] += 1

    student_summary = []
    for s in students:
        present = student_present.get(s.student_id, 0)
        s_total = student_sessions_count.get(s.student_id, 0)
        pct = (present / s_total * 100) if s_total > 0 else 0.0
        pct = min(100.0, max(0.0, round(pct, 1)))
        student_summary.append({
            "student_id": s.student_id,
            "name": s.name,
            "sessions_attended": present,
            "total_sessions": s_total,
            "attendance_pct": pct,
        })

    student_summary.sort(key=lambda x: x["attendance_pct"])

    # Overall
    total_expected = sum(student_sessions_count.values())
    total_present = sum(student_present.values())
    overall_pct = min(100.0, max(0.0, round((total_present / total_expected * 100), 1))) if total_expected > 0 else 0.0'''

assert old_code in text, "old_code not found in attendance.py"
text = text.replace(old_code, new_code, 1)

with open('vista/backend/app/routes/attendance.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Applied fix to attendance.py")
