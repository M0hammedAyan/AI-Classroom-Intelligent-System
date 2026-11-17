"""Step 5 e2e: API mark-batch with held-out (Split B test) photos + in-process gallery/classifier decider log.
Usage: python e2e_test.py api|decider   (api needs backend on :8002)"""
import base64, json, os, sys, io
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "training_results" / "expanded_v3"
sys.path.insert(0, str(ROOT))
import cv2, numpy as np

D = ROOT / "dataset"
TMP = OUT / "e2e_inputs"
TMP.mkdir(exist_ok=True)


def collage():
    ps = [D / "1DA23AI004" / "x", D / "1DA25AI005" / "x", D / "1DA24AI403" / "IMG_20260824_111315_006.jpg"]
    sp = json.loads((OUT / "splits_B.json").read_text())
    ims = []
    for u in ["1DA23AI004", "1DA25AI005", "1DA24AI403"]:
        e = [x for x in sp["test"] if x["usn"] == u][0]
        im = cv2.imread(str(D / u / e["source_image"]))
        im = cv2.resize(im, (int(im.shape[1] * 600 / im.shape[0]), 600))
        ims.append(im)
    p = TMP / "group_collage.jpg"
    cv2.imwrite(str(p), np.hstack(ims))
    return p


def noise_and_blank():
    rng = np.random.RandomState(1)
    cv2.imwrite(str(TMP / "noise.jpg"), rng.randint(0, 255, (480, 640, 3), dtype=np.uint8))
    cv2.imwrite(str(TMP / "gray.jpg"), np.full((480, 640, 3), 128, np.uint8))
    return TMP / "noise.jpg", TMP / "gray.jpg"


def cases():
    sp = json.loads((OUT / "splits_B.json").read_text())
    t = lambda u: sorted(e["source_image"] for e in sp["test"] if e["usn"] == u)
    n, g = noise_and_blank()
    c = [("original 1DA23AI001", D / "1DA23AI001" / t("1DA23AI001")[0], "1DA23AI001"),
         ("original 1DA24AI403", D / "1DA24AI403" / t("1DA24AI403")[0], "1DA24AI403"),
         ("new 1DA25AI003", D / "1DA25AI003" / t("1DA25AI003")[0], "1DA25AI003"),
         ("new 1DA25AI010", D / "1DA25AI010" / sorted(e["source_image"] for e in sp["test"] if e["usn"] == "1DA25AI010")[0], "1DA25AI010")]
    c += [(f"404 test photo {i}", D / "1DA24AI404" / f, "1DA24AI404") for i, f in enumerate(t("1DA24AI404"))]
    c += [("group collage (404-free: AI004+25AI005+AI403)", collage(), "multi"), ("non-face noise", n, None), ("non-face gray", g, None)]
    return c


if sys.argv[1] == "api":
    import requests
    B = "http://127.0.0.1:8002/api/v1"
    r = requests.post(B + "/auth/login", json={"email": "admin@vista.local", "password": "admin123"})
    tok = r.json().get("access_token") or r.json().get("token")
    H = {"Authorization": "Bearer " + tok}
    out = []
    for i, (name, path, exp) in enumerate(cases()):
        b64 = base64.b64encode(Path(path).read_bytes()).decode()
        body = {"image": b64, "classroom_id": "class-aiml-4a", "session_date": f"2099-01-{i + 1:02d}",
                "subject_id": "sub-ml101", "source": "upload", "is_extra_class": True, "extra_class_reason": "e2e test"}
        r = requests.post(B + "/attendance/mark-batch", json=body, headers=H)
        try:
            j = r.json()
        except Exception:
            j = r.text
        print(name, r.status_code, json.dumps(j)[:700])
        out.append({"case": name, "file": str(path), "expected": exp, "http": r.status_code, "resp": j, "session_date": body["session_date"]})
    (OUT / "e2e_results.json").write_text(json.dumps(out, indent=1))
else:
    os.environ["VISTA_DB_URL"] = "sqlite:///" + (ROOT / "vista/backend/vista_dev.db").as_posix()
    os.environ["VISTA_FACE_MODEL"] = str(OUT / "best_model_expanded_v3_splitB.pth")
    os.environ["VISTA_FACE_MODEL_THRESHOLD"] = "0.60"
    import importlib; rc = importlib.import_module('vista.vision.recognize')
    from vista.vision.personal_classifier import classify_face
    det = rc.get_detector()
    res = []
    for name, path, exp in cases():
        faces = det.detect(str(path))
        for k, f in enumerate(faces or []):
            gm = rc._match_student_gallery(f)
            row = {"case": name, "face": k, "expected": exp, "gallery": gm}
            if gm["matched"]:
                row["decider"] = "gallery"
            else:
                crop = rc._crop_face(str(path), f["bbox"])
                cr = classify_face(crop) if crop is not None else None
                row["classifier"] = cr
                row["decider"] = "classifier" if cr and cr.get("student_id") else "none (rejected)"
            res.append(row)
            print(json.dumps(row))
        if not faces:
            print(json.dumps({"case": name, "faces": 0}))
            res.append({"case": name, "faces": 0})
    (OUT / "e2e_decider.json").write_text(json.dumps(res, indent=1))

