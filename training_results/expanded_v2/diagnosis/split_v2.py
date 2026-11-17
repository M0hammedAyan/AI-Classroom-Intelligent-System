"""Reusable v2 split: stratified by source photo (usn, source_image).

split_by_photo(keys, val_ratio, test_ratio, seed, min_val=2, min_test=2)
  keys: iterable of (usn, source_image) unique photos.
  Returns (train, val, test, flags): three lists of keys and a dict
  usn -> note for classes that could not meet the minimum.

Per class (photos shuffled with a per-class RNG derived from seed + usn, so
Split A and B use the same ordering and B's val/test are supersets of A's):
  n_val  = max(min_val,  round(n * val_ratio))
  n_test = max(min_test, round(n * test_ratio))
  If n < n_val + n_test + 1 (need at least 1 train photo), fall back:
     n >= 3 -> 1 val / 1 test (flag "fallback_1_1")
     n <= 2 -> all photos stay in train, no val/test (flag "no_eval_photos")
  No data is created or duplicated. Val/test contain photos only; the caller
  maps val/test to augmentation_index==0 rows and train to all augmented rows.
"""
import hashlib
import random
from collections import defaultdict


def _rng(seed, usn):
    h = int(hashlib.md5(f"{seed}:{usn}".encode()).hexdigest()[:8], 16)
    return random.Random(h)


def split_by_photo(keys, val_ratio, test_ratio, seed=42, min_val=2, min_test=2):
    by_cls = defaultdict(list)
    for k in sorted(set(keys)):
        by_cls[k[0]].append(k)
    train, val, test, flags = [], [], [], {}
    for usn in sorted(by_cls):
        photos = by_cls[usn][:]
        _rng(seed, usn).shuffle(photos)
        n = len(photos)
        nv = max(min_val, round(n * val_ratio))
        nt = max(min_test, round(n * test_ratio))
        if n < nv + nt + 1:
            if n >= 3:
                nv, nt = 1, 1
                flags[usn] = f"fallback_1_1 (n={n})"
            else:
                nv, nt = 0, 0
                flags[usn] = f"no_eval_photos (n={n})"
        val += photos[:nv]
        test += photos[nv:nv + nt]
        train += photos[nv + nt:]
    return train, val, test, flags
