import numpy as np, pandas as pd, os
from PIL import Image
D = r'training_results/expanded_v2/diagnosis'
os.makedirs(D + '/contact_sheets', exist_ok=True)
d = np.load('data/processed/facial_pipeline_results_expanded.npz', allow_pickle=True)
img, emb, lab, meta = d['images'], d['embeddings'], d['labels'].astype(str), d['metadata']
aug = np.array([m['augmentation_index'] for m in meta]); src = np.array([m['source_image'] for m in meta])
cls = sorted(set(lab)); new = [c for c in cls if c.startswith('1DA25AI0') and 1 <= int(c[-3:]) <= 12]
old = [c for c in cls if c not in new]
rng = np.random.RandomState(42)
orig3 = list(rng.choice(old, 3, replace=False))
def sheet(c):
    idx = np.where((lab == c) & (aug == 0))[0]
    n = min(32, len(idx)); pick = np.random.RandomState(42).choice(idx, n, replace=False)
    g = np.zeros((4 * 160, 8 * 160, 3), np.uint8)
    for k, i in enumerate(pick): g[(k // 8) * 160:(k // 8 + 1) * 160, (k % 8) * 160:(k % 8 + 1) * 160] = img[i]
    Image.fromarray(g).save(f'{D}/contact_sheets/{c}.png'); return len(idx)
n0 = {c: sheet(c) for c in new + orig3}
print('sheets', {c: n0[c] for c in n0}, 'orig3', orig3)
means = {}; rows = []
for c in cls:
    m = lab == c; mu = emb[m].mean(0); mu /= np.linalg.norm(mu); means[c] = mu
    e = emb[m] / np.linalg.norm(emb[m], axis=1, keepdims=True); cs = e @ mu
    idxs = np.where(m)[0]
    for j in np.argsort(cs)[:5]:
        i = idxs[j]; rows.append(dict(usn=c, npz_index=i, source_image=src[i], aug_idx=aug[i], cos_to_class_mean=round(float(cs[j]), 4), class_mean_cos=round(float(cs.mean()), 4), class_min_cos=round(float(cs.min()), 4)))
pd.DataFrame(rows).to_csv(D + '/embedding_outliers.csv', index=False)
M = np.stack([means[c] for c in cls]); S = M @ M.T
pairs = [(cls[i], cls[j], float(S[i, j])) for i in range(len(cls)) for j in range(i + 1, len(cls))]
pairs.sort(key=lambda t: -t[2])
pd.DataFrame(pairs[:10], columns=['usn_a', 'usn_b', 'cosine']).round(4).to_csv(D + '/closest_pairs.csv', index=False)
print('top10'); [print(p) for p in pairs[:10]]
print('n pairs >0.9:', sum(p[2] > 0.9 for p in pairs))
# per class summary: unique photos, within-class mean cos, fraction of aug0 samples with cos<0.3 (unaugmented-only)
for c in new + orig3:
    m = (lab == c); a0 = m & (aug == 0)
    e = emb[a0] / np.linalg.norm(emb[a0], axis=1, keepdims=True); cs = e @ means[c]
    print(c, 'photos', len(set(src[m])), 'aug0', a0.sum(), 'aug0 cos mean %.3f min %.3f p10 %.3f' % (cs.mean(), cs.min(), np.percentile(cs, 10)))
