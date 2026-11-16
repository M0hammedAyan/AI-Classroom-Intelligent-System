"""Audit v3 parts c, d, e. Outputs under training_results/expanded_v3/diagnosis/.
Usage: python audit_v3_b.py [--stage detect|report]. Detection cached in photo_stats.csv."""
import argparse, csv, hashlib, json, random, re, subprocess
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent
DS = ROOT / "dataset"
AUG = ROOT / "agumented data"
NPZ = ROOT / "data" / "processed" / "facial_pipeline_results.npz"
OUT = ROOT / "training_results" / "expanded_v3" / "diagnosis"
SHEETS = OUT / "contact_sheets"
EXT = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
COLS = ["usn", "file", "width", "height", "n_faces", "det_score", "bbox", "face_w", "face_h",
        "lap_var", "brightness", "chosen_by", "second_score"]


def npz_meta():
    d = np.load(NPZ, allow_pickle=True)
    return d, d["metadata"]


def detect():
    import cv2
    from vista.vision.facial_pipeline import initialize_face_detector
    OUT.mkdir(parents=True, exist_ok=True)
    f_csv = OUT / "photo_stats.csv"
    done = {}
    if f_csv.exists():
        for r in csv.DictReader(open(f_csv, encoding="utf-8")):
            done[(r["usn"], r["file"])] = r
    app = initialize_face_detector()
    rows = list(done.values())
    for u in sorted(p.name for p in DS.iterdir() if p.is_dir()):
        for f in sorted((DS / u).iterdir()):
            if f.suffix.lower() not in EXT or (u, f.name) in done:
                continue
            im = cv2.imread(str(f))
            if im is None:
                rows.append(dict(usn=u, file=f.name, width=0, height=0, n_faces=-1)); continue
            h, w = im.shape[:2]
            faces = app.get(im)
            r = dict(usn=u, file=f.name, width=w, height=h, n_faces=len(faces))
            if faces:
                fs = sorted(faces, key=lambda x: -x.det_score)
                p = fs[0]  # pipeline rule: highest det_score
                x1, y1, x2, y2 = [int(v) for v in p.bbox]
                x1, y1 = max(0, min(x1, w - 1)), max(0, min(y1, h - 1)); x2, y2 = min(x2, w), min(y2, h)
                crop = im[y1:y2, x1:x2]
                g = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
                r.update(det_score=round(float(p.det_score), 4), bbox=json.dumps([x1, y1, x2, y2]),
                         face_w=x2 - x1, face_h=y2 - y1, lap_var=round(float(cv2.Laplacian(g, cv2.CV_64F).var()), 2),
                         brightness=round(float(g.mean()), 2), chosen_by="max_det_score",
                         second_score=round(float(fs[1].det_score), 4) if len(fs) > 1 else "")
            rows.append(r)
        print(u, "detected", flush=True)
        with open(f_csv, "w", newline="", encoding="utf-8") as fh:
            w_ = csv.DictWriter(fh, COLS); w_.writeheader()
            for r in rows: w_.writerow({k: r.get(k, "") for k in COLS})


def load_stats():
    rows = list(csv.DictReader(open(OUT / "photo_stats.csv", encoding="utf-8")))
    for r in rows:
        for k in ["width", "height", "n_faces", "face_w", "face_h"]:
            r[k] = int(r[k]) if r[k] != "" else None
        for k in ["det_score", "lap_var", "brightness", "second_score"]:
            r[k] = float(r[k]) if r[k] != "" else None
    return rows


def stat(v):
    v = [x for x in v if x is not None]
    return (len(v), float(np.mean(v)), float(np.median(v)), float(np.std(v))) if v else (0, 0, 0, 0)


def part_c(rows, old):
    from scipy import stats
    res, md = {}, []
    metrics = [("megapixels", lambda r: r["width"] * r["height"] / 1e6), ("face_w", lambda r: r["face_w"]),
               ("face_h", lambda r: r["face_h"]), ("det_score", lambda r: r["det_score"]),
               ("lap_var", lambda r: r["lap_var"]), ("brightness", lambda r: r["brightness"])]
    grp = {"old": [r for r in rows if r["usn"] in old], "new": [r for r in rows if r["usn"] not in old]}
    md.append(f"Old group = {len({r['usn'] for r in grp['old']})} students present in dataset\\ and in npz ({len(grp['old'])} photos); "
              f"new = {len({r['usn'] for r in grp['new']})} students ({len(grp['new'])} photos).\n")
    md.append("| metric | old mean (median) | new mean (median) | Mann-Whitney p | flag |\n|---|---|---|---|---|")
    csv_rows = []
    for name, fn in metrics:
        vals = {}
        for g, rr in grp.items():
            vals[g] = [fn(r) for r in rr if r["n_faces"] and r["n_faces"] > 0 or name == "megapixels"]
            vals[g] = [x for x in vals[g] if x is not None]
        so, sn = stat(vals["old"]), stat(vals["new"])
        p = float(stats.mannwhitneyu(vals["old"], vals["new"]).pvalue)
        ratio = sn[2] / so[2] if so[2] else 0
        flag = "DIFFERENT" if p < 0.01 and (ratio < 0.8 or ratio > 1.25) else ("minor" if p < 0.01 else "same")
        md.append(f"| {name} | {so[1]:.2f} ({so[2]:.2f}) | {sn[1]:.2f} ({sn[2]:.2f}) | {p:.2g} | {flag} (new/old median {ratio:.2f}) |")
        csv_rows.append([name, *so[1:3], *sn[1:3], p, ratio, flag])
        res[name] = flag
    for g, rr in grp.items():
        nf = sum(1 for r in rr if not r["n_faces"] or r["n_faces"] <= 0)
        multi = sum(1 for r in rr if (r["n_faces"] or 0) > 1)
        md.append(f"\n- {g}: {len(rr)} photos, no face {nf} ({100*nf/len(rr):.1f}%), multi-face {multi} ({100*multi/len(rr):.1f}%)")
        res[g + "_noface"] = nf; res[g + "_multi"] = multi
    resos = {}
    for g, rr in grp.items():
        c = {}
        for r in rr: c[f"{r['width']}x{r['height']}"] = c.get(f"{r['width']}x{r['height']}", 0) + 1
        resos[g] = sorted(c.items(), key=lambda x: -x[1])[:4]
        md.append(f"- {g} top resolutions: {resos[g]}")
    with open(OUT / "old_vs_new.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["metric", "old_mean", "old_median", "new_mean", "new_median", "p", "median_ratio", "flag"]); w.writerows(csv_rows)
    return "\n".join(md), res


def sheets(rows, old, d):
    import cv2
    SHEETS.mkdir(parents=True, exist_ok=True)
    rng = random.Random(7)
    new = sorted({r["usn"] for r in rows} - old)
    orig = rng.sample(sorted(old & {r["usn"] for r in rows}), 3)
    for u in new + orig:
        rr = [r for r in rows if r["usn"] == u and r["bbox"]]
        sel = sorted(rng.sample(rr, min(32, len(rr))), key=lambda r: r["file"])
        T = 160
        canvas = np.zeros((4 * T, 8 * T, 3), np.uint8)
        for i, r in enumerate(sel):
            im = cv2.imread(str(DS / u / r["file"]))
            x1, y1, x2, y2 = json.loads(r["bbox"])
            c = cv2.resize(im[y1:y2, x1:x2], (T, T))
            tag = f"{r['file'][-10:-4]}"
            if r["n_faces"] > 1: tag += f" F{r['n_faces']}"
            cv2.putText(c, tag, (2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
            canvas[(i // 8) * T:(i // 8 + 1) * T, (i % 8) * T:(i % 8 + 1) * T] = c
        cv2.putText(canvas, u, (4, 4 * T - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.imwrite(str(SHEETS / f"{u}.png"), canvas)
    return new, orig


def part_e(rows, old, d, meta):
    # npz truth per student: source -> (bbox, score, count of aug)
    npz = {}
    for m in meta:
        e = npz.setdefault(m["student_id"], {})
        s = e.setdefault(m["source_image"], {"n": 0, "bbox": None, "score": None})
        s["n"] += 1
        if m["augmentation_index"] == 0:
            s["bbox"], s["score"] = m["original_bbox"], m["det_score"]
    ds_rows = {}
    for r in rows: ds_rows.setdefault(r["usn"], {})[r["file"]] = r
    augdirs = {p.name: {q.name: len(list(q.glob("aug_*.jpg"))) for q in p.iterdir() if q.is_dir()} for p in AUG.iterdir() if p.is_dir()}
    ds_users = sorted(p.name for p in DS.iterdir() if p.is_dir())
    regen, keep, detail = [], [], {}
    for u in ds_users:
        photos = {f.name for f in (DS / u).iterdir() if f.suffix.lower() in EXT}
        stems = {Path(f).stem: f for f in photos}
        a = augdirs.get(u)
        if a is None:
            regen.append(u); detail[u] = "no augmented folder"; continue
        nof = {Path(r['file']).stem for r in ds_rows[u].values() if not r['n_faces'] or r['n_faces'] <= 0}
        miss = sorted(set(stems) - set(a) - nof); orph = sorted(set(a) - set(stems))
        bad_cnt = sorted(k for k, v in a.items() if v != 30)
        # content check: redetected bbox vs npz aug_000 bbox
        mism = []
        for s, f in stems.items():
            n = npz.get(u, {}).get(f)
            r = ds_rows[u][f]
            if n is None or n["bbox"] is None: continue
            if not r["bbox"]: mism.append(f); continue
            b = json.loads(r["bbox"]); o = n["bbox"]
            ix = max(0, min(b[2], o[2]) - max(b[0], o[0])); iy = max(0, min(b[3], o[3]) - max(b[1], o[1]))
            iou = ix * iy / ((b[2]-b[0])*(b[3]-b[1]) + (o[2]-o[0])*(o[3]-o[1]) - ix * iy + 1e-9)
            if iou < 0.9: mism.append(f)
        stale = bool(miss or orph or bad_cnt or mism)
        (regen if stale else keep).append(u)
        detail[u] = dict(photos=len(photos), aug_folders=len(a), missing_in_aug=miss, orphan_in_aug=orph,
                         not_30=bad_cnt, bbox_mismatch=mism)
    orphan_students = sorted(set(augdirs) - set(ds_users))
    return regen, keep, detail, orphan_students, npz


def ident(rows, d):
    import cv2
    from vista.vision.facial_pipeline import initialize_face_detector
    e = np.load(OUT / "embeddings.npz", allow_pickle=True)
    lab = np.array(e["labels"]); E = e["emb"]
    cen = {}
    for u in set(lab):
        c = E[lab == u].mean(0); cen[u] = c / np.linalg.norm(c)
    app = initialize_face_detector()
    out, md = [], []
    for r in rows:
        if (r["n_faces"] or 0) < 2: continue
        im = cv2.imread(str(DS / r["usn"] / r["file"]))
        fs = sorted(app.get(im), key=lambda x: -x.det_score)
        cs = [float(f.normed_embedding @ cen[r["usn"]]) for f in fs]
        best = int(np.argmax(cs))
        out.append([r["usn"], r["file"], len(fs), round(cs[0], 3), round(cs[best], 3), best != 0])
    with open(OUT / "multi_face_identity.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["usn", "file", "n_faces", "chosen_cos_to_own_centroid", "best_cos_any_face", "chosen_is_not_best"]); w.writerows(out)
    bad = [o for o in out if o[5]]; low = [o for o in out if o[3] < 0.3]
    md.append(f"\n### Identity check of chosen face in multi-face photos\nCosine of each detected face to the student's centroid (from single-pass sampled embeddings). "
              f"{len(out)} photos checked; chosen face is not the closest-to-centroid face in {len(bad)}; chosen face cosine < 0.3 in {len(low)}. Full table: multi_face_identity.csv\n")
    md.append("| USN | photo | faces | chosen cos | best cos |\n|---|---|---|---|---|")
    for o in sorted(set(map(tuple, bad + low))): md.append(f"| {o[0]} | {o[1]} | {o[2]} | {o[3]} | {o[4]} |")
    d2 = np.load(NPZ, allow_pickle=True); L = d2["labels"]; X = d2["embeddings"]
    mu = {}
    for u in ["1DA22AI402", "1DA24AI403"]:
        c = X[L == u].mean(0); mu[u] = c / np.linalg.norm(c)
    md.append(f"\n- Old npz class means: cos(1DA22AI402, 1DA24AI403) = {float(mu['1DA22AI402'] @ mu['1DA24AI403']):.3f}; "
              f"1DA22AI402 vs current dataset 1DA24AI403 centroid = {float(mu['1DA22AI402'] @ cen['1DA24AI403']):.3f}; "
              f"npz 1DA24AI403 vs current dataset 1DA24AI403 = {float(mu['1DA24AI403'] @ cen['1DA24AI403']):.3f}")
    return "\n".join(md)


def tree_hash():
    h = hashlib.sha256(); n = 0
    for p in sorted(AUG.rglob("*")):
        if p.is_file():
            st = p.stat(); h.update(f"{p.relative_to(AUG)}|{st.st_size}|{int(st.st_mtime)}".encode()); n += 1
    return h.hexdigest()[:16], n


def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def report():
    rows = load_stats()
    d, meta = npz_meta()
    old_all = set(d["labels"])
    old = old_all & {r["usn"] for r in rows}
    md = ["\n\n---\n# Parts c, d, e\n", "## c) Old vs new students\n"]
    ctext, cres = part_c(rows, old)
    md.append(ctext)
    new, orig = sheets(rows, old, d)
    md.append(f"\n\n## d) Label check\nContact sheets (4x8 random face crops, tag = photo time suffix, `Fn` = n faces detected): "
              f"`contact_sheets/<USN>.png` for new {new} and random originals {orig}. Visual findings are in the section below.\n")
    multi = [r for r in rows if (r["n_faces"] or 0) > 1]
    noface = [r for r in rows if not r["n_faces"] or r["n_faces"] <= 0]
    with open(OUT / "multi_face.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["usn", "file", "n_faces", "chosen_det_score", "chosen_face_wxh", "second_best_score", "rule"])
        for r in multi: w.writerow([r["usn"], r["file"], r["n_faces"], r["det_score"], f"{r['face_w']}x{r['face_h']}", r["second_score"], "highest det_score"])
    md.append(f"### Multi-face photos ({len(multi)}); chosen face = highest det_score (same rule as facial_pipeline.extract_primary_face). Full list: multi_face.csv\n")
    md.append("| USN | photo | faces | chosen score | chosen size | runner-up score |\n|---|---|---|---|---|---|")
    for r in multi: md.append(f"| {r['usn']} | {r['file']} | {r['n_faces']} | {r['det_score']} | {r['face_w']}x{r['face_h']} | {r['second_score']} |")
    md.append(f"\n### Photos with no detected face ({len(noface)})\n" + "\n".join(f"- {r['usn']}\\{r['file']}" for r in noface))
    regen, keep, detail, orphan, npz = part_e(rows, old, d, meta)
    exclude = [f"{r['usn']}/{r['file']}" for r in noface]
    json.dump(dict(regen=regen, keep=keep, exclude_photos=exclude, orphan_aug_students_not_in_dataset=orphan,
                   detail=detail), open(OUT / "regen_list.json", "w", encoding="utf-8"), indent=1)
    h, n = tree_hash()
    g_aug = git("status", "--porcelain", "--", "agumented data"); g_npz = git("status", "--porcelain", "--", str(NPZ.relative_to(ROOT)))
    md.append(ident(rows, d))
    wrong = [f'{r[0]}/{r[1]}' for r in csv.reader(open(OUT / 'multi_face_identity.csv', encoding='utf-8')) if r[0] != 'usn' and float(r[3]) < 0.3]
    exclude += wrong
    J = json.load(open(OUT / 'regen_list.json', encoding='utf-8')); J['exclude_photos'] = exclude; J['wrong_face_photos'] = wrong
    json.dump(J, open(OUT / 'regen_list.json', 'w', encoding='utf-8'), indent=1)
    md.append(f'- Wrong-face photos (chosen face cos<0.3 to own centroid) added to exclude_photos: {len(wrong)}. Orphan aug-only class 1DA22AI402 is the same person/photos as 1DA24AI403 in the old npz (class-mean cos 0.999, identical source names) and is not a member: do not train on it.')
    sha = hashlib.sha256(NPZ.read_bytes()).hexdigest()[:16]
    lfs = (AUG / "1DA23AI001").rglob("aug_000.jpg").__next__().stat().st_size
    md.append("\n## e) Stale-data check\n")
    md.append(f"- Augmented folders present: {len(list(AUG.iterdir()))}. Dataset folders: {len(detail)}. Augmented folders with no dataset folder: {orphan}.")
    md.append(f"- The `aug_*.jpg` files are Git LFS pointer stubs ({lfs} bytes each), not images, so source-vs-augmented MD5 is not recoverable from them. "
              f"Content was instead compared by re-detecting each photo and matching the face bbox (IoU>=0.9) with `original_bbox` of aug_idx 0 in the original npz (which holds the real 160x160 crops).")
    md.append(f"- Regen needed ({len(regen)}): {regen}\n- Keep ({len(keep)}): {keep}")
    for u in regen + keep:
        dd = detail[u]
        if isinstance(dd, str): md.append(f"  - {u}: {dd}")
        elif regen.count(u):
            md.append(f"  - {u}: photos {dd['photos']}, aug folders {dd['aug_folders']}, missing {len(dd['missing_in_aug'])}, orphan {len(dd['orphan_in_aug'])}, not-30 {len(dd['not_30'])}, bbox-mismatch {len(dd['bbox_mismatch'])}")
    md.append(f"- exclude_photos ({len(exclude)}): {exclude}; non-image `TEMP` files are ignored by the image filter.")
    md.append(f"- Untouched check: `agumented data` tree hash (name|size|mtime) {h} over {n} files, git status: {g_aug or 'clean'}; "
              f"npz sha256[:16] {sha}, mtime {NPZ.stat().st_mtime:.0f}, git status: {g_npz or 'clean'}. Nothing was written to either by this audit.")
    (OUT / "AUDIT_V3.md").write_text((OUT / "AUDIT_V3.md").read_text(encoding="utf-8").split("\n\n---\n# Parts c, d, e")[0] + "\n".join(md) + "\n", encoding="utf-8")
    print("report written", len(regen), len(keep), len(multi), len(noface), cres)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--stage", default="all")
    s = ap.parse_args().stage
    if s in ("detect", "all"): detect()
    if s in ("report", "all"): report()
