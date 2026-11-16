with open('vista/backend/app/db.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_code = '''def create_tables() -> None:
    from .models import attendance, student, user, organization, intervention, audit, notification, timetable  # noqa: F401
    Base.metadata.create_all(bind=engine)'''

new_code = '''def _run_migrations(bind_engine) -> None:
    """Safely and idempotently apply missing columns to existing SQLite tables."""
    try:
        with bind_engine.connect() as conn:
            def add_col_if_missing(table, col, col_def):
                res = conn.execute(text(f"PRAGMA table_info({table})"))
                cols = [r[1] for r in res.fetchall()]
                if cols and col not in cols:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_def}"))
                    conn.commit()

            add_col_if_missing("timetable_slots", "period_label", "TEXT")
            add_col_if_missing("timetable_slots", "slot_type", "TEXT DEFAULT 'teaching'")
            add_col_if_missing("timetable_slots", "batch", "TEXT")
            add_col_if_missing("timetable_slots", "is_unconfirmed", "BOOLEAN DEFAULT 0")
            add_col_if_missing("timetable_slots", "effective_from", "TEXT")

            add_col_if_missing("students", "batch", "TEXT")

            add_col_if_missing("attendance", "slot_id", "TEXT")
            add_col_if_missing("attendance", "period_label", "TEXT")
            add_col_if_missing("attendance", "is_extra_class", "BOOLEAN DEFAULT 0")
            add_col_if_missing("attendance", "extra_class_reason", "TEXT")
    except Exception:
        pass


def create_tables() -> None:
    from .models import attendance, student, user, organization, intervention, audit, notification, timetable, capture  # noqa: F401
    Base.metadata.create_all(bind=engine)
    _run_migrations(engine)'''

text = text.replace(old_code.replace('\r\n', '\n'), new_code.replace('\r\n', '\n'))
text = text.replace(old_code, new_code)
with open('vista/backend/app/db.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Updated db.py')
