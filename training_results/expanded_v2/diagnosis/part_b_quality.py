import sys, os, csv, time
sys.path.insert(0, r"D:\CipherTECH\Projects\AI-Classroom-Intelligent-System")
import cv2, numpy as np
from pathlib import Path
from vista.vision.facial_pipeline import initialize_face_detector, preprocess_face

ROOT = Path(r"D:\CipherTECH\Projects\AI-Classroom-Intelligent-System")
OUT = ROOT / "training_results/expanded_v2/diagnosis/quality_per_photo.csv"
cols = ["usn","group","file","src_w","src_h","src_mp","n_faces","detected","det_score","second_score",
        "crop_w","crop_h","crop_side","face_frac","blur_lap_var","brightness","primary_is_largest"]
done = set()
if OUT.exists():
    with open(OUT, newline="") as f:
        done = {(r["usn"], r["file"]) for r in csv.DictReader(f)}
app = initialize_face_detector(providers=["CPUExecutionProvider"])
new = not OUT.exists()
fh = open(OUT, "a", newline="")
w = csv.DictWriter(fh, fieldnames=cols)
if new: w.writeheader()
t0 = time.time()
for d in sorted(p for p in (ROOT/"dataset").iterdir() if p.is_dir()):
    grp = "new" if d.name.startswith("1DA25AI") else "orig"
    for p in sorted(x for x in d.iterdir() if x.suffix.lower() in (".jpg", ".jpeg", ".png")):
        if (d.name, p.name) in done: continue
        r = dict.fromkeys(cols, "")
        r.update(usn=d.name, group=grp, file=p.name)
        img = cv2.imread(str(p))
        if img is None:
            r.update(detected=0, n_faces=-1); w.writerow(r); continue
        H, W = img.shape[:2]
        r.update(src_w=W, src_h=H, src_mp=round(W*H/1e6, 2))
        faces = app.get(img)
        r["n_faces"] = len(faces)
        if not faces:
            r["detected"] = 0; w.writerow(r); fh.flush(); continue
        faces = sorted(faces, key=lambda f: -f.det_score)
        f0 = faces[0]
        x1, y1, x2, y2 = f0.bbox.astype(int)
        x1 = max(0, min(x1, W-1)); y1 = max(0, min(y1, H-1)); x2 = max(0, min(x2, W)); y2 = max(0, min(y2, H))
        if x2 <= x1 or y2 <= y1:
            r["detected"] = 0; w.writerow(r); fh.flush(); continue
        crop = cv2.cvtColor(img[y1:y2, x1:x2], cv2.COLOR_BGR2RGB)
        c160 = preprocess_face(crop)
        g = cv2.cvtColor(c160, cv2.COLOR_RGB2GRAY)
        area = lambda f: (f.bbox[2]-f.bbox[0])*(f.bbox[3]-f.bbox[1])
        r.update(detected=1, det_score=round(float(f0.det_score), 4),
                 second_score=round(float(faces[1].det_score), 4) if len(faces) > 1 else "",
                 crop_w=x2-x1, crop_h=y2-y1, crop_side=round(((x2-x1)*(y2-y1))**0.5, 1),
                 face_frac=round((x2-x1)*(y2-y1)/(W*H), 4),
                 blur_lap_var=round(float(cv2.Laplacian(g, cv2.CV_64F).var()), 2),
                 brightness=round(float(g.mean()), 2),
                 primary_is_largest=int(area(f0) >= max(area(f) for f in faces)))
        w.writerow(r); fh.flush()
    print(d.name, round(time.time()-t0), flush=True)
fh.close()
