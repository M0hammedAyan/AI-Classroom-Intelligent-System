"""Inspect current facial_pipeline_results.npz and write a summary."""
import numpy as np
from pathlib import Path
from collections import Counter

NPZ = Path(r"D:\CipherTECH\Projects\AI-Classroom-Intelligent-System\data\processed\facial_pipeline_results.npz")

print(f"File: {NPZ}")
print(f"Exists: {NPZ.exists()}")
if not NPZ.exists():
    print("FILE NOT FOUND — nothing to inspect.")
    raise SystemExit(1)

print(f"Size: {NPZ.stat().st_size / 1024 / 1024:.2f} MB")

data = np.load(NPZ, allow_pickle=True)
print(f"\nKeys: {list(data.keys())}")

images     = data["images"]
embeddings = data["embeddings"]
labels     = data["labels"]
metadata   = data["metadata"]

print(f"\nimages     shape={images.shape}     dtype={images.dtype}")
print(f"embeddings shape={embeddings.shape} dtype={embeddings.dtype}")
print(f"labels     shape={labels.shape}     dtype={labels.dtype}")
print(f"metadata   shape={metadata.shape}   dtype={metadata.dtype}")

# Label distribution
counts = Counter(str(l) for l in labels)
print(f"\nStudents found: {len(counts)}")
print(f"\nPer-student sample counts:")
for usn in sorted(counts):
    print(f"  {usn}: {counts[usn]} samples")

# Embedding stats
print(f"\nEmbedding value range: [{embeddings.min():.4f}, {embeddings.max():.4f}]")
print(f"Embedding norms (first 5): {[round(float(np.linalg.norm(embeddings[i])),4) for i in range(5)]}")

# Metadata sample
m0 = metadata[0]
print(f"\nMetadata[0]: {m0}")
# Unique source images across all metadata
sources = set(str(m['source_image']) for m in metadata if hasattr(m, '__getitem__'))
print(f"Unique source images in metadata: {len(sources)}")

total = images.shape[0]
print(f"\nTotal samples: {total}")
print(f"Expected (21 students × ~30 imgs × 30 aug): {21*30*30}")
print("INSPECT DONE")
