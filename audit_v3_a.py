"""Audit v3 parts a+b: dataset counts, roster check, MD5 dupes, ArcFace class cosines.
Usage: python audit_v3_a.py [--per-student 15]
Outputs under training_results/expanded_v3/diagnosis/. Resumable (embeddings cached)."""
import argparse, csv, hashlib, random, re, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
DS = ROOT / "dataset"
OUT = ROOT / "training_results" / "expanded_v3" / "diagnosis"
EXT = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
USN = re.compile(r"^1DA\d{2}[A-Z]{2}\d{3}$")


def w_csv(name, header, rows):
    with open(OUT / name, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--per-student", type=int, default=15)
    n = ap.parse_args().per_student
    OUT.mkdir(parents=True, exist_ok=True)
    roster = set(re.findall(r"\|(1DA\w+)", (ROOT / "vista/frontend/src/App.jsx").read_text(encoding="utf-8")))
    folders = sorted(p for p in DS.iterdir() if p.is_dir())
    files = {p.name: sorted(f for f in p.rglob("*") if f.is_file()) for p in folders}
    stray = [f.name for f in DS.iterdir() if f.is_file()]
    rows, md5s, nonimg = [], {}, []
    for u, fl in files.items():
        imgs = [f for f in fl if f.suffix.lower() in EXT]
        nonimg += [str(f) for f in fl if f.suffix.lower() not in EXT]
        rows.append([u, len(imgs), bool(USN.match(u)), u in roster, len(imgs) == 0, len(imgs) < 10])
        for f in imgs:
            md5s.setdefault(hashlib.md5(f.read_bytes()).hexdigest(), []).append(f)
    w_csv("students.csv", ["usn", "photos", "valid_usn", "in_roster", "empty", "lt10"], rows)
    dup_rows = []
    for h, fl in md5s.items():
        if len(fl) > 1:
            same = len({f.parent.name for f in fl}) == 1
            for f in fl:
                dup_rows.append([h, f.parent.name, f.name, "same_folder" if same else "cross_usn"])
    w_csv("md5_dupes.csv", ["md5", "usn", "file", "kind"], dup_rows)

    # embeddings (cached)
    npz = OUT / "embeddings.npz"
    cache = {}
    if npz.exists():
        d = np.load(npz, allow_pickle=True)
        cache = {k: e for k, e in zip(d["paths"], d["emb"])}
    from vista.vision.facial_pipeline import initialize_face_detector
    import cv2
    app = None
    rng = random.Random(42)
    paths, embs, labels, noface = [], [], [], []
    for u, fl in files.items():
        imgs = [f for f in fl if f.suffix.lower() in EXT]
        sel = sorted(rng.sample(imgs, min(n, len(imgs))))
        for f in sel:
            key = str(f.relative_to(DS))
            if key in cache:
                e = cache[key]
            else:
                if app is None:
                    app = initialize_face_detector()
                im = cv2.imread(str(f))
                fs = app.get(im) if im is not None else []
                if not fs:
                    noface.append(key); continue
                b = max(fs, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))
                e = b.normed_embedding
            paths.append(key); embs.append(e); labels.append(u)
        print(u, "done", flush=True)
    embs = np.array(embs, dtype=np.float32)
    np.savez(npz, paths=np.array(paths), emb=embs, labels=np.array(labels))
    us = sorted(set(labels))
    M = np.array([embs[[i for i, l in enumerate(labels) if l == u]].mean(0) for u in us])
    M /= np.linalg.norm(M, axis=1, keepdims=True)
    C = M @ M.T
    pairs = sorted(((float(C[i, j]), us[i], us[j]) for i in range(len(us)) for j in range(i + 1, len(us))), reverse=True)
    w_csv("class_cosines.csv", ["cosine", "usn_a", "usn_b"], pairs)

    tot = sum(r[1] for r in rows)
    L = ["# AUDIT_V3", "", "## a) Dataset counts", "",
         f"- Student folders: {len(folders)} (user expects 29)", f"- Total photos: {tot}",
         f"- Stray files at dataset root: {stray or 'none'}", f"- Non-image files: {nonimg or 'none'}",
         f"- Invalid USN folder names: {[r[0] for r in rows if not r[2]] or 'none'}",
         f"- Empty folders: {[r[0] for r in rows if r[4]] or 'none'}",
         f"- <10 photos: {[r[0] for r in rows if r[5]] or 'none'}",
         f"- Not in roster ({len(roster)} roster USNs): {[r[0] for r in rows if not r[3]] or 'none'}", "",
         "| USN | photos | in roster |", "|---|---|---|"]
    L += [f"| {r[0]} | {r[1]} | {r[3]} |" for r in rows]
    cross = [r for r in dup_rows if r[3] == "cross_usn"]; same = [r for r in dup_rows if r[3] == "same_folder"]
    L += ["", "## b) Duplicates and embeddings", "",
          f"- MD5 groups duplicated: {sum(1 for v in md5s.values() if len(v) > 1)}",
          f"- Cross-USN duplicate files: {len(cross)}", f"- Same-folder duplicate files: {len(same)}"]
    L += [f"  - {r[1]}/{r[2]} ({r[0][:8]})" for r in dup_rows]
    L += ["", f"- Embedded photos: {len(paths)} (<= {n}/student); no face detected: {noface or 'none'}",
          f"- Pairs with cosine > 0.6: {sum(1 for p in pairs if p[0] > 0.6)}", "", "Top 10 closest pairs:", "",
          "| cosine | A | B |", "|---|---|---|"]
    L += [f"| {c:.4f} | {a} | {b} |" for c, a, b in pairs[:10]]
    (OUT / "AUDIT_V3.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:14])); print(*pairs[:10], sep="\n"); print("dupes", len(dup_rows), "cross", len(cross))


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    main()
