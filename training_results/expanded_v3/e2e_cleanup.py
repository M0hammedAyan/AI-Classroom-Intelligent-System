import sqlite3, json
c = sqlite3.connect('vista/backend/vista_dev.db')
ids = [x['resp']['capture_event_id'] for x in json.load(open('training_results/expanded_v3/e2e_results.json'))
       if isinstance(x['resp'], dict) and 'capture_event_id' in x['resp']]
a = c.execute("delete from attendance where session_date like '2099-01-%'").rowcount
b = c.execute('delete from capture_events where id in (%s)' % ','.join('?' * len(ids)), ids).rowcount
c.commit()
print('deleted attendance', a, 'capture_events', b)
print('attendance', c.execute('select count(*) from attendance').fetchone(), 'capture_events', c.execute('select count(*) from capture_events').fetchone())
print('active', c.execute('select count(*) from students where is_active=1').fetchone(),
      'new with emb', c.execute("select count(*) from students where student_id like '1DA25AI%' and embedding is not null").fetchone())
