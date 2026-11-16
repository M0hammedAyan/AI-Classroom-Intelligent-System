import sqlite3

conn = sqlite3.connect('vista/backend/vista_dev.db')
c = conn.cursor()

# Get all students
c.execute("SELECT student_id, name, class, classroom_id FROM students WHERE is_active=1")
students = c.fetchall()
print(f"Total active students: {len(students)}")

# For each student, get counts
stats = []
exact_100 = []
exact_0 = []
for sid, name, cls, crid in students:
    c.execute("""
        SELECT 
            COUNT(*) as total_rows,
            SUM(CASE WHEN status='present' THEN 1 ELSE 0 END) as present_rows,
            SUM(CASE WHEN status='absent' THEN 1 ELSE 0 END) as absent_rows,
            SUM(CASE WHEN status='liveness_failed' THEN 1 ELSE 0 END) as liveness_rows,
            COUNT(DISTINCT session_date || '_' || COALESCE(subject_id, '')) as distinct_sessions
        FROM attendance
        WHERE student_id = ?
    """, (sid,))
    tot, pres, ab, live, dist = c.fetchone()
    pres = pres or 0
    ab = ab or 0
    live = live or 0
    pct = round((pres / tot) * 100, 1) if tot > 0 else 0.0
    stats.append((sid, name, tot, pres, ab, live, dist, pct))
    if pct == 100.0:
        exact_100.append((sid, name, tot, pres))
    elif pct == 0.0:
        exact_0.append((sid, name, tot, pres))

print(f"\nStudents with exactly 100% attendance: {len(exact_100)}")
for s in exact_100:
    print(f"  {s[0]} ({s[1]}): present={s[3]}/{s[2]}")

print(f"\nStudents with exactly 0% attendance: {len(exact_0)}")
for s in exact_0:
    print(f"  {s[0]} ({s[1]}): present={s[3]}/{s[2]}")

# Pick 2 students with interesting/realistic numbers to verify by hand:
# e.g., one typical student and one high/low
candidates = [s for s in stats if 40.0 <= s[7] <= 90.0]
print("\nSample 2 students with intermediate attendance for manual verification:")
for s in candidates[:2]:
    print(f"  ID: {s[0]}, Name: {s[1]}, Total: {s[2]}, Present: {s[3]}, Absent: {s[4]}, LivenessFailed: {s[5]}, DistSessions: {s[6]}, Pct: {s[7]}%")

    # Per-subject breakdown for this student
    c.execute("""
        SELECT 
            COALESCE(s.code, a.subject_id) as subj,
            COUNT(*) as total,
            SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) as pres
        FROM attendance a
        LEFT JOIN subjects s ON a.subject_id = s.id OR a.subject_id = s.code
        WHERE a.student_id = ?
        GROUP BY subj
    """, (s[0],))
    print("    Breakdown by subject:")
    for subj_code, sub_tot, sub_pres in c.fetchall():
        sub_pct = round(sub_pres / sub_tot * 100, 1) if sub_tot > 0 else 0.0
        print(f"      {subj_code}: {sub_pres}/{sub_tot} = {sub_pct}%")
