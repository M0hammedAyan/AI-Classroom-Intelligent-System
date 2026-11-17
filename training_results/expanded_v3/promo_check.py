import torch, sqlite3
D = 'training_results/'
ck = {}
for k, n in [('v3B', 'expanded_v3/best_model_expanded_v3_splitB.pth'), ('v3A', 'expanded_v3/best_model_expanded_v3_splitA.pth'), ('live', 'best_model_npz_splitB.pth')]:
    c = torch.load(D + n, map_location='cpu', weights_only=False)
    ck[k] = c
    sd = c['model_state_dict']
    last = list(sd)[-1]
    print(k, [x for x in c if x != 'model_state_dict'], len(c['class_names']), type(c['class_names']).__name__, 'epoch', c.get('epoch'), last, tuple(sd[last].shape))
live = ck['live']['class_names']; v3 = ck['v3B']['class_names']
print('live', live)
print('v3 not in live', sorted(set(v3) - set(live)))
print('live not in v3', sorted(set(live) - set(v3)))
con = sqlite3.connect('file:vista/backend/vista_dev.db?mode=ro', uri=True)
cur = con.cursor()
print('students total, active', cur.execute("select count(*),sum(is_active) from students").fetchall())
db = [r[0] for r in cur.execute("select student_id from students")]
print('v3 classes in DB', len(set(v3) & set(db)))
print('v3 classes NOT in DB', sorted(set(v3) - set(db)))
print('live classes NOT in DB', sorted(set(live) - set(db)))
print('402 row', cur.execute("select student_id,name,is_active,embedding is not null,classroom_id from students where student_id='1DA22AI402'").fetchall())
print('att rows 402', cur.execute("select count(*) from attendance where student_id='1DA22AI402'").fetchall())
print('students with embedding', cur.execute("select count(*) from students where embedding is not null and is_active=1").fetchall())
print('fk pragma', cur.execute("pragma foreign_keys").fetchall())
