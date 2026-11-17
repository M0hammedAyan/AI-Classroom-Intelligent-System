import re,os,sqlite3,json,glob,numpy as np
R=r'D:\CipherTECH\Projects\AI-Classroom-Intelligent-System'
T=R+r'\.agents\tasks\dataset-expansion'
src=open(R+r'\vista\frontend\src\App.jsx',encoding='utf8').read()
m=re.search(r'const ROSTER = `(.*?)`',src,re.S)
roster={}
for l in m.group(1).strip().splitlines():
    if '|' in l:
        n,u=l.rsplit('|',1); roster[u.strip()]=n.strip()
IMG=('.jpg','.jpeg','.png','.bmp','.webp')
ds={};anom=[]
for d in sorted(os.listdir(R+r'\dataset')):
    p=R+r'\dataset'+'\\'+d
    if not os.path.isdir(p): anom.append(f'file in dataset root: {d}');continue
    fs=[f for f in os.listdir(p) if f.lower().endswith(IMG)]
    other=[f for f in os.listdir(p) if not f.lower().endswith(IMG)]
    if other: anom.append(f'{d}: non-image files {other[:3]}')
    ds[d]=sorted(fs)
ag={};missing={}
for d in sorted(os.listdir(R+r'\agumented data')):
    p=R+r'\agumented data'+'\\'+d
    if not os.path.isdir(p): continue
    ag[d]={}
    for s in os.listdir(p):
        sp=p+'\\'+s
        if os.path.isdir(sp):
            ag[d][s]=set(f for f in os.listdir(sp) if re.fullmatch(r'aug_\d{3}\.jpg',f))
full={f'aug_{i:03d}.jpg' for i in range(30)}
db=sqlite3.connect('file:'+R+r'\vista\backend\vista_dev.db?mode=ro',uri=True)
cols=[c[1] for c in db.execute('pragma table_info(students)')]
print(cols)
dbu=set()
for c in cols:
    if c.lower() in('usn','student_usn','roll_no'):
        dbu={r[0] for r in db.execute(f'select {c} from students')}
z=np.load(R+r'\data\processed\facial_pipeline_results.npz',allow_pickle=True)
labs=z['labels']; ulab,cnt=np.unique(labs,return_counts=True)
print(labs.dtype,ulab[:5])
npzset={str(x) for x in ulab}
rows=[];tot_src=0;tot_ag=0
allu=sorted(set(ds)|set(ag)|set(roster))
valid=re.compile(r'^1DA2\dAI\d{3}$')
for u in allu:
    n=len(ds.get(u,[]))
    a=ag.get(u,{})
    nsrc=len(a); naug=sum(len(v) for v in a.values())
    stems={os.path.splitext(f)[0] for f in ds.get(u,[])}
    miss=sorted(f for f in ds.get(u,[]) if len(a.get(os.path.splitext(f)[0],set()) & full)<30)
    if miss: missing[u]=miss
    if u in ds and not valid.match(u): anom.append(f'invalid USN folder name: {u}')
    orphan=sorted(set(a)-stems) if u in ds else sorted(a)
    if orphan: anom.append(f'{u}: aug folders without raw image: {orphan[:3]} (n={len(orphan)})')
    if u in ds and u not in roster: st='not-in-roster'
    elif u not in ds: st='not in dataset'
    elif n<3: st='<3 images'
    elif not a: st='missing augmentation'
    elif miss: st='partial'
    else: st='ok'
    if u in ds and u not in roster and False: pass
    rows.append((u,n,nsrc,naug,u in roster,u in dbu,st))
    tot_src+=n
dsu=set(ds);agu=set(ag)
L=['# S1 Audit','',f'Roster: {len(roster)} students (App.jsx). dataset folders: {len(ds)}. agumented data folders: {len(ag)}. DB students: {len(dbu)}.','',
'| USN | dataset imgs | aug src imgs | augs | roster | DB | status |','|---|---|---|---|---|---|---|']
for r in rows: L.append(f'| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {"Y" if r[4] else "N"} | {"Y" if r[5] else "N"} | {r[6]} |')
from collections import Counter
sc=Counter(r[6] for r in rows)
L+=['','## Totals',f'- Students in dataset: {len(ds)}; source images: {sum(len(v) for v in ds.values())}',
f'- Students in agumented data: {len(ag)}; source folders: {sum(len(v) for v in ag.values())}; aug files: {sum(len(s) for v in ag.values() for s in v.values())}',
f'- Status counts: {dict(sc)}',
f'- Source images lacking complete aug_000..029: {sum(len(v) for v in missing.values())} across {len(missing)} students',
f'- In dataset not in agumented data: {sorted(dsu-agu)}',
f'- In agumented data not in dataset: {sorted(agu-dsu)}',
f'- Roster students not in dataset: {len(set(roster)-dsu)}',
f'- Dataset USNs not in roster: {sorted(dsu-set(roster))}',
f'- Dataset USNs not in DB: {sorted(dsu-dbu)}',
f'- Students with <3 images (file count): {sorted(u for u in ds if len(ds[u])<3)}',
'','## NPZ',f'- samples: {len(labs)}; classes: {len(npzset)}; keys: {list(z.keys())}',
f'- NPZ classes == agumented students: {npzset==agu}; npz-only: {sorted(npzset-agu)}; aug-only: {sorted(agu-npzset)}',
'','## Anomalies']+[f'- {a}' for a in anom]+(['- none'] if not anom else [])
L+=['','## Target (60-70 more students)',f'- Students with images now: {len(ds)}; with augmentation: {len(ag)}; roster: {len(roster)}; NPZ classes: {len(npzset)}',
f'- Target total at +60..70 over {len(ag)} augmented: {len(ag)+60}..{len(ag)+70}; remaining new students needed: {60-0}..70 beyond current augmented set, of which dataset provides {len(dsu-agu)} unaugmented',
f'- Gap to target (using augmented count {len(ag)}): need {len(ag)+60-len(ds)}..{len(ag)+70-len(ds)} more students beyond current dataset folders ({len(ds)})']
open(T+r'\s1-audit.md','w',encoding='utf8').write('\n'.join(L))
json.dump(missing,open(T+r'\s1-missing.json','w'),indent=1)
print('\n'.join(L[-30:]))

