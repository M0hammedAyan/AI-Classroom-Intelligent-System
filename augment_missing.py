"""Augment only the images missing from 'agumented data' (S3), reusing facial_pipeline helpers.

Usage:
  python augment_missing.py                 # baseline 30-variant recipe for missing images
  python augment_missing.py --advanced      # advanced recipe -> agumented_data_advanced_test (3 images only)
Resume: progress is stored in .agents/tasks/dataset-expansion/s3-progress.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from vista.vision import facial_pipeline as fp  # noqa: E402

T = ROOT / ".agents" / "tasks" / "dataset-expansion"
DATASET = ROOT / "dataset"
OUT_BASE = ROOT / "agumented data"
OUT_ADV = ROOT / "agumented_data_advanced_test"
PROGRESS = T / "s3-progress.json"
PROGRESS_ADV = T / "s3-progress-advanced.json"
N = fp.AUGMENTATIONS_PER_FACE
ADV_LIMIT = 3
ADV_SAMPLE_USN = '1DA23AI001'


def not_in_roster() -> set[str]:
    audit = (T / "s1-audit.md").read_text(encoding="utf-8")
    return set(re.findall(r"^\| (\S+) \|.*\| not-in-roster \|$", audit, re.M))


def build_advanced_pipeline():
    import albumentations as A
    return A.Compose([
        A.MotionBlur(blur_limit=(3, 7), p=0.3),
        A.GaussianBlur(blur_limit=(3, 7), p=0.3),
        A.RandomShadow(p=0.4),
        A.Downscale(scale_range=(0.4, 0.8), p=0.4),
    ])


def load_progress(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"done": {}, "no_face": {}, "skipped_not_in_roster": []}


def save_progress(path: Path, prog: dict) -> None:
    path.write_text(json.dumps(prog, indent=1), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--advanced", action="store_true")
    args = ap.parse_args()

    missing = json.loads((T / "s1-missing.json").read_text(encoding="utf-8"))
    skip = not_in_roster()
    out_dir = OUT_ADV if args.advanced else OUT_BASE
    prog_path = PROGRESS_ADV if args.advanced else PROGRESS
    prog = load_progress(prog_path)
    prog["skipped_not_in_roster"] = sorted(u for u in missing if u in skip)

    jobs = [(u, i) for u, imgs in missing.items() if u not in skip for i in imgs]
    if args.advanced:  # unit check: first 3 images of an already-augmented roster student
        sample = sorted(p.name for p in (DATASET / ADV_SAMPLE_USN).glob('*.jpg'))[:ADV_LIMIT]
        jobs = [(ADV_SAMPLE_USN, n) for n in sample]
    todo = [(u, i) for u, i in jobs if f"{u}/{i}" not in prog["done"] and f"{u}/{i}" not in prog["no_face"]]
    print(f"jobs={len(jobs)} todo={len(todo)} skipped_not_in_roster={prog['skipped_not_in_roster']}", flush=True)
    if not todo:
        save_progress(prog_path, prog)
        return

    app = fp.initialize_face_detector()
    pipeline = build_advanced_pipeline() if args.advanced else fp.build_augmentation_pipeline()

    for u, name in todo:
        key = f"{u}/{name}"
        stem = Path(name).stem
        dest = out_dir / u / stem
        if not args.advanced and (dest / f"aug_{N-1:03d}.jpg").exists():
            prog["done"][key] = N  # never overwrite existing complete output
            save_progress(prog_path, prog)
            continue
        crop, _info = fp.extract_primary_face(app, str(DATASET / u / name))
        if crop is None:
            prog["no_face"][key] = True
            save_progress(prog_path, prog)
            continue
        face = fp.preprocess_face(crop, fp.TARGET_SIZE)
        dest.mkdir(parents=True, exist_ok=True)
        for k, img in enumerate(fp.augment_face(face, pipeline, N)):
            cv2.imwrite(str(dest / f"aug_{k:03d}.jpg"), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        prog["done"][key] = N
        save_progress(prog_path, prog)
        print(f"done {key}", flush=True)


if __name__ == "__main__":
    main()
