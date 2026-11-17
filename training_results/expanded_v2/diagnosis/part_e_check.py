import numpy as np, collections
d = np.load("data/processed/facial_pipeline_results_expanded.npz", allow_pickle=True)
L = d["labels"]; M = d["metadata"]; im = d["images"]
print("N", len(L), "imgs", im.shape, im.dtype, "meta keys", list(M[0].keys()))
idx = collections.defaultdict(dict)
for i, (l, m) in enumerate(zip(L, M)):
    idx[(str(l), m["source_image"])][int(m["augmentation_index"])] = i
bad = [k for k, v in idx.items() if sorted(v) != list(range(30))]
print("sources", len(idx), "sources not exactly aug 0..29:", len(bad))
cls = collections.Counter(k[0] for k in idx)
print("classes", len(cls), "min/max sources per class", min(cls.values()), max(cls.values()))
per_cls_ok = {c: all(len(v) == 30 for k, v in idx.items() if k[0] == c) for c in cls}
print("classes with exactly 30 aug per source:", sum(per_cls_ok.values()), "/", len(cls))
new = [k for k in idx if k[0].startswith("1DA25")]
old = [k for k in idx if not k[0].startswith("1DA25")]
for nm, g in (("old20", old), ("new12", new)):
    ds = [M[idx[k][0]]["det_score"] for k in g]
    print(nm, "sources", len(g), "samples", len(g) * 30, "det_score mean %.4f min %.4f" % (np.mean(ds), np.min(ds)))
# is aug0 unaugmented? count sources where aug0 equals no other variant, and
# whether any variant equals another (identity transform drawn)
def n_identical_to_0(k):
    a = im[idx[k][0]]
    return sum(np.array_equal(a, im[idx[k][j]]) for j in range(1, 30))
for nm, g in (("old20", old), ("new12", new)):
    # estimate the fraction of variants that are pixel-identical to each other (i.e. no-op draws)
    noop = []
    for k in g:
        arrs = [im[idx[k][j]] for j in range(30)]
        noop.append(len({a.tobytes() for a in arrs}))
    print(nm, "mean distinct images among 30 variants per source: %.2f" % np.mean(noop),
          "| sources with aug0 identical to another variant:", sum(n_identical_to_0(k) > 0 for k in g))
# aug0 vs a reference: share of aug0 that differ from the clean resized crop cannot be known; use blur/noise proxy
def hf(a):
    g = a.astype(np.float32).mean(2)
    return float(np.abs(np.diff(g, axis=0)).mean())
for nm, g in (("old20", old), ("new12", new)):
    print(nm, "aug0 hi-freq energy %.2f | aug1-29 mean %.2f" % (
        np.mean([hf(im[idx[k][0]]) for k in g[:150]]),
        np.mean([hf(im[idx[k][j]]) for k in g[:150] for j in (1, 7, 15)])))
