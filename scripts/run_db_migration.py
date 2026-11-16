import sqlite3

def run_mig(dbpath):
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    
    def add_col_if_missing(table, col, col_def):
        c.execute(f"PRAGMA table_info({table})")
        cols = [r[1] for r in c.fetchall()]
        if col not in cols:
            print(f"Adding {col} to {table} in {dbpath}...")
            c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_def}")
            conn.commit()

    add_col_if_missing('timetable_slots', 'period_label', 'TEXT')
    add_col_if_missing('timetable_slots', 'slot_type', "TEXT DEFAULT 'teaching'")
    add_col_if_missing('timetable_slots', 'batch', 'TEXT')
    add_col_if_missing('timetable_slots', 'is_unconfirmed', 'BOOLEAN DEFAULT 0')
    add_col_if_missing('timetable_slots', 'effective_from', 'TEXT')

    add_col_if_missing('students', 'batch', 'TEXT')

    add_col_if_missing('attendance', 'slot_id', 'TEXT')
    add_col_if_missing('attendance', 'period_label', 'TEXT')
    add_col_if_missing('attendance', 'is_extra_class', 'BOOLEAN DEFAULT 0')
    add_col_if_missing('attendance', 'extra_class_reason', 'TEXT')
    
    conn.close()

run_mig('vista/backend/vista_dev.db')
run_mig('vista_dev.db')
print('Migration test completed!')
