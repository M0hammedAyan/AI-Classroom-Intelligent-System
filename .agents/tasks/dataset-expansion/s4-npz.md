# S4 Expanded NPZ

Built by `regenerate_npz_expanded.py` (parameterised copy of `regenerate_npz.py`; `--dataset`, `--output`; refuses to write the original npz name). Log: `s4-regen.log`.
Output: `data/processed/facial_pipeline_results_expanded.npz` (1.76 GB, not committed). Original npz untouched.
Keys: images (30390,160,160,3) uint8, embeddings, labels, metadata (source_image, student_id, augmentation_index 0-29, original_bbox, det_score). augmentation_index range verified 0-29.

Source: all 32 folders in `dataset/` (includes the 12 `1DA25AI0xx` students that S3 flagged as not in roster; they are included here because regenerate_npz logic reads every folder).

Classes: 32. Total samples: 30,390 (1,013 detected source images x 30).

| USN | source images | samples |
|---|---|---|
| 1DA22AI402 | 34 | 1020 |
| 1DA23AI001 | 39 | 1170 |
| 1DA23AI004 | 29 | 870 |
| 1DA23AI005 | 39 | 1170 |
| 1DA23AI009 | 35 | 1050 |
| 1DA23AI011 | 27 | 810 |
| 1DA23AI024 | 27 | 810 |
| 1DA23AI025 | 38 | 1140 |
| 1DA23AI031 | 34 | 1020 |
| 1DA23AI033 | 41 | 1230 |
| 1DA23AI036 | 28 | 840 |
| 1DA23AI042 | 33 | 990 |
| 1DA23AI044 | 38 | 1140 |
| 1DA23AI047 | 36 | 1080 |
| 1DA23AI049 | 33 | 990 |
| 1DA23AI050 | 30 | 900 |
| 1DA23AI055 | 35 | 1050 |
| 1DA23AI059 | 32 | 960 |
| 1DA24AI403 | 33 | 990 |
| 1DA24AI404 | 30 | 900 |
| 1DA25AI001 | 30 | 900 |
| 1DA25AI002 | 31 | 930 |
| 1DA25AI003 | 26 | 780 |
| 1DA25AI004 | 30 | 900 |
| 1DA25AI005 | 27 | 810 |
| 1DA25AI006 | 27 | 810 |
| 1DA25AI007 | 31 | 930 |
| 1DA25AI008 | 30 | 900 |
| 1DA25AI009 | 30 | 900 |
| 1DA25AI010 | 27 | 810 |
| 1DA25AI011 | 27 | 810 |
| 1DA25AI012 | 26 | 780 |

`train_expanded.py` (copy of `train_from_npz.py`): class count derived from labels; `--split A|B` (required), `--epochs`, `--npz`, `--smoke`; per-epoch history JSON `history_expanded_splitX.json` with `epoch_seconds`; outputs in `training_results/expanded/`.
