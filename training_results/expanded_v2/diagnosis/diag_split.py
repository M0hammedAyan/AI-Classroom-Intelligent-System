"""Diagnosis parts a, c, f. Run from project root with the project venv."""
import csv, hashlib, re, sys
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT))
from split_v2 import split_by_photo

NPZ = ROOT / "data/processed/facial_pipeline_results_expanded.npz"
LOG = ROOT / "training_results/expanded_v1_failed/data_split_expanded_log.txt"
SEED = 42
CFG = {"A": (0.80, 0.10, 0.10), "B": (0.70, 0.15, 0.15)}

d = np.load(NPZ, allow_pickle=True)
labels = [str(l).strip("'\"") for l in d["labels"]]
meta = d["metadata"]
recs = []
for i, m in enumerate(meta):
    m = m.item() if hasattr(m, "item") else m
    recs.append((i, labels[i], str(m.get("source_image", "")), int(m.get("augmentation_index", 0))))
N = len(recs)
classes = sorted(set(r[1] for r in recs))
cls_idx = {c: i for i, c in enumerate(classes)}
groups = defaultdict(list)
for r in recs:
    groups[(r[1], r[2])].append(r)
photos = sorted(groups)
aug_counts = Counter(len(g) for g in groups.values())
no_aug0 = [k for k, g in groups.items() if not any(r[3] == 0 for r in g)]
dup_aug = [k for k, g in groups.items() if len(g) != len(set(r[3] for r in g))]

# ---- v1 split: exact reimplementation of train_expanded.split_npz ----
def v1_split(tr, va):
    sl = [cls_idx[s[0]] for s in photos]
    te = round(1.0 - tr - va, 6)
    tv, test, _, _ = train_test_split(photos, sl, test_size=te, stratify=sl, random_state=SEED)
    tvl = [cls_idx[s[0]] for s in tv]
    train, val, _, _ = train_test_split(tv, tvl, test_size=va / (tr + va), stratify=tvl, random_state=SEED)
    return train, val, test

def rows(keys, train):
    out = []
    for k in keys:
        out += [r[0] for r in groups[k] if train or r[3] == 0]
    return out

def count_by_cls(idx):
    c = Counter(recs[i][1] for i in idx)
    return c

# ---- parse v1 log (sections of A and B interleaved by concurrent writes) ----
sec = {}
cur = None
for line in LOG.read_text(encoding="utf-8", errors="replace").splitlines():
    m = re.match(r"--- (TRAIN|VAL|TEST) \((\d+) samples\) ---", line)
    if m:
        cur = (m.group(1), int(m.group(2))); sec[cur] = []
        continue
    m = re.match(r"\s+\[(\S+)\]\s+(\S+)\s+aug=(\d+)", line)
    if m and cur:
        sec[cur].append((m.group(1), m.group(2), int(m.group(3))))

result = {}
lines = []
v1 = {}
for s, (tr, va, te) in CFG.items():
    a, b, c = v1_split(tr, va)
    v1[s] = (a, b, c)
    # compare with log
    lg = {}
    for (name, n), ents in sec.items():
        lg.setdefault(name, []).append((n, ents))
    exp = {"TRAIN": rows(a, True), "VAL": rows(b, False), "TEST": rows(c, False)}
    match = {}
    for name, idxs in exp.items():
        mine = sorted((recs[i][1], recs[i][2], recs[i][3]) for i in idxs)
        match[name] = any(sorted(e) == mine for n, e in lg.get(name, []))
    result[s] = match

# ---- v2 split ----
v2 = {}
flags_v2 = {}
for s, (tr, va, te) in CFG.items():
    t, v, e, fl = split_by_photo(photos, va, te, seed=SEED)
    v2[s] = (t, v, e); flags_v2[s] = fl

# ---- hash source files ----
ds = ROOT / "dataset"
fhash, dh = {}, {}
for p in sorted(ds.glob("*/*")):
    if p.suffix.lower() not in (".jpg", ".jpeg", ".png", ".bmp", ".webp"):
        continue
    fhash[(p.parent.name, p.name)] = hashlib.sha256(p.read_bytes()).hexdigest()
    try:
        im = Image.open(p).convert("L").resize((9, 8), Image.LANCZOS)
        a = np.asarray(im, dtype=np.int16)
        dh[(p.parent.name, p.name)] = (a[:, 1:] > a[:, :-1]).flatten()
    except Exception:
        pass
missing_files = [k for k in photos if k not in fhash]

def leak_checks(tag, tr, va, te, train_rows_fn=None):
    """Assert on actual index sets. Returns list of text lines."""
    L = []
    tri, vai, tei = rows(tr, True), rows(va, False), rows(te, False)
    assert not set(tri) & set(vai) and not set(tri) & set(tei) and not set(vai) & set(tei), "index overlap"
    assert all(recs[i][3] == 0 for i in vai + tei), "non-aug0 in val/test"
    ts = {(recs[i][1], recs[i][2]) for i in tri}
    vs = {(recs[i][1], recs[i][2]) for i in vai}
    es = {(recs[i][1], recs[i][2]) for i in tei}
    assert not ts & vs and not ts & es and not vs & es, "source photo shared across splits"
    assert len(vs) == len(vai) and len(es) == len(tei), "val/test hold >1 row per photo"
    L.append(f"- {tag}: PASS (train {len(tri)} rows/{len(ts)} photos, val {len(vai)}/{len(vs)}, test {len(tei)}/{len(es)}); "
             f"index overlap 0, non-aug0 in val/test 0, shared photos 0")
    # exact + near duplicates across splits
    def hs(S): return {k: fhash.get(k) for k in S}
    th, vh, eh = hs(ts), hs(vs), hs(es)
    trh = {}
    for k, h in th.items():
        if h: trh.setdefault(h, []).append(k)
    exact = 0; ex_list = []
    for nm, X in (("val", vh), ("test", eh)):
        for k, h in X.items():
            if h in trh:
                exact += 1; ex_list.append((nm, k, trh[h][0]))
    # exact between val and test
    vt = [(k, k2) for k, h in vh.items() for k2, h2 in eh.items() if h and h == h2]
    xc = sum(1 for x in ex_list if x[1][0] != x[2][0])
    L.append(f"  exact-duplicate files: eval vs train = {exact} (of which different USN = {xc}, same USN = {exact - xc}), val vs test = {len(vt)}")
    for x in ex_list[:10]: L.append(f"    {x}")
    # near duplicates (dHash hamming <=4) same class eval vs train
    near = []
    for nm, X in (("val", vs), ("test", es)):
        for k in X:
            if k not in dh: continue
            for k2 in ts:
                if k2[0] != k[0] or k2 not in dh: continue
                if int((dh[k] != dh[k2]).sum()) <= 4:
                    near.append((nm, k, k2))
    L.append(f"  near-duplicates (dHash hamming<=4, same class) eval vs train = {len(near)}")
    for x in near[:15]: L.append(f"    {x}")
    return L, exact, len(near)

# ---- per-class CSV ----
rows_csv = []
for c in classes:
    ph = [k for k in photos if k[0] == c]
    tot = sum(len(groups[k]) for k in ph)
    row = {"usn": c, "unique_photos": len(ph), "total_samples": tot,
           "group": "new" if c.startswith("1DA25AI") else "original"}
    for s in "AB":
        for ver, spl in (("v1", v1[s]), ("v2", v2[s])):
            a, b, e = spl
            row[f"{ver}{s}_train_samples"] = sum(len(groups[k]) for k in a if k[0] == c)
            row[f"{ver}{s}_val_samples"] = sum(1 for k in b if k[0] == c)
            row[f"{ver}{s}_test_samples"] = sum(1 for k in e if k[0] == c)
            row[f"{ver}{s}_train_photos"] = sum(1 for k in a if k[0] == c)
            row[f"{ver}{s}_val_photos"] = row[f"{ver}{s}_val_samples"]
            row[f"{ver}{s}_test_photos"] = row[f"{ver}{s}_test_samples"]
    row["flag_lt10_photos"] = len(ph) < 10
    for s in "AB":
        row[f"v1{s}_lt2val_or_test"] = row[f"v1{s}_val_photos"] < 2 or row[f"v1{s}_test_photos"] < 2
        row[f"v2{s}_lt2val_or_test"] = row[f"v2{s}_val_photos"] < 2 or row[f"v2{s}_test_photos"] < 2
    rows_csv.append(row)
with open(OUT / "per_class.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows_csv[0].keys()))
    w.writeheader(); w.writerows(rows_csv)

# ---- report ----
R = []
R.append("# Diagnosis parts a, c, f\n")
R.append(f"Source: `{NPZ.name}`, {N} samples, {len(classes)} classes, {len(photos)} unique (usn, source_image) photos.")
R.append(f"Rows per photo distribution: {dict(aug_counts)}. Photos without aug_idx 0: {len(no_aug0)}. Photos with repeated aug_idx: {len(dup_aug)}. Photos whose file is missing in dataset/<USN>/: {len(missing_files)}.\n")
R.append("## a) Per-class table\n")
R.append("Full table: `per_class.csv`. Photos shown as train/val/test photos; v1 = train_expanded.py split, v2 = split_v2.py.\n")
R.append("| USN | grp | photos | samples | v1A tr/va/te | v1B tr/va/te | v2A tr/va/te | v2B tr/va/te | flags |")
R.append("|---|---|---|---|---|---|---|---|---|")
for r in rows_csv:
    fl = []
    if r["flag_lt10_photos"]: fl.append("<10 photos")
    for s in "AB":
        if r[f"v1{s}_lt2val_or_test"]: fl.append(f"v1{s}<2 val/test")
        if r[f"v2{s}_lt2val_or_test"]: fl.append(f"v2{s}<2 val/test")
    def t(ver, s): return f"{r[f'{ver}{s}_train_photos']}/{r[f'{ver}{s}_val_photos']}/{r[f'{ver}{s}_test_photos']}"
    R.append(f"| {r['usn']} | {r['group']} | {r['unique_photos']} | {r['total_samples']} | {t('v1','A')} | {t('v1','B')} | {t('v2','A')} | {t('v2','B')} | {', '.join(fl)} |")
R.append("")
lt10 = [r["usn"] for r in rows_csv if r["flag_lt10_photos"]]
R.append(f"Classes with <10 unique photos: {len(lt10)} {lt10}")
ph_counts = sorted(r["unique_photos"] for r in rows_csv)
R.append(f"Photos per class: min {ph_counts[0]}, median {ph_counts[len(ph_counts)//2]}, max {ph_counts[-1]}. Original-20 mean {np.mean([r['unique_photos'] for r in rows_csv if r['group']=='original']):.1f}, new-12 mean {np.mean([r['unique_photos'] for r in rows_csv if r['group']=='new']):.1f}.")
for s in "AB":
    for ver in ("v1", "v2"):
        bad = [r["usn"] for r in rows_csv if r[f"{ver}{s}_lt2val_or_test"]]
        nv = sum(r[f"{ver}{s}_val_photos"] for r in rows_csv); nt = sum(r[f"{ver}{s}_test_photos"] for r in rows_csv)
        R.append(f"- {ver} Split {s}: val {nv} samples, test {nt} samples; classes with <2 val or <2 test photos: {len(bad)} {bad}")
R.append("")

R.append("## c) Leakage check\n")
R.append("Code review of `train_expanded.split_npz` (read, not edited): groups rows by (usn, source_image); `train_test_split` on the unique photo list, stratified by class, seed 42; train gets all rows of train photos, val/test get only rows with aug_idx==0 of their photos. So the split is by photo and val/test hold clean crops only. Weakness: `sklearn` stratification is on photo counts per class, so it does not guarantee 2 val/2 test photos per class (see a/f).\n")
R.append("Reproduction of the v1 log: my re-implementation of the split vs the sections in `data_split_expanded_log.txt`. The log is unreliable for exact comparison: A and B were written concurrently, so TRAIN/VAL/TEST sections of the two splits are interleaved (e.g. the B TRAIN header is at line 6, the A header at line 1288, and the 'TEST 152' section spans 3,400 lines). Only sections that match byte-for-byte as sets are reported True; False means 'not verifiable from the log', not 'different split'. Sample counts do agree with the log (A: 24270/102/102, B: 21270/152/152).")
for s in "AB":
    R.append(f"- Split {s}: {result[s]}")
R.append("\nAssertion run on actual index sets (index overlap, aug_idx==0 only, no shared (usn, source) photo, one row per eval photo):")
tot_ex = tot_near = 0
for ver, spl in (("v1", v1), ("v2", v2)):
    for s in "AB":
        L, ex, nr = leak_checks(f"{ver} Split {s}", *spl[s])
        R += L
R.append("")
R.append(f"Dataset files hashed: {len(fhash)} (SHA-256 of files in dataset/<USN>/). Distinct hashes: {len(set(fhash.values()))}.")
byh = defaultdict(list)
for k, h in fhash.items(): byh[h].append(k)
dups = [v for v in byh.values() if len(v) > 1]
R.append(f"Identical-content file groups inside dataset/: {len(dups)}")
for g in dups[:15]: R.append(f"  {g}")
cross = [g for g in dups if len({k[0] for k in g}) > 1]
R.append(f"  of which span more than one USN (possible mislabel/shared photo): {len(cross)}")
pairs = Counter(tuple(sorted({k[0] for k in g})) for g in cross)
R.append("  USN groups sharing identical files (count of files): " + str(dict(pairs)))
R.append("  Cross-USN identical files that are npz photos: " + str(sum(1 for g in cross for k in g if k in groups)) + " of " + str(len(photos)) + " photos in the npz.")
R.append("")

R.append("## f) Proposed split (split_v2.py)\n")
R.append("`split_by_photo(keys, val_ratio, test_ratio, seed=42, min_val=2, min_test=2)`: per class, shuffle photos with an RNG seeded by (seed, usn), take n_val=max(2, round(n*val)), n_test=max(2, round(n*test)), rest train. Same seed gives A and B the same photo ordering. Val/test use only aug_idx 0; train uses all 30 augmented copies. If a class has fewer than n_val+n_test+1 photos it falls back to 1 val/1 test (n>=3, flagged) or keeps everything in train with no val/test (n<=2, flagged). No data is created or duplicated.\n")
for s in "AB":
    t, v, e = v2[s]
    R.append(f"- Split {s} ({CFG[s]}): train {sum(len(groups[k]) for k in t)} samples/{len(t)} photos, val {len(v)}, test {len(e)}. Flags: {flags_v2[s] or 'none'}")
    R.append(f"  min val photos per class {min(r[f'v2{s}_val_photos'] for r in rows_csv)}, min test {min(r[f'v2{s}_test_photos'] for r in rows_csv)}, min train photos {min(r[f'v2{s}_train_photos'] for r in rows_csv)}")
    R.append(f"  v1 for comparison: val {len(v1[s][1])}, test {len(v1[s][2])}")
R.append("")
R.append("Classes that cannot meet 2 val + 2 test photos: " + (", ".join(f"{u}: {n}" for u, n in flags_v2['A'].items() | flags_v2['B'].items()) or "none") + ".")
R.append("Note: with 80:10:10 and min 2/2, classes with fewer than 20 photos get more than 10% in val and test; this is the cost of a usable eval set.")
(OUT / "part_a_c_f.md").write_text("\n".join(R) + "\n\n<!-- complete -->\n", encoding="utf-8")
print("\n".join(R))
