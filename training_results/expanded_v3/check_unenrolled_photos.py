"""Check the 'non-enrolled person' photos (folder of an ex-student, read from git HEAD).
For every photo in that folder: MD5 identity with enrolled-student photos, ArcFace cosine to the nearest
enrolled-student photo, and Split B classifier prediction/confidence (app preprocessing, as threshold_check.py).
Output is anonymised (no USNs) and written to graphs_report/unenrolled_check.json."""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "training_results" / "expanded_v3"
os.environ["VISTA_FACE_MODEL"] = str(OUT / "best_model_expanded_v3_splitB.pth")
sys.path.insert(0, str(ROOT))
import cv2
import numpy as np
import torch
from vista.vision import personal_classifier as pc
from vista.vision import facial_pipeline as fp

EX = "1DA22AI402"          # folder of the removed student (internal, never printed)
SAMPLED = ["IMG_20260824_111434_745.jpg", "IMG_20260824_111446_544.jpg", "IMG_20260824_111142_782.jpg",
           "IMG_20260824_111324_003.jpg", "IMG_20260824_111538_979.jpg"]  # the 5 in threshold_check_results.json

model, classes, pre = pc._load_model()
app = fp.initialize_face_detector()


def git_files(folder):
    out = subprocess.run(["git", "ls-tree", "-r", "--name-only", "HEAD", folder], cwd=ROOT,
                         capture_output=True, text=True).stdout.split("\n")
    return [o for o in out if o.strip()]


def blob(name):
    return subprocess.run(["git", "show", f"HEAD:{name}"], cwd=ROOT, capture_output=True).stdout


def face(data):
    bgr = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    faces = app.get(bgr)
    if not faces:
        return None
    f = max(faces, key=lambda x: x.det_score)
    h, w = bgr.shape[:2]
    x1, y1, x2, y2 = [max(0, int(v)) for v in f.bbox[:4]]
    crop = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)[y1:min(h, y2), x1:min(w, x2)].copy()
    return crop, np.asarray(f.normed_embedding, dtype=np.float64)


# enrolled students' photos in HEAD (all other folders under dataset/), excluding the ex-student folder
all_files = [n for n in git_files("dataset") if n.lower().endswith((".jpg", ".jpeg", ".png"))]
ex_files = [n for n in all_files if f"/{EX}/" in n]
other = [n for n in all_files if f"/{EX}/" not in n]
print("ex-student photos in HEAD:", len(ex_files), "| other enrolled-folder photos in HEAD:", len(other))

other_md5 = {}
for n in other:
    other_md5.setdefault(hashlib.md5(blob(n)).hexdigest(), []).append(n.split("/")[1])
twin = None
rec = []
twin_embs = {}
for n in ex_files:
    data = blob(n)
    md5 = hashlib.md5(data).hexdigest()
    r = {"sampled_in_threshold_check": Path(n).name in SAMPLED, "byte_identical_to_enrolled": md5 in other_md5,
         "n_enrolled_owners_of_identical_file": len(set(other_md5.get(md5, [])))}
    if md5 in other_md5:
        owners = sorted(set(other_md5[md5]))
        twin = owners[0] if len(owners) == 1 else twin
    fc = face(data)
    if fc is None:
        r.update(face=False)
    else:
        crop, emb = fc
        with torch.inference_mode():
            pr = torch.softmax(model(pre(pc.Image.fromarray(crop, mode="RGB")).unsqueeze(0)), 1)[0].numpy()
        r.update(face=True, conf=float(pr.max()), _pred=classes[int(pr.argmax())], _emb=emb)
    rec.append(r)

# embeddings of the enrolled photos that share content / the predicted student, for the cosine check
pred_set = sorted({r["_pred"] for r in rec if r.get("face")})
print("distinct predicted identities among ex-student photos:", len(pred_set))
embs = {}
for p in pred_set:
    for n in [x for x in other if f"/{p}/" in x]:
        fc = face(blob(n))
        if fc:
            embs.setdefault(p, []).append(fc[1])
for r in rec:
    if r.get("face"):
        e = np.stack(embs[r["_pred"]])
        r["cos_to_nearest_photo_of_predicted_student"] = float((e @ r["_emb"]).max())
        r["cos_to_centroid_of_predicted_student"] = float((e.mean(0) / np.linalg.norm(e.mean(0))) @ r["_emb"])
        r["pred_is_enrolled_class"] = r["_pred"] in classes

def summ(rs):
    f = [r for r in rs if r.get("face")]
    c = [r["conf"] for r in f]
    return {"photos": len(rs), "face_detected": len(f), "byte_identical_to_an_enrolled_photo": sum(r["byte_identical_to_enrolled"] for r in rs),
            "pred_enrolled_class": sum(r.get("pred_is_enrolled_class", False) for r in f),
            "distinct_predicted_identities": len({r["_pred"] for r in f}),
            "conf_min": min(c) if c else None, "conf_max": max(c) if c else None,
            "cos_nearest_photo_min": min(r["cos_to_nearest_photo_of_predicted_student"] for r in f) if f else None,
            "cos_nearest_photo_max": max(r["cos_to_nearest_photo_of_predicted_student"] for r in f) if f else None,
            "cos_centroid_min": min(r["cos_to_centroid_of_predicted_student"] for r in f) if f else None,
            "cos_centroid_max": max(r["cos_to_centroid_of_predicted_student"] for r in f) if f else None,
            "conf_ge_0.60": sum(1 for x in c if x >= 0.60)}

out = {"all_photos_in_folder": summ(rec), "the_5_sampled_photos": summ([r for r in rec if r["sampled_in_threshold_check"]]),
       "only_sampled_found": sum(r["sampled_in_threshold_check"] for r in rec)}
(OUT / "graphs_report" / "unenrolled_check.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
