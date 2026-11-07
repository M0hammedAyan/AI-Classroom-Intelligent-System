import sqlite3

conn = sqlite3.connect('vista/backend/vista_dev.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [r[0] for r in cursor.fetchall() if not r[0].startswith('sqlite_')]

print("Searching DB for '3rd' or '3rd Year':")
for t in tables:
    cursor.execute(f"PRAGMA table_info({t});")
    cols = [c[1] for c in cursor.fetchall()]
    for c in cols:
        try:
            cursor.execute(f"SELECT rowid, {c} FROM {t} WHERE CAST({c} AS TEXT) LIKE '%3rd%'")
            rows = cursor.fetchall()
            if rows:
                print(f"Table {t}, Column {c}: {rows}")
        except Exception:
            pass
