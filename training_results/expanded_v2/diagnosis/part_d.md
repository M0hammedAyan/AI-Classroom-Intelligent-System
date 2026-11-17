# Part D: label check (complete)

Script: `part_d.py` (seed 42). Outputs: `contact_sheets/<USN>.png` (12 new + 3 random originals 1DA22AI402, 1DA23AI059, 1DA23AI050, plus 1DA24AI403), `closest_pairs.csv`, `embedding_outliers.csv`.
Note: the npz metadata key is `student_id` (no `usn`); I used the `labels` array.

## Main finding: the 12 new students are only 6 people, each under two USNs

Mean-ArcFace cosine between different USNs (7 pairs > 0.9; the next pair is 0.525):

| USN A | USN B | cosine | photos A / B | identical source filenames |
|---|---|---|---|---|
| 1DA25AI002 | 1DA25AI007 | 0.9998 | 31 / 31 | 31 |
| 1DA25AI003 | 1DA25AI012 | 0.9997 | 26 / 26 | 26 |
| 1DA25AI001 | 1DA25AI009 | 0.9996 | 30 / 30 | 30 |
| 1DA25AI004 | 1DA25AI008 | 0.9996 | 30 / 30 | 30 |
| 1DA25AI005 | 1DA25AI011 | 0.9995 | 27 / 27 | 27 |
| 1DA25AI006 | 1DA25AI010 | 0.9994 | 27 / 27 | 27 |
| 1DA22AI402 (original) | 1DA24AI403 (original) | 0.9993 | 34 / 33 | 33 |

Every pair uses the same source photo filenames in both folders. I viewed the sheets for 001 vs 009 and 003 vs 012: they show the same man and the same photos, with different random augmentation. The other pairs (002/007, 004/008, 005/011, 006/010) were not viewed. They rest on the embedding and filename evidence, which is the same as for the viewed pairs.

Effect: the same face carries two labels, so the classifier cannot separate them. A source photo can land in train under one label and in val/test under the other, which breaks the source-photo split. The 1DA22AI402 / 1DA24AI403 duplication is in the original 20 as well, so it probably also hurts the baseline.

## Contact-sheet observations (viewed: 001, 009, 003, 012)
- No wrong-person crops, hands or backgrounds seen. Each folder shows one person, so there are no multi-person folders.
- Some crops are heavy noise or very dark (augmentation: 003 has a near-black crop and a side profile). They are poor but not mislabeled.
- The other 8 new sheets and the 3 original comparison sheets were saved but not viewed.

## Embedding outliers
`embedding_outliers.csv` lists the 5 lowest cosine-to-class-mean samples per class (32 classes). Many are augmented noise/dark variants of one photo (for example 1DA25AI003 and 012 outliers all come from IMG_20261112_151017.jpg, cosine about 0.01 to 0.06). These are low-quality crops of one photo. Original classes have outliers at near 0 too (1DA23AI033, 1DA23AI025, 1DA23AI009), so low-quality augmentation also affects the old data. 1DA25AI012 has an aug0 sample with cosine 0.012 to its class mean.

## Photo counts
New students have 26 to 31 unique source photos each, which is enough to train. Because of the duplication, effective independent students are 6, not 12.

## Recommendation
Decide which USN is correct for each duplicated pair, or merge/drop one label per pair, before retraining. This is a roster decision that I did not make.
