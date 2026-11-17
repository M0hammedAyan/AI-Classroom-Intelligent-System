import sqlite3
c = sqlite3.connect('vista/backend/vista_dev.db')
print(c.execute('select id,captured_at,status,reason from capture_events').fetchall())
n = c.execute("delete from capture_events where status='failed' and reason='No faces detected in image.' and captured_at>='2026-11-17'").rowcount
c.commit()
print('deleted', n, c.execute('select count(*) from capture_events').fetchone(), c.execute('select count(*) from attendance').fetchone())
