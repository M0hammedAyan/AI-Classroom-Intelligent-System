"""Build data/processed/facial_pipeline_results_expanded_v3.npz and the v3 splits.

Keys/format identical to facial_pipeline_results.npz: images, embeddings, labels, metadata.
augmentation_index convention (differs from baseline, see FIX_LOG.md):
    0     = clean, unaugmented 160x160 crop (identity)
    1..30 = the 30 augmented variants (aug_000..aug_029 on disk)
Val/test use only augmentation_index == 0.

Inputs : dataset/ (raw photos), agumented data/ (aug + clean.jpg for regenerated students),
         training_results/expanded_v3/clean_crops (clean crops for the 19 kept students).
Outputs: the npz, training_results/expanded_v3/splits_A.json, splits_B.json, split_counts.csv.
"""
from __future__ import annotations

import csv
import hashlib
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

DATASET = ROOT / "dataset"
AUG = ROOT / "agumented data"
V3 = ROOT / "training_results" / "expanded_v3"
CLEAN = V3 / "clean_crops"
REGEN = V3 / "diagnosis" / "regen_list.json"
OLD_NPZ = ROOT / "data" / "processed" / "facial_pipeline_results.npz"
OUT = ROOT / "data" / "processed" / "facial_pipeline_results_expanded_v3.npz"
EXT = {".jpg", ".jpeg", ".png"}
N_AUG = 30
SEED = 42
MIN_PER_SPLIT = 3
SPLITS = {"A": (0.80, 0.10, 0.10), "B": (0.70, 0.15, 0.15)}


def md5_file(p: Path) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_rgb(p: Path) -> np.ndarray:
    img = cv2.imread(str(p))
    assert img is not None, f"cannot read {p}"
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    assert img.shape == (160, 160, 3), f"{p} has shape {img.shape}"
    return img


def collect_sources():
    cfg = json.loads(REGEN.read_text())
    excl = {e.replace("\\", "/") for e in cfg["exclude_photos"]}
    usns = sorted(cfg["regen"] + cfg["keep"])
    regen = set(cfg["regen"])
    sources = []  # dicts
    for usn in usns:
        photos = sorted(p for p in (DATASET / usn).iterdir() if p.suffix.lower() in EXT)
        stems = [p.stem for p in photos]
        assert len(stems) == len(set(stems)), f"{usn}: duplicate stems"
        for p in photos:
            if f"{usn}/{p.name}" in excl:
                continue
            if usn in regen:
                clean = AUG / usn / p.stem / "clean.jpg"
            else:
                clean = CLEAN / usn / f"{p.stem}.jpg"
            augdir = AUG / usn / p.stem
            assert clean.exists(), f"missing clean crop {clean}"
            if usn in regen:
                augs = [augdir / f"aug_{i:03d}.jpg" for i in range(N_AUG)]
                assert all(a.exists() for a in augs), f"missing aug files in {augdir}"
            else:
                # kept students: aug files on disk are Git-LFS pointers, use the baseline npz variants
                augs = None
            sources.append({"usn": usn, "name": p.name, "raw": p, "clean": clean, "augs": augs, "md5": md5_file(p)})
    return usns, sources


def bbox_lookup():
    d = np.load(OLD_NPZ, allow_pickle=True)
    out, var = {}, defaultdict(dict)
    for i, m in enumerate(d["metadata"]):
        k = (m["student_id"], m["source_image"])
        var[k][m["augmentation_index"]] = i
        if m["augmentation_index"] == 0:
            out[k] = (m["original_bbox"], m["det_score"])
    return out, var, d["images"]


def make_split(sources, usns, ratios, rng_orders):
    """Per-class split by source photo. Same per-class shuffled order for every split (same seed)."""
    _, r_val, r_test = ratios
    split = {"train": [], "val": [], "test": []}
    shortfall = {}
    for usn in usns:
        order = rng_orders[usn]
        n = len(order)
        n_val = max(MIN_PER_SPLIT, round(n * r_val))
        n_test = max(MIN_PER_SPLIT, round(n * r_test))
        if n - n_val - n_test < 1:
            # cannot satisfy: keep at least 1 train photo, split the rest evenly
            rest = n - 1
            n_test = rest // 2
            n_val = rest - n_test
        if n_val < MIN_PER_SPLIT or n_test < MIN_PER_SPLIT:
            shortfall[usn] = {"photos": n, "val": n_val, "test": n_test}
        split["test"] += order[:n_test]
        split["val"] += order[n_test:n_test + n_val]
        split["train"] += order[n_test + n_val:]
    return split, shortfall


def assert_no_leakage(tag, split, sources, meta_by_sample):
    key = lambda i: (sources[i]["usn"], sources[i]["name"])  # noqa: E731
    sets = {k: set(v) for k, v in split.items()}
    assert not sets["train"] & sets["val"], f"[{tag}] source in train and val"
    assert not sets["train"] & sets["test"], f"[{tag}] source in train and test"
    assert not sets["val"] & sets["test"], f"[{tag}] source in val and test"
    assert sum(len(s) for s in sets.values()) == len(sources), f"[{tag}] sources not fully partitioned"
    # content-hash: identical files cannot be on both sides
    h = {k: {sources[i]["md5"] for i in v} for k, v in sets.items()}
    assert not h["train"] & h["val"], f"[{tag}] identical file content in train and val"
    assert not h["train"] & h["test"], f"[{tag}] identical file content in train and test"
    assert not h["val"] & h["test"], f"[{tag}] identical file content in val and test"
    # sample-level indices
    idx = {k: [j for i in v for j in meta_by_sample[i] if (k == "train" or j[1] == 0)] for k, v in split.items()}
    sidx = {k: {j[0] for j in v} for k, v in idx.items()}
    assert not sidx["train"] & sidx["val"] and not sidx["train"] & sidx["test"] and not sidx["val"] & sidx["test"], \
        f"[{tag}] sample index overlap"
    for k in ("val", "test"):
        assert all(j[1] == 0 for j in idx[k]), f"[{tag}] {k} contains augmented samples"
        assert len(idx[k]) == len(split[k]), f"[{tag}] {k}: not exactly one clean sample per photo"
    print(f"[{tag}] leakage + md5 checks PASSED", flush=True)
    return sidx


def main():
    usns, sources = collect_sources()
    print(f"{len(usns)} classes, {len(sources)} source photos", flush=True)
    old, old_var, old_images = bbox_lookup()

    # Sample table (order: by source, aug idx 0..30)
    from vista.vision import facial_pipeline as fp
    app = None
    for s in sources:
        k = (s["usn"], s["name"])
        if k in old:
            s["bbox"], s["det"] = [int(x) for x in old[k][0]], float(old[k][1])
        else:
            if app is None:
                app = fp.initialize_face_detector()
            crop, info = fp.extract_primary_face(app, str(s["raw"]))
            assert info is not None, f"no face in {s['raw']}"
            s["bbox"], s["det"] = info["bbox"], info["det_score"]
    if app is None:
        app = fp.initialize_face_detector()
    print("bboxes ready", flush=True)

    images, labels, metadata = [], [], []
    meta_by_sample = {}  # source index -> [(sample_idx, aug_idx)]
    for si, s in enumerate(sources):
        meta_by_sample[si] = []
        if s["augs"] is None:
            v = old_var[(s["usn"], s["name"])]
            assert sorted(v) == list(range(N_AUG)), f"{s['usn']}/{s['name']}: baseline npz variants {sorted(v)}"
            arrs = [read_rgb(s["clean"])] + [old_images[v[j]] for j in range(N_AUG)]
        else:
            arrs = [read_rgb(f) for f in [s["clean"]] + s["augs"]]
        for ai, arr in enumerate(arrs):
            meta_by_sample[si].append((len(images), ai))
            images.append(arr)
            labels.append(s["usn"])
            metadata.append({
                "source_image": s["name"], "student_id": s["usn"], "augmentation_index": ai,
                "original_bbox": s["bbox"], "det_score": s["det"],
            })
    print(f"loaded {len(images)} images", flush=True)

    embs = []
    for i in range(0, len(images), 64):
        embs.append(np.asarray(fp.extract_embeddings_batch(app, images[i:i + 64]), dtype=np.float32))
        if (i // 64) % 20 == 0:
            print(f"  embeddings {i}/{len(images)}", flush=True)
    embs = np.concatenate(embs, axis=0)
    assert embs.shape == (len(images), 512)

    images_arr = np.stack(images).astype(np.uint8)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT, images=images_arr, embeddings=embs,
                        labels=np.array(labels, dtype=object), metadata=np.array(metadata, dtype=object))
    print(f"saved {OUT} ({OUT.stat().st_size / 1e6:.1f} MB) images={images_arr.shape}", flush=True)

    # Splits: one seeded shuffle per class, reused by both splits
    rng = random.Random(SEED)
    by_cls = defaultdict(list)
    for i, s in enumerate(sources):
        by_cls[s["usn"]].append(i)
    orders = {}
    for usn in usns:
        o = list(by_cls[usn])
        rng.shuffle(o)
        orders[usn] = o

    rows = []
    for tag, ratios in SPLITS.items():
        split, short = make_split(sources, usns, ratios, orders)
        sidx = assert_no_leakage(tag, split, sources, meta_by_sample)
        js = {
            "split": tag, "ratios": dict(zip(("train", "val", "test"), ratios)), "seed": SEED,
            "unit": "source photo", "min_per_class_val_test": MIN_PER_SPLIT,
            "classes": usns, "classes_below_min": short,
            "val_test_use_only_augmentation_index": 0, "train_uses_augmentation_index": "0-30",
            "n_samples": {k: len(v) for k, v in sidx.items()},
            "n_photos": {k: len(v) for k, v in split.items()},
        }
        for k, v in split.items():
            js[k] = [{"usn": sources[i]["usn"], "source_image": sources[i]["name"], "md5": sources[i]["md5"]}
                     for i in sorted(v, key=lambda i: (sources[i]["usn"], sources[i]["name"]))]
        (V3 / f"splits_{tag}.json").write_text(json.dumps(js, indent=1))
        print(f"[{tag}] photos {js['n_photos']} samples {js['n_samples']} below-min {short}", flush=True)
        for usn in usns:
            r = {"split": tag, "usn": usn, "photos_total": len(by_cls[usn])}
            for k in ("train", "val", "test"):
                ph = [i for i in split[k] if sources[i]["usn"] == usn]
                r[f"{k}_photos"] = len(ph)
                r[f"{k}_samples"] = sum(len(meta_by_sample[i]) for i in ph) if k == "train" else len(ph)
            rows.append(r)
    with open(V3 / "split_counts.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()


