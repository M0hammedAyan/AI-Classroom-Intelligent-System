# Diagnosis parts a, c, f

Source: `facial_pipeline_results_expanded.npz`, 30390 samples, 32 classes, 1013 unique (usn, source_image) photos.
Rows per photo distribution: {30: 1013}. Photos without aug_idx 0: 0. Photos with repeated aug_idx: 0. Photos whose file is missing in dataset/<USN>/: 0.

## a) Per-class table

Full table: `per_class.csv`. Photos shown as train/val/test photos; v1 = train_expanded.py split, v2 = split_v2.py.

| USN | grp | photos | samples | v1A tr/va/te | v1B tr/va/te | v2A tr/va/te | v2B tr/va/te | flags |
|---|---|---|---|---|---|---|---|---|
| 1DA22AI402 | original | 34 | 1020 | 28/3/3 | 24/5/5 | 28/3/3 | 24/5/5 |  |
| 1DA23AI001 | original | 39 | 1170 | 31/4/4 | 27/6/6 | 31/4/4 | 27/6/6 |  |
| 1DA23AI004 | original | 29 | 870 | 23/3/3 | 21/4/4 | 23/3/3 | 21/4/4 |  |
| 1DA23AI005 | original | 39 | 1170 | 31/4/4 | 27/6/6 | 31/4/4 | 27/6/6 |  |
| 1DA23AI009 | original | 35 | 1050 | 28/4/3 | 25/5/5 | 27/4/4 | 25/5/5 |  |
| 1DA23AI011 | original | 27 | 810 | 21/3/3 | 19/4/4 | 21/3/3 | 19/4/4 |  |
| 1DA23AI024 | original | 27 | 810 | 21/3/3 | 19/4/4 | 21/3/3 | 19/4/4 |  |
| 1DA23AI025 | original | 38 | 1140 | 30/4/4 | 26/6/6 | 30/4/4 | 26/6/6 |  |
| 1DA23AI031 | original | 34 | 1020 | 28/3/3 | 24/5/5 | 28/3/3 | 24/5/5 |  |
| 1DA23AI033 | original | 41 | 1230 | 33/4/4 | 29/6/6 | 33/4/4 | 29/6/6 |  |
| 1DA23AI036 | original | 28 | 840 | 22/3/3 | 20/4/4 | 22/3/3 | 20/4/4 |  |
| 1DA23AI042 | original | 33 | 990 | 27/3/3 | 23/5/5 | 27/3/3 | 23/5/5 |  |
| 1DA23AI044 | original | 38 | 1140 | 30/4/4 | 26/6/6 | 30/4/4 | 26/6/6 |  |
| 1DA23AI047 | original | 36 | 1080 | 28/4/4 | 26/5/5 | 28/4/4 | 26/5/5 |  |
| 1DA23AI049 | original | 33 | 990 | 27/3/3 | 23/5/5 | 27/3/3 | 23/5/5 |  |
| 1DA23AI050 | original | 30 | 900 | 24/3/3 | 21/5/4 | 24/3/3 | 22/4/4 |  |
| 1DA23AI055 | original | 35 | 1050 | 28/4/3 | 25/5/5 | 27/4/4 | 25/5/5 |  |
| 1DA23AI059 | original | 32 | 960 | 26/3/3 | 22/5/5 | 26/3/3 | 22/5/5 |  |
| 1DA24AI403 | original | 33 | 990 | 27/3/3 | 23/5/5 | 27/3/3 | 23/5/5 |  |
| 1DA24AI404 | original | 30 | 900 | 24/3/3 | 21/4/5 | 24/3/3 | 22/4/4 |  |
| 1DA25AI001 | new | 30 | 900 | 24/3/3 | 21/4/5 | 24/3/3 | 22/4/4 |  |
| 1DA25AI002 | new | 31 | 930 | 25/3/3 | 21/5/5 | 25/3/3 | 21/5/5 |  |
| 1DA25AI003 | new | 26 | 780 | 21/2/3 | 18/4/4 | 20/3/3 | 18/4/4 |  |
| 1DA25AI004 | new | 30 | 900 | 24/3/3 | 21/5/4 | 24/3/3 | 22/4/4 |  |
| 1DA25AI005 | new | 27 | 810 | 21/3/3 | 19/4/4 | 21/3/3 | 19/4/4 |  |
| 1DA25AI006 | new | 27 | 810 | 21/3/3 | 19/4/4 | 21/3/3 | 19/4/4 |  |
| 1DA25AI007 | new | 31 | 930 | 25/3/3 | 21/5/5 | 25/3/3 | 21/5/5 |  |
| 1DA25AI008 | new | 30 | 900 | 24/3/3 | 21/4/5 | 24/3/3 | 22/4/4 |  |
| 1DA25AI009 | new | 30 | 900 | 24/3/3 | 21/5/4 | 24/3/3 | 22/4/4 |  |
| 1DA25AI010 | new | 27 | 810 | 21/3/3 | 19/4/4 | 21/3/3 | 19/4/4 |  |
| 1DA25AI011 | new | 27 | 810 | 21/3/3 | 19/4/4 | 21/3/3 | 19/4/4 |  |
| 1DA25AI012 | new | 26 | 780 | 21/2/3 | 18/4/4 | 20/3/3 | 18/4/4 |  |

Classes with <10 unique photos: 0 []
Photos per class: min 26, median 31, max 41. Original-20 mean 33.5, new-12 mean 28.5.
- v1 Split A: val 102 samples, test 102 samples; classes with <2 val or <2 test photos: 0 []
- v2 Split A: val 104 samples, test 104 samples; classes with <2 val or <2 test photos: 0 []
- v1 Split B: val 152 samples, test 152 samples; classes with <2 val or <2 test photos: 0 []
- v2 Split B: val 149 samples, test 149 samples; classes with <2 val or <2 test photos: 0 []

## c) Leakage check

Code review of `train_expanded.split_npz` (read, not edited): groups rows by (usn, source_image); `train_test_split` on the unique photo list, stratified by class, seed 42; train gets all rows of train photos, val/test get only rows with aug_idx==0 of their photos. So the split is by photo and val/test hold clean crops only. Weakness: `sklearn` stratification is on photo counts per class, so it does not guarantee 2 val/2 test photos per class (see a/f).

Reproduction of the v1 log: my re-implementation of the split vs the sections in `data_split_expanded_log.txt`. The log is unreliable for exact comparison: A and B were written concurrently, so TRAIN/VAL/TEST sections of the two splits are interleaved (e.g. the B TRAIN header is at line 6, the A header at line 1288, and the 'TEST 152' section spans 3,400 lines). Only sections that match byte-for-byte as sets are reported True; False means 'not verifiable from the log', not 'different split'. Sample counts do agree with the log (A: 24270/102/102, B: 21270/152/152).
- Split A: {'TRAIN': False, 'VAL': True, 'TEST': True}
- Split B: {'TRAIN': False, 'VAL': False, 'TEST': False}

Assertion run on actual index sets (index overlap, aug_idx==0 only, no shared (usn, source) photo, one row per eval photo):
- v1 Split A: PASS (train 24270 rows/809 photos, val 102/102, test 102/102); index overlap 0, non-aug0 in val/test 0, shared photos 0
  exact-duplicate files: eval vs train = 58 (of which different USN = 58, same USN = 0), val vs test = 8
    ('val', ('1DA25AI011', 'IMG_20261112_151225.jpg'), ('1DA25AI005', 'IMG_20261112_151225.jpg'))
    ('val', ('1DA25AI009', 'IMG_20261112_151858.jpg'), ('1DA25AI001', 'IMG_20261112_151858.jpg'))
    ('val', ('1DA25AI006', 'IMG_20261112_151737.jpg'), ('1DA25AI010', 'IMG_20261112_151737.jpg'))
    ('val', ('1DA25AI012', 'IMG_20261112_151015.jpg'), ('1DA25AI003', 'IMG_20261112_151015.jpg'))
    ('val', ('1DA25AI008', 'IMG_20261112_152114.jpg'), ('1DA25AI004', 'IMG_20261112_152114.jpg'))
    ('val', ('1DA25AI010', 'IMG_20261112_151615.jpg'), ('1DA25AI006', 'IMG_20261112_151615.jpg'))
    ('val', ('1DA25AI005', 'IMG_20261112_151239.jpg'), ('1DA25AI011', 'IMG_20261112_151239.jpg'))
    ('val', ('1DA25AI010', 'IMG_20261112_151653.jpg'), ('1DA25AI006', 'IMG_20261112_151653.jpg'))
    ('val', ('1DA25AI011', 'IMG_20261112_151305.jpg'), ('1DA25AI005', 'IMG_20261112_151305.jpg'))
    ('val', ('1DA24AI403', 'IMG_20260824_111330_003.jpg'), ('1DA22AI402', 'IMG_20260824_111330_003.jpg'))
  near-duplicates (dHash hamming<=4, same class) eval vs train = 3
    ('val', ('1DA25AI009', 'IMG_20261112_151858.jpg'), ('1DA25AI009', 'IMG_20261112_151856.jpg'))
    ('val', ('1DA25AI012', 'IMG_20261112_151015.jpg'), ('1DA25AI012', 'IMG_20261112_151043.jpg'))
    ('test', ('1DA23AI004', 'IMG_20260824_105230_501.jpg'), ('1DA23AI004', 'IMG_20260824_105246_411.jpg'))
- v1 Split B: PASS (train 21270 rows/709 photos, val 152/152, test 152/152); index overlap 0, non-aug0 in val/test 0, shared photos 0
  exact-duplicate files: eval vs train = 89 (of which different USN = 89, same USN = 0), val vs test = 8
    ('val', ('1DA25AI001', 'IMG_20261112_151824.jpg'), ('1DA25AI009', 'IMG_20261112_151824.jpg'))
    ('val', ('1DA25AI006', 'IMG_20261112_151719.jpg'), ('1DA25AI010', 'IMG_20261112_151719.jpg'))
    ('val', ('1DA25AI004', 'IMG_20261112_152319.jpg'), ('1DA25AI008', 'IMG_20261112_152319.jpg'))
    ('val', ('1DA25AI010', 'IMG_20261112_151653.jpg'), ('1DA25AI006', 'IMG_20261112_151653.jpg'))
    ('val', ('1DA25AI002', 'IMG_20261112_152401.jpg'), ('1DA25AI007', 'IMG_20261112_152401.jpg'))
    ('val', ('1DA24AI403', 'IMG_20260824_111507_246.jpg'), ('1DA22AI402', 'IMG_20260824_111507_246.jpg'))
    ('val', ('1DA25AI003', 'IMG_20261112_151149.jpg'), ('1DA25AI012', 'IMG_20261112_151149.jpg'))
    ('val', ('1DA25AI009', 'IMG_20261112_151850.jpg'), ('1DA25AI001', 'IMG_20261112_151850.jpg'))
    ('val', ('1DA22AI402', 'IMG_20260824_111212_385.jpg'), ('1DA24AI403', 'IMG_20260824_111212_385.jpg'))
    ('val', ('1DA25AI009', 'IMG_20261112_151907.jpg'), ('1DA25AI001', 'IMG_20261112_151907.jpg'))
  near-duplicates (dHash hamming<=4, same class) eval vs train = 8
    ('val', ('1DA25AI004', 'IMG_20261112_152319.jpg'), ('1DA25AI004', 'IMG_20261112_152311.jpg'))
    ('val', ('1DA23AI049', 'IMG_20260824_113430_372.jpg'), ('1DA23AI049', 'IMG_20260824_113442_749.jpg'))
    ('val', ('1DA23AI047', 'IMG_6678.jpeg'), ('1DA23AI047', 'IMG_6676.jpeg'))
    ('test', ('1DA25AI009', 'IMG_20261112_151858.jpg'), ('1DA25AI009', 'IMG_20261112_151856.jpg'))
    ('test', ('1DA25AI001', 'IMG_20261112_151858.jpg'), ('1DA25AI001', 'IMG_20261112_151856.jpg'))
    ('test', ('1DA25AI007', 'IMG_20261112_152442.jpg'), ('1DA25AI007', 'IMG_20261112_152456.jpg'))
    ('test', ('1DA25AI012', 'IMG_20261112_151043.jpg'), ('1DA25AI012', 'IMG_20261112_151015.jpg'))
    ('test', ('1DA25AI003', 'IMG_20261112_151043.jpg'), ('1DA25AI003', 'IMG_20261112_151015.jpg'))
- v2 Split A: PASS (train 24150 rows/805 photos, val 104/104, test 104/104); index overlap 0, non-aug0 in val/test 0, shared photos 0
  exact-duplicate files: eval vs train = 64 (of which different USN = 64, same USN = 0), val vs test = 4
    ('val', ('1DA25AI011', 'IMG_20261112_151225.jpg'), ('1DA25AI005', 'IMG_20261112_151225.jpg'))
    ('val', ('1DA25AI011', 'IMG_20261112_151259.jpg'), ('1DA25AI005', 'IMG_20261112_151259.jpg'))
    ('val', ('1DA25AI006', 'IMG_20261112_151719.jpg'), ('1DA25AI010', 'IMG_20261112_151719.jpg'))
    ('val', ('1DA25AI008', 'IMG_20261112_152132.jpg'), ('1DA25AI004', 'IMG_20261112_152132.jpg'))
    ('val', ('1DA22AI402', 'IMG_20260824_111309_467.jpg'), ('1DA24AI403', 'IMG_20260824_111309_467.jpg'))
    ('val', ('1DA25AI010', 'IMG_20261112_151653.jpg'), ('1DA25AI006', 'IMG_20261112_151653.jpg'))
    ('val', ('1DA24AI403', 'IMG_20260824_111302_527.jpg'), ('1DA22AI402', 'IMG_20260824_111302_527.jpg'))
    ('val', ('1DA25AI009', 'IMG_20261112_151850.jpg'), ('1DA25AI001', 'IMG_20261112_151850.jpg'))
    ('val', ('1DA25AI001', 'IMG_20261112_151814.jpg'), ('1DA25AI009', 'IMG_20261112_151814.jpg'))
    ('val', ('1DA25AI006', 'IMG_20261112_151730.jpg'), ('1DA25AI010', 'IMG_20261112_151730.jpg'))
  near-duplicates (dHash hamming<=4, same class) eval vs train = 5
    ('test', ('1DA23AI047', 'IMG_6689.jpeg'), ('1DA23AI047', 'IMG_6690.jpeg'))
    ('test', ('1DA25AI004', 'IMG_20261112_152319.jpg'), ('1DA25AI004', 'IMG_20261112_152311.jpg'))
    ('test', ('1DA23AI047', 'IMG_6691.jpeg'), ('1DA23AI047', 'IMG_6695.jpeg'))
    ('test', ('1DA25AI007', 'IMG_20261112_152456.jpg'), ('1DA25AI007', 'IMG_20261112_152442.jpg'))
    ('test', ('1DA25AI001', 'IMG_20261112_151856.jpg'), ('1DA25AI001', 'IMG_20261112_151858.jpg'))
- v2 Split B: PASS (train 21450 rows/715 photos, val 149/149, test 149/149); index overlap 0, non-aug0 in val/test 0, shared photos 0
  exact-duplicate files: eval vs train = 73 (of which different USN = 73, same USN = 0), val vs test = 10
    ('val', ('1DA25AI011', 'IMG_20261112_151225.jpg'), ('1DA25AI005', 'IMG_20261112_151225.jpg'))
    ('val', ('1DA25AI011', 'IMG_20261112_151259.jpg'), ('1DA25AI005', 'IMG_20261112_151259.jpg'))
    ('val', ('1DA25AI006', 'IMG_20261112_151719.jpg'), ('1DA25AI010', 'IMG_20261112_151719.jpg'))
    ('val', ('1DA25AI008', 'IMG_20261112_152132.jpg'), ('1DA25AI004', 'IMG_20261112_152132.jpg'))
    ('val', ('1DA22AI402', 'IMG_20260824_111309_467.jpg'), ('1DA24AI403', 'IMG_20260824_111309_467.jpg'))
    ('val', ('1DA25AI010', 'IMG_20261112_151653.jpg'), ('1DA25AI006', 'IMG_20261112_151653.jpg'))
    ('val', ('1DA24AI403', 'IMG_20260824_111302_527.jpg'), ('1DA22AI402', 'IMG_20260824_111302_527.jpg'))
    ('val', ('1DA25AI009', 'IMG_20261112_151850.jpg'), ('1DA25AI001', 'IMG_20261112_151850.jpg'))
    ('val', ('1DA25AI006', 'IMG_20261112_151730.jpg'), ('1DA25AI010', 'IMG_20261112_151730.jpg'))
    ('val', ('1DA25AI003', 'IMG_20261112_151024.jpg'), ('1DA25AI012', 'IMG_20261112_151024.jpg'))
  near-duplicates (dHash hamming<=4, same class) eval vs train = 7
    ('val', ('1DA25AI007', 'IMG_20261112_152456.jpg'), ('1DA25AI007', 'IMG_20261112_152442.jpg'))
    ('test', ('1DA23AI047', 'IMG_6689.jpeg'), ('1DA23AI047', 'IMG_6690.jpeg'))
    ('test', ('1DA25AI004', 'IMG_20261112_152319.jpg'), ('1DA25AI004', 'IMG_20261112_152311.jpg'))
    ('test', ('1DA23AI004', 'IMG_20260824_105230_501.jpg'), ('1DA23AI004', 'IMG_20260824_105246_411.jpg'))
    ('test', ('1DA23AI036', 'IMG_20260824_112732_409.jpg'), ('1DA23AI036', 'IMG_20260824_112734_114.jpg'))
    ('test', ('1DA25AI001', 'IMG_20261112_151856.jpg'), ('1DA25AI001', 'IMG_20261112_151858.jpg'))
    ('test', ('1DA23AI047', 'IMG_6695.jpeg'), ('1DA23AI047', 'IMG_6690.jpeg'))

Dataset files hashed: 1018 (SHA-256 of files in dataset/<USN>/). Distinct hashes: 813.
Identical-content file groups inside dataset/: 205
  [('1DA22AI402', 'IMG_20260824_111130_071.jpg'), ('1DA24AI403', 'IMG_20260824_111130_071.jpg')]
  [('1DA22AI402', 'IMG_20260824_111135_732.jpg'), ('1DA24AI403', 'IMG_20260824_111135_732.jpg')]
  [('1DA22AI402', 'IMG_20260824_111142_782.jpg'), ('1DA24AI403', 'IMG_20260824_111142_782.jpg')]
  [('1DA22AI402', 'IMG_20260824_111148_564.jpg'), ('1DA24AI403', 'IMG_20260824_111148_564.jpg')]
  [('1DA22AI402', 'IMG_20260824_111157_699.jpg'), ('1DA24AI403', 'IMG_20260824_111157_699.jpg')]
  [('1DA22AI402', 'IMG_20260824_111204_147.jpg'), ('1DA24AI403', 'IMG_20260824_111204_147.jpg')]
  [('1DA22AI402', 'IMG_20260824_111212_385.jpg'), ('1DA24AI403', 'IMG_20260824_111212_385.jpg')]
  [('1DA22AI402', 'IMG_20260824_111217_328.jpg'), ('1DA24AI403', 'IMG_20260824_111217_328.jpg')]
  [('1DA22AI402', 'IMG_20260824_111226_047.jpg'), ('1DA24AI403', 'IMG_20260824_111226_047.jpg')]
  [('1DA22AI402', 'IMG_20260824_111231_203.jpg'), ('1DA24AI403', 'IMG_20260824_111231_203.jpg')]
  [('1DA22AI402', 'IMG_20260824_111238_538.jpg'), ('1DA24AI403', 'IMG_20260824_111238_538.jpg')]
  [('1DA22AI402', 'IMG_20260824_111244_071.jpg'), ('1DA24AI403', 'IMG_20260824_111244_071.jpg')]
  [('1DA22AI402', 'IMG_20260824_111258_401.jpg'), ('1DA24AI403', 'IMG_20260824_111258_401.jpg')]
  [('1DA22AI402', 'IMG_20260824_111302_527.jpg'), ('1DA24AI403', 'IMG_20260824_111302_527.jpg')]
  [('1DA22AI402', 'IMG_20260824_111309_467.jpg'), ('1DA24AI403', 'IMG_20260824_111309_467.jpg')]
  of which span more than one USN (possible mislabel/shared photo): 205
  USN groups sharing identical files (count of files): {('1DA22AI402', '1DA24AI403'): 33, ('1DA25AI001', '1DA25AI009'): 30, ('1DA25AI002', '1DA25AI007'): 31, ('1DA25AI003', '1DA25AI012'): 26, ('1DA25AI004', '1DA25AI008'): 30, ('1DA25AI005', '1DA25AI011'): 28, ('1DA25AI006', '1DA25AI010'): 27}
  Cross-USN identical files that are npz photos: 408 of 1013 photos in the npz.

## f) Proposed split (split_v2.py)

`split_by_photo(keys, val_ratio, test_ratio, seed=42, min_val=2, min_test=2)`: per class, shuffle photos with an RNG seeded by (seed, usn), take n_val=max(2, round(n*val)), n_test=max(2, round(n*test)), rest train. Same seed gives A and B the same photo ordering. Val/test use only aug_idx 0; train uses all 30 augmented copies. If a class has fewer than n_val+n_test+1 photos it falls back to 1 val/1 test (n>=3, flagged) or keeps everything in train with no val/test (n<=2, flagged). No data is created or duplicated.

- Split A ((0.8, 0.1, 0.1)): train 24150 samples/805 photos, val 104, test 104. Flags: none
  min val photos per class 3, min test 3, min train photos 20
  v1 for comparison: val 102, test 102
- Split B ((0.7, 0.15, 0.15)): train 21450 samples/715 photos, val 149, test 149. Flags: none
  min val photos per class 4, min test 4, min train photos 18
  v1 for comparison: val 152, test 152

Classes that cannot meet 2 val + 2 test photos: none.
Note: with 80:10:10 and min 2/2, classes with fewer than 20 photos get more than 10% in val and test; this is the cost of a usable eval set.

<!-- complete -->
