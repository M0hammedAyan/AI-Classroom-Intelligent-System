import pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
D = r"D:\CipherTECH\Projects\AI-Classroom-Intelligent-System\training_results\expanded_v2\diagnosis"
df = pd.read_csv(f"{D}/quality_per_photo.csv")
met = ["src_mp","src_w","src_h","crop_side","face_frac","det_score","blur_lap_var","brightness"]
rows = []
for g, s in df.groupby("group"):
    for m in met:
        v = s[m].dropna()
        rows.append(dict(group=g, metric=m, n=len(v), mean=v.mean(), median=v.median(), std=v.std(), p10=v.quantile(.1), p90=v.quantile(.9)))
gr = pd.DataFrame(rows).round(3)
gr.to_csv(f"{D}/quality_groups.csv", index=False)
print(gr.pivot(index="metric", columns="group", values=["mean","median"]))
for m in met:
    a = df[df.group=="orig"][m].dropna(); b = df[df.group=="new"][m].dropna()
    print(m, "MWU p=%.2g" % stats.mannwhitneyu(a, b).pvalue)
# per student
ps = df.groupby("usn").agg(group=("group","first"), photos=("file","count"), failed=("detected", lambda x:(x==0).sum()),
     multi=("n_faces", lambda x:(x>1).sum()), nonlargest=("primary_is_largest", lambda x:(x==0).sum()),
     src_mp=("src_mp","median"), crop_side=("crop_side","median"), det=("det_score","median"),
     blur=("blur_lap_var","median"), bright=("brightness","median")).round(2)
ps.to_csv(f"{D}/quality_per_student.csv")
print(ps.to_string())
print(ps.groupby("group")[["photos","failed","multi","nonlargest"]].sum())
print("size dist", df.groupby(["group","src_w","src_h"]).size().sort_values(ascending=False).head(8))
mf = df[df.n_faces>1]
print("multi-face rows: min second_score/det by group"); print(mf.groupby("group")[["det_score","second_score"]].describe().T)
print("close competition (second>=0.6):", (mf.second_score>=0.6).groupby(mf.group).sum().to_dict())
fig, ax = plt.subplots(2, 4, figsize=(18, 8))
for a, m in zip(ax.ravel(), met):
    data = [df[df.group==g][m].dropna() for g in ("orig","new")]
    a.boxplot(data, tick_labels=["orig 20","new 12"])
    a.set_title(m + "  (med %.2f / %.2f)" % (data[0].median(), data[1].median()))
    if m in ("blur_lap_var","crop_side","src_mp"): a.set_yscale("log")
plt.tight_layout(); plt.savefig(f"{D}/quality_comparison.png", dpi=110)
