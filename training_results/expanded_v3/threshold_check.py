"""Threshold sanity calibration for the promoted v3 Split B classifier (CPU, app preprocessing).
Uses vista.vision.personal_classifier with VISTA_FACE_MODEL set to the v3 Split B checkpoint.
Sets: (1) Split B TEST clean crops (npz aug idx 0), (2) raw TEST photos, face-detected + bbox-cropped
like recognize._crop_face, (3) non-students: ex-student 1DA22AI402 photos (from git HEAD), non-face crops, noise.
Not a new accuracy claim; no tuning on train."""
import json, os, subprocess, sys, random
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "training_results" / "expanded_v3"
os.environ["VISTA_FACE_MODEL"] = str(OUT / "best_model_expanded_v3_splitB.pth")
os.environ.pop("VISTA_FACE_MODEL_DEVICE", None)
sys.path.insert(0, str(ROOT))
import cv2
import numpy as np
import torch
from vista.vision import personal_classifier as pc
from vista.vision import facial_pipeline as fp

random.seed(0)
np.random.seed(0)
model, classes, pre = pc._load_model()


def probs(rgb):
    img = pc.Image.fromarray(rgb.astype(np.uint8), mode="RGB")
    with torch.inference_mode():
        return torch.softmax(model(pre(img).unsqueeze(0)), 1)[0].numpy()


def pred(rgb):
    p = probs(rgb)
    return classes[int(p.argmax())], float(p.max())


sp = json.loads((OUT / "splits_B.json").read_text(encoding="utf-8"))
test = sp["test"]
d = np.load(ROOT / "data" / "processed" / "facial_pipeline_results_expanded_v3.npz", allow_pickle=True)
imgs, meta = d["images"], d["metadata"]
rows = {}
for i, m in enumerate(meta):
    m = m.item() if hasattr(m, "item") else m
    if int(m["augmentation_index"]) == 0:
        rows[(m["student_id"], m["source_image"])] = i

res = {"threshold_candidates": [0.60, 0.55, 0.50, 0.45, 0.40, 0.35, 0.30]}


def summarize(recs):
    c = np.array([r["conf"] for r in recs if r["ok"]])
    w = np.array([r["conf"] for r in recs if not r["ok"]])
    s = lambda a: ({"n": int(len(a)), "min": float(a.min()), "p05": float(np.percentile(a, 5)), "p25": float(np.percentile(a, 25)),
                    "median": float(np.median(a)), "mean": float(a.mean()), "max": float(a.max())} if len(a) else {"n": 0})
    out = {"n": len(recs), "correct": s(c), "wrong": s(w)}
    out["correct_below"] = {str(t): int((c < t).sum()) for t in res["threshold_candidates"]}
    out["wrong_at_or_above"] = {str(t): int((w >= t).sum()) for t in res["threshold_candidates"]}
    out["wrong_confs"] = sorted(float(x) for x in w)
    return out


# 1) clean crops
clean = []
for e in test:
    rgb = imgs[rows[(e["usn"], e["source_image"])]]
    p, c = pred(rgb)
    clean.append({"usn": e["usn"], "img": e["source_image"], "pred": p, "conf": c, "ok": p == e["usn"]})
res["clean_test"] = summarize(clean)

# 2) raw test photos, detector + bbox crop (as the app does)
app = fp.initialize_face_detector()
by = {}
for e in test:
    by.setdefault(e["usn"], []).append(e)
raw = []
for usn, es in by.items():
    for e in sorted(es, key=lambda x: x["source_image"])[:3]:
        path = ROOT / "dataset" / usn / e["source_image"]
        bgr = cv2.imread(str(path))
        faces = app.get(bgr) if bgr is not None else []
        if not faces:
            raw.append({"usn": usn, "img": e["source_image"], "pred": None, "conf": None, "ok": False, "nodet": True})
            continue
        f = max(faces, key=lambda x: x.det_score)
        h, w = bgr.shape[:2]
        x1, y1, x2, y2 = [int(v) for v in f.bbox[:4]]
        x1, y1, x2, y2 = max(0, x1), max(0, y1), min(w, x2), min(h, y2)
        crop = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)[y1:y2, x1:x2].copy()
        p, c = pred(crop)
        raw.append({"usn": usn, "img": e["source_image"], "pred": p, "conf": c, "ok": p == usn})
nodet = [r for r in raw if r.get("nodet")]
raw_det = [r for r in raw if not r.get("nodet")]
res["raw_test"] = summarize(raw_det)
res["raw_test"]["no_face_detected"] = len(nodet)

# 3) non-students
neg = []
tmp = OUT / "_tmp_neg"
tmp.mkdir(exist_ok=True)
lst = subprocess.run(["git", "ls-tree", "-r", "--name-only", "HEAD", "dataset/1DA22AI402"], cwd=ROOT, capture_output=True, text=True).stdout.split()
for name in random.sample(lst, min(5, len(lst))):
    blob = subprocess.run(["git", "show", f"HEAD:{name}"], cwd=ROOT, capture_output=True).stdout
    (tmp / Path(name).name).write_bytes(blob)
    bgr = cv2.imread(str(tmp / Path(name).name))
    faces = app.get(bgr)
    if not faces:
        neg.append({"kind": "ex-student 1DA22AI402 (not a class)", "img": Path(name).name, "pred": None, "conf": None, "nodet": True})
        continue
    f = max(faces, key=lambda x: x.det_score)
    h, w = bgr.shape[:2]
    x1, y1, x2, y2 = [max(0, int(v)) for v in f.bbox[:4]]
    crop = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)[y1:min(h, y2), x1:min(w, x2)].copy()
    p, c = pred(crop)
    neg.append({"kind": "ex-student 1DA22AI402 (not a class)", "img": Path(name).name, "pred": p, "conf": c})
# non-face: random patches of a screenshot, noise, flat colour
shots = sorted((ROOT / "docs" / "screenshots").glob("*.png"))[:3]
for s in shots:
    im = cv2.cvtColor(cv2.imread(str(s)), cv2.COLOR_BGR2RGB)
    h, w = im.shape[:2]
    y, x = random.randint(0, h - 200), random.randint(0, w - 200)
    p, c = pred(im[y:y + 200, x:x + 200].copy())
    neg.append({"kind": "non-face UI screenshot patch", "img": s.name, "pred": p, "conf": c})
# non-face: background (floor/wall) patch from a raw photo corner
bgr = cv2.imread(str(ROOT / "dataset" / "1DA23AI001" / "IMG_20260824_105001.jpg"))
h, w = bgr.shape[:2]
p, c = pred(cv2.cvtColor(bgr[:h // 6, :w // 6].copy(), cv2.COLOR_BGR2RGB))
neg.append({"kind": "non-face background patch of raw photo", "img": "corner", "pred": p, "conf": c})
p, c = pred(np.random.randint(0, 255, (160, 160, 3), dtype=np.uint8))
neg.append({"kind": "random noise", "img": "noise", "pred": p, "conf": c})
p, c = pred(np.full((160, 160, 3), 128, np.uint8))
neg.append({"kind": "flat gray", "img": "gray", "pred": p, "conf": c})
res["non_students"] = neg
for f in tmp.iterdir():
    f.unlink()
tmp.rmdir()

(OUT / "threshold_check_results.json").write_text(json.dumps(res, indent=1), encoding="utf-8")

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 4))
    bins = np.linspace(0, 1, 41)
    allr = clean + raw_det
    ax.hist([r["conf"] for r in allr if r["ok"]], bins, alpha=.7, label="correct")
    ax.hist([r["conf"] for r in allr if not r["ok"]], bins, alpha=.7, label="wrong")
    ax.hist([r["conf"] for r in neg if r["conf"] is not None], bins, alpha=.7, label="non-student")
    ax.axvline(0.60, ls="--", c="k")
    ax.set_xlabel("max softmax"); ax.legend(); ax.set_title("v3 Split B confidence (test clean + raw, non-students)")
    fig.tight_layout(); fig.savefig(OUT / "threshold_check.png", dpi=120)
except Exception as ex:
    print("png skipped", ex)

for k in ("clean_test", "raw_test"):
    r = res[k]
    print(k, "n", r["n"], "correct", r["correct"], "\n wrong", r["wrong"], "\n below", r["correct_below"], "\n wrong>=", r["wrong_at_or_above"])
print("raw no face", len(nodet))
for n in neg:
    print(n)
