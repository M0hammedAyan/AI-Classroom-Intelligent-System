"""Regenerate stale/missing augmentation for expanded_v3 (resumable).

- Students in regen_list.json["regen"]: move any existing "agumented data/<USN>" to
  "agumented data_stale_v1/<USN>" (never deleted), then write
  agumented data/<USN>/<IMG>/aug_000..029.jpg + clean.jpg.
- Students in regen_list.json["keep"]: write clean crops only to
  training_results/expanded_v3/clean_crops/<USN>/<IMG>.jpg (existing aug folders untouched).
- Photos in exclude_photos are skipped. Photos with no face are logged and skipped.
- Recipe: vista.vision.facial_pipeline (SCRFD buffalo_l, primary = highest det_score,
  resize 160x160, build_augmentation_pipeline(), 30 variants).
Progress is stored in training_results/expanded_v3/regen_progress.json.
"""
import json
import shutil
import sys
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from vista.vision import facial_pipeline as fp  # noqa: E402

DATASET = ROOT / "dataset"
AUG = ROOT / "agumented data"
STALE = ROOT / "agumented data_stale_v1"
V3 = ROOT / "training_results" / "expanded_v3"
CLEAN = V3 / "clean_crops"
PROGRESS = V3 / "regen_progress.json"
REGEN = V3 / "diagnosis" / "regen_list.json"
EXT = {".jpg", ".jpeg", ".png"}
N_AUG = 30


def load_progress():
    if PROGRESS.exists():
        return json.loads(PROGRESS.read_text())
    return {"moved": {}, "done": {}, "no_face": [], "excluded": [], "counts": {}}


def save_progress(p):
    tmp = PROGRESS.with_suffix(".tmp")
    tmp.write_text(json.dumps(p, indent=1))
    tmp.replace(PROGRESS)


def main():
    cfg = json.loads(REGEN.read_text())
    excl = {e.replace("\\", "/") for e in cfg["exclude_photos"]}
    prog = load_progress()
    # state before (once)
    if "before" not in prog:
        prog["before"] = {}
        for usn in cfg["regen"] + cfg["keep"]:
            d = AUG / usn
            prog["before"][usn] = {
                "photos_in_dataset": len([f for f in (DATASET / usn).iterdir() if f.suffix.lower() in EXT]),
                "aug_photo_folders": len([x for x in d.iterdir() if x.is_dir()]) if d.exists() else 0,
                "aug_files": len(list(d.rglob("aug_*.jpg"))) if d.exists() else 0,
            }
        save_progress(prog)

    # 1. move stale folders (regen students only)
    for usn in cfg["regen"]:
        src = AUG / usn
        if src.exists() and usn not in prog["moved"]:
            STALE.mkdir(exist_ok=True)
            shutil.move(str(src), str(STALE / usn))
            prog["moved"][usn] = str(STALE / usn)
            save_progress(prog)

    app = fp.initialize_face_detector()
    pipe = fp.build_augmentation_pipeline()

    jobs = [(u, "regen") for u in cfg["regen"]] + [(u, "keep") for u in cfg["keep"]]
    for usn, mode in jobs:
        done = set(prog["done"].get(usn, []))
        for img in sorted(p for p in (DATASET / usn).iterdir() if p.suffix.lower() in EXT):
            key = f"{usn}/{img.name}"
            if img.name in done:
                continue
            if key in excl:
                if key not in prog["excluded"]:
                    prog["excluded"].append(key)
                done.add(img.name)
                prog["done"][usn] = sorted(done)
                save_progress(prog)
                continue
            crop, info = fp.extract_primary_face(app, str(img))
            if crop is None:
                if key not in prog["no_face"]:
                    prog["no_face"].append(key)
            else:
                face = fp.preprocess_face(crop)
                bgr = cv2.cvtColor(face, cv2.COLOR_RGB2BGR)
                if mode == "regen":
                    out = AUG / usn / img.stem
                    out.mkdir(parents=True, exist_ok=True)
                    cv2.imwrite(str(out / "clean.jpg"), bgr)
                    seed = int.from_bytes(key.encode()[-4:], "little") % (2**31)
                    pipe.set_random_seed(seed)
                    for i, a in enumerate(fp.augment_face(face, pipe, N_AUG)):
                        cv2.imwrite(str(out / f"aug_{i:03d}.jpg"), cv2.cvtColor(a, cv2.COLOR_RGB2BGR))
                else:
                    out = CLEAN / usn
                    out.mkdir(parents=True, exist_ok=True)
                    cv2.imwrite(str(out / f"{img.stem}.jpg"), bgr)
            done.add(img.name)
            prog["done"][usn] = sorted(done)
            save_progress(prog)
        print(f"{usn} ({mode}) done: {len(done)} photos", flush=True)

    # after counts
    for usn, mode in jobs:
        if mode == "regen":
            d = AUG / usn
            prog["counts"][usn] = {
                "aug_photo_folders": len([x for x in d.iterdir() if x.is_dir()]) if d.exists() else 0,
                "aug_files": len(list(d.rglob("aug_*.jpg"))) if d.exists() else 0,
                "clean_files": len(list(d.rglob("clean.jpg"))) if d.exists() else 0,
            }
        else:
            d = CLEAN / usn
            prog["counts"][usn] = {"clean_crops": len(list(d.glob("*.jpg"))) if d.exists() else 0}
    prog["finished"] = True
    save_progress(prog)
    print("FINISHED", flush=True)


if __name__ == "__main__":
    main()
