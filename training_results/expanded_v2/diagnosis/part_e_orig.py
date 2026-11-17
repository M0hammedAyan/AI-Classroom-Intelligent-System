import numpy as np, collections
d=np.load("data/processed/facial_pipeline_results.npz",allow_pickle=True)
L=d["labels"]; M=d["metadata"]
s=collections.defaultdict(set)
for l,m in zip(L,M): s[str(l)].add(m["source_image"])
print(len(L),len(s),sum(len(v) for v in s.values()))
print(sorted(s))
