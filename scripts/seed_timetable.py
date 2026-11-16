import sqlite3
import uuid
from datetime import datetime, timezone

def make_subject_id_nullable(c):
    c.execute("PRAGMA foreign_keys=OFF")
    # Check if timetable_slots subject_id has NOT NULL
    c.execute("PRAGMA table_info(timetable_slots)")
    info = c.fetchall()
    # info: [(cid, name, type, notnull, dflt_value, pk), ...]
    subj_col = next((col for col in info if col[1] == 'subject_id'), None)
    if subj_col and subj_col[3] == 1:  # notnull == 1
        print("  Recreating timetable_slots to allow nullable subject_id...")
        c.execute("""
            CREATE TABLE timetable_slots_new (
                id TEXT PRIMARY KEY,
                class_section_id TEXT NOT NULL,
                subject_id TEXT,
                teacher_id TEXT,
                day_of_week INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                room TEXT,
                period_label TEXT,
                slot_type TEXT DEFAULT 'teaching',
                batch TEXT,
                is_unconfirmed BOOLEAN DEFAULT 0,
                effective_from TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TEXT NOT NULL
            )
        """)
        c.execute("""
            INSERT INTO timetable_slots_new (
                id, class_section_id, subject_id, teacher_id, day_of_week,
                start_time, end_time, room, period_label, slot_type, batch,
                is_unconfirmed, effective_from, is_active, created_at
            )
            SELECT 
                id, class_section_id, subject_id, teacher_id, day_of_week,
                start_time, end_time, room, period_label, slot_type, batch,
                is_unconfirmed, effective_from, is_active, created_at
            FROM timetable_slots
        """)
        c.execute("DROP TABLE timetable_slots")
        c.execute("ALTER TABLE timetable_slots_new RENAME TO timetable_slots")
    c.execute("PRAGMA foreign_keys=ON")

def seed_timetable(dbpath):
    print(f"\nSeeding timetable in {dbpath}...")
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    # 1. Ensure IDE-UNCONFIRMED subject exists
    c.execute("SELECT id FROM subjects WHERE code='IDE-UNCONFIRMED'")
    row = c.fetchone()
    if not row:
        c.execute("SELECT department_id FROM class_sections WHERE id='class-aiml-4a'")
        dept_row = c.fetchone()
        dept_id = dept_row[0] if dept_row else "dept-aiml"
        c.execute("""
            INSERT INTO subjects (id, code, name, department_id, semester, credits, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("subject-ide-unconfirmed", "IDE-UNCONFIRMED", "IDE (Unconfirmed)", dept_id, "7", 0, 1, now))
        print("  Created IDE-UNCONFIRMED subject")

    make_subject_id_nullable(c)

    # 2. Mark legacy slots inactive
    c.execute("UPDATE timetable_slots SET is_active=0 WHERE id LIKE 'slot-0%'")
    print(f"  Deactivated legacy slots (rows updated: {c.rowcount})")

    # 3. Clean any existing 7th sem seeded slots so this is idempotent
    c.execute("DELETE FROM timetable_slots WHERE id LIKE 'slot-7th-%'")

    t_raj = "a65d2ace-2522-4232-b597-b6e5beb3dce1"
    t_ajay = "5efb33f0-4d32-4a3f-b607-7bbe772418e2"
    t_ganesh = "bc5d8d92-9890-4e7d-8008-4953d00bd4b0"
    t_bharat = "2bd4cc94-4a57-4144-9487-d5408aa882b6"

    s_dl = "subject-22aiu701"
    s_gai = "subject-22aiu702"
    s_dea = "subject-22ait703"
    s_dsp = "subject-22ait704c"
    s_proj = "subject-22aip706"
    s_ide = "subject-ide-unconfirmed"

    slots_to_insert = [
        # --- Monday (day 0) ---
        ("slot-7th-m-s1-b1", "class-aiml-4a", s_dl, t_raj, 0, "09:00", "09:55", "Lab A-302", "S1", "lab", "B1", 0),
        ("slot-7th-m-s1-b2", "class-aiml-4a", s_gai, t_ajay, 0, "09:00", "09:55", "Lab A-302", "S1", "lab", "B2", 0),
        ("slot-7th-m-s2-b1", "class-aiml-4a", s_dl, t_raj, 0, "09:55", "10:50", "Lab A-302", "S2", "lab", "B1", 0),
        ("slot-7th-m-s2-b2", "class-aiml-4a", s_gai, t_ajay, 0, "09:55", "10:50", "Lab A-302", "S2", "lab", "B2", 0),
        ("slot-7th-m-tea",   "class-aiml-4a", None, None, 0, "10:50", "11:10", "A-302", "TEA BREAK", "break", None, 0),
        ("slot-7th-m-s3-b2", "class-aiml-4a", s_dl, t_raj, 0, "11:10", "12:05", "Lab A-302", "S3", "lab", "B2", 0),
        ("slot-7th-m-s3-b3", "class-aiml-4a", s_gai, t_ajay, 0, "11:10", "12:05", "Lab A-302", "S3", "lab", "B3", 0),
        ("slot-7th-m-s4-b2", "class-aiml-4a", s_dl, t_raj, 0, "12:05", "13:00", "Lab A-302", "S4", "lab", "B2", 0),
        ("slot-7th-m-s4-b3", "class-aiml-4a", s_gai, t_ajay, 0, "12:05", "13:00", "Lab A-302", "S4", "lab", "B3", 0),
        ("slot-7th-m-lunch", "class-aiml-4a", None, None, 0, "13:00", "13:45", "A-302", "LUNCH", "break", None, 0),
        ("slot-7th-m-s5-b3", "class-aiml-4a", s_dl, t_raj, 0, "13:45", "14:40", "Lab A-302", "S5", "lab", "B3", 0),
        ("slot-7th-m-s5-b1", "class-aiml-4a", s_gai, t_ajay, 0, "13:45", "14:40", "Lab A-302", "S5", "lab", "B1", 0),
        ("slot-7th-m-s6-b3", "class-aiml-4a", s_dl, t_raj, 0, "14:40", "15:35", "Lab A-302", "S6", "lab", "B3", 0),
        ("slot-7th-m-s6-b1", "class-aiml-4a", s_gai, t_ajay, 0, "14:40", "15:35", "Lab A-302", "S6", "lab", "B1", 0),
        ("slot-7th-m-s7",    "class-aiml-4a", None, None, 0, "15:35", "16:30", "A-302", "S7", "free", None, 0),

        # --- Tuesday (day 1) ---
        ("slot-7th-t-s1",    "class-aiml-4a", s_dl, t_raj, 1, "09:00", "09:55", "A-302", "S1", "teaching", None, 0),
        ("slot-7th-t-s2",    "class-aiml-4a", s_gai, t_ajay, 1, "09:55", "10:50", "A-302", "S2", "teaching", None, 0),
        ("slot-7th-t-tea",   "class-aiml-4a", None, None, 1, "10:50", "11:10", "A-302", "TEA BREAK", "break", None, 0),
        ("slot-7th-t-s3",    "class-aiml-4a", s_dsp, t_bharat, 1, "11:10", "12:05", "A-302", "S3", "teaching", None, 0),
        ("slot-7th-t-s4",    "class-aiml-4a", s_dea, t_ganesh, 1, "12:05", "13:00", "A-302", "S4", "teaching", None, 0),
        ("slot-7th-t-lunch", "class-aiml-4a", None, None, 1, "13:00", "13:45", "A-302", "LUNCH", "break", None, 0),
        ("slot-7th-t-s5",    "class-aiml-4a", None, None, 1, "13:45", "14:40", "A-302", "S5", "free", None, 0),
        ("slot-7th-t-s6",    "class-aiml-4a", s_proj, t_ganesh, 1, "14:40", "15:35", "A-302", "S6", "teaching", None, 0),
        ("slot-7th-t-s7",    "class-aiml-4a", s_proj, t_ganesh, 1, "15:35", "16:30", "A-302", "S7", "teaching", None, 0),

        # --- Wednesday (day 2) ---
        ("slot-7th-w-s1",    "class-aiml-4a", s_gai, t_ajay, 2, "09:00", "09:55", "A-302", "S1", "teaching", None, 0),
        ("slot-7th-w-s2",    "class-aiml-4a", s_dsp, t_bharat, 2, "09:55", "10:50", "A-302", "S2", "teaching", None, 0),
        ("slot-7th-w-tea",   "class-aiml-4a", None, None, 2, "10:50", "11:10", "A-302", "TEA BREAK", "break", None, 0),
        ("slot-7th-w-s3",    "class-aiml-4a", s_ide, None, 2, "11:10", "12:05", "A-302", "S3", "teaching", None, 1),
        ("slot-7th-w-s4",    "class-aiml-4a", s_dea, t_ganesh, 2, "12:05", "13:00", "A-302", "S4", "teaching", None, 0),
        ("slot-7th-w-lunch", "class-aiml-4a", None, None, 2, "13:00", "13:45", "A-302", "LUNCH", "break", None, 0),
        ("slot-7th-w-s5",    "class-aiml-4a", s_proj, t_ganesh, 2, "13:45", "14:40", "A-302", "S5", "teaching", None, 0),
        ("slot-7th-w-s6",    "class-aiml-4a", s_proj, t_ganesh, 2, "14:40", "15:35", "A-302", "S6", "teaching", None, 0),
        ("slot-7th-w-s7",    "class-aiml-4a", s_proj, t_ganesh, 2, "15:35", "16:30", "A-302", "S7", "teaching", None, 0),

        # --- Thursday (day 3) ---
        ("slot-7th-th-s1",   "class-aiml-4a", s_dea, t_ganesh, 3, "09:00", "09:55", "A-302", "S1", "teaching", None, 0),
        ("slot-7th-th-s2",   "class-aiml-4a", s_dsp, t_bharat, 3, "09:55", "10:50", "A-302", "S2", "teaching", None, 0),
        ("slot-7th-th-tea",  "class-aiml-4a", None, None, 3, "10:50", "11:10", "A-302", "TEA BREAK", "break", None, 0),
        ("slot-7th-th-s3",   "class-aiml-4a", s_dl, t_raj, 3, "11:10", "12:05", "A-302", "S3", "teaching", None, 0),
        ("slot-7th-th-s4",   "class-aiml-4a", s_gai, t_ajay, 3, "12:05", "13:00", "A-302", "S4", "teaching", None, 0),
        ("slot-7th-th-lunch","class-aiml-4a", None, None, 3, "13:00", "13:45", "A-302", "LUNCH", "break", None, 0),
        ("slot-7th-th-s5",   "class-aiml-4a", s_ide, None, 3, "13:45", "14:40", "A-302", "S5", "teaching", None, 1),
        ("slot-7th-th-s6",   "class-aiml-4a", None, None, 3, "14:40", "15:35", "A-302", "S6", "free", None, 0),
        ("slot-7th-th-s7",   "class-aiml-4a", None, None, 3, "15:35", "16:30", "A-302", "S7", "free", None, 0),

        # --- Friday (day 4) ---
        ("slot-7th-f-s1",    "class-aiml-4a", s_dsp, t_bharat, 4, "09:00", "09:55", "A-302", "S1", "teaching", None, 0),
        ("slot-7th-f-s2",    "class-aiml-4a", s_ide, None, 4, "09:55", "10:50", "A-302", "S2", "teaching", None, 1),
        ("slot-7th-f-tea",   "class-aiml-4a", None, None, 4, "10:50", "11:10", "A-302", "TEA BREAK", "break", None, 0),
        ("slot-7th-f-s3",    "class-aiml-4a", s_dea, t_ganesh, 4, "11:10", "12:05", "A-302", "S3", "teaching", None, 0),
        ("slot-7th-f-s4",    "class-aiml-4a", s_dl, t_raj, 4, "12:05", "13:00", "A-302", "S4", "teaching", None, 0),
        ("slot-7th-f-lunch", "class-aiml-4a", None, None, 4, "13:00", "13:45", "A-302", "LUNCH", "break", None, 0),
        ("slot-7th-f-s5",    "class-aiml-4a", s_proj, t_ganesh, 4, "13:45", "14:40", "A-302", "S5", "teaching", None, 0),
        ("slot-7th-f-s6",    "class-aiml-4a", s_proj, t_ganesh, 4, "14:40", "15:35", "A-302", "S6", "teaching", None, 0),
        ("slot-7th-f-s7",    "class-aiml-4a", s_proj, t_ganesh, 4, "15:35", "16:30", "A-302", "S7", "teaching", None, 0),

        # --- Saturday (day 5) ---
        ("slot-7th-sa-s1",   "class-aiml-4a", None, None, 5, "09:00", "09:55", "A-302", "S1", "non_teaching", None, 0),
        ("slot-7th-sa-s2",   "class-aiml-4a", None, None, 5, "09:55", "10:50", "A-302", "S2", "non_teaching", None, 0),
        ("slot-7th-sa-tea",  "class-aiml-4a", None, None, 5, "10:50", "11:10", "A-302", "TEA BREAK", "break", None, 0),
        ("slot-7th-sa-s3",   "class-aiml-4a", None, None, 5, "11:10", "12:05", "A-302", "S3", "non_teaching", None, 0),
        ("slot-7th-sa-s4",   "class-aiml-4a", None, None, 5, "12:05", "13:00", "A-302", "S4", "non_teaching", None, 0),
        ("slot-7th-sa-lunch","class-aiml-4a", None, None, 5, "13:00", "13:45", "A-302", "LUNCH", "break", None, 0),
        ("slot-7th-sa-s5",   "class-aiml-4a", None, None, 5, "13:45", "14:40", "A-302", "S5", "non_teaching", None, 0),
        ("slot-7th-sa-s6",   "class-aiml-4a", None, None, 5, "14:40", "15:35", "A-302", "S6", "non_teaching", None, 0),
        ("slot-7th-sa-s7",   "class-aiml-4a", None, None, 5, "15:35", "16:30", "A-302", "S7", "non_teaching", None, 0),
    ]

    for slot in slots_to_insert:
        sid, cid, sub_id, tid, dow, st, et, rm, pl, stype, batch, unconf = slot
        c.execute("""
            INSERT INTO timetable_slots (
                id, class_section_id, subject_id, teacher_id, day_of_week,
                start_time, end_time, room, period_label, slot_type, batch,
                is_unconfirmed, effective_from, is_active, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
        """, (sid, cid, sub_id, tid, dow, st, et, rm, pl, stype, batch, unconf, "2026-08-03", now))

    conn.commit()
    print(f"  Inserted {len(slots_to_insert)} new active 7th semester slots.")
    conn.close()

seed_timetable('vista/backend/vista_dev.db')
seed_timetable('vista_dev.db')
print("\nTimetable seeding completed successfully!")
