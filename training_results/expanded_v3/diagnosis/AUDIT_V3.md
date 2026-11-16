# AUDIT_V3

## a) Dataset counts

- Student folders: 29 (user expects 29)
- Total photos: 947
- Stray files at dataset root: none
- Non-image files: ['D:\\CipherTECH\\Projects\\AI-Classroom-Intelligent-System\\dataset\\1DA23AI004\\TEMP', 'D:\\CipherTECH\\Projects\\AI-Classroom-Intelligent-System\\dataset\\1DA23AI011\\TEMP', 'D:\\CipherTECH\\Projects\\AI-Classroom-Intelligent-System\\dataset\\1DA23AI024\\TEMP', 'D:\\CipherTECH\\Projects\\AI-Classroom-Intelligent-System\\dataset\\1DA23AI036\\TEMP', 'D:\\CipherTECH\\Projects\\AI-Classroom-Intelligent-System\\dataset\\1DA23AI049\\TEMP']
- Invalid USN folder names: none
- Empty folders: none
- <10 photos: none
- Not in roster (65 roster USNs): ['1DA25AI001', '1DA25AI002', '1DA25AI003', '1DA25AI004', '1DA25AI005', '1DA25AI006', '1DA25AI007', '1DA25AI008', '1DA25AI009', '1DA25AI010']

| USN | photos | in roster |
|---|---|---|
| 1DA23AI001 | 39 | True |
| 1DA23AI004 | 29 | True |
| 1DA23AI005 | 39 | True |
| 1DA23AI009 | 35 | True |
| 1DA23AI011 | 27 | True |
| 1DA23AI024 | 29 | True |
| 1DA23AI025 | 38 | True |
| 1DA23AI031 | 34 | True |
| 1DA23AI033 | 41 | True |
| 1DA23AI036 | 28 | True |
| 1DA23AI042 | 33 | True |
| 1DA23AI044 | 38 | True |
| 1DA23AI047 | 36 | True |
| 1DA23AI049 | 33 | True |
| 1DA23AI050 | 30 | True |
| 1DA23AI055 | 36 | True |
| 1DA23AI059 | 32 | True |
| 1DA24AI403 | 33 | True |
| 1DA24AI404 | 30 | True |
| 1DA25AI001 | 31 | False |
| 1DA25AI002 | 28 | False |
| 1DA25AI003 | 30 | False |
| 1DA25AI004 | 26 | False |
| 1DA25AI005 | 30 | False |
| 1DA25AI006 | 27 | False |
| 1DA25AI007 | 34 | False |
| 1DA25AI008 | 36 | False |
| 1DA25AI009 | 36 | False |
| 1DA25AI010 | 29 | False |

## b) Duplicates and embeddings

- MD5 groups duplicated: 0
- Cross-USN duplicate files: 0
- Same-folder duplicate files: 0

- Embedded photos: 434 (<= 15/student); no face detected: ['1DA23AI055\\IMG20260824105047.jpg']
- Pairs with cosine > 0.6: 0

Top 10 closest pairs:

| cosine | A | B |
|---|---|---|
| 0.4104 | 1DA23AI031 | 1DA23AI055 |
| 0.3596 | 1DA24AI403 | 1DA25AI008 |
| 0.3439 | 1DA23AI001 | 1DA25AI001 |
| 0.3282 | 1DA23AI004 | 1DA23AI031 |
| 0.3270 | 1DA23AI004 | 1DA25AI001 |
| 0.3228 | 1DA23AI047 | 1DA24AI404 |
| 0.3143 | 1DA23AI031 | 1DA24AI403 |
| 0.3127 | 1DA24AI403 | 1DA25AI002 |
| 0.3116 | 1DA25AI005 | 1DA25AI010 |
| 0.2958 | 1DA23AI004 | 1DA23AI036 |

---
# Parts c, d, e

## c) Old vs new students

Old group = 19 students present in dataset\ and in npz (640 photos); new = 10 students (307 photos).

| metric | old mean (median) | new mean (median) | Mann-Whitney p | flag |
|---|---|---|---|---|
| megapixels | 13.42 (12.39) | 10.70 (9.37) | 7.2e-25 | DIFFERENT (new/old median 0.76) |
| face_w | 145.32 (127.00) | 170.78 (125.50) | 0.083 | same (new/old median 0.99) |
| face_h | 180.05 (156.00) | 209.44 (153.50) | 0.4 | same (new/old median 0.98) |
| det_score | 0.81 (0.83) | 0.82 (0.83) | 0.89 | same (new/old median 0.99) |
| lap_var | 219.70 (144.18) | 233.84 (202.60) | 0.0032 | DIFFERENT (new/old median 1.41) |
| brightness | 78.49 (77.54) | 84.37 (86.53) | 9.1e-07 | minor (new/old median 1.12) |

- old: 640 photos, no face 3 (0.5%), multi-face 62 (9.7%)

- new: 307 photos, no face 1 (0.3%), multi-face 31 (10.1%)
- old top resolutions: [('2296x4080', 185), ('3072x4096', 148), ('3048x4064', 134), ('4284x5712', 101)]
- new top resolutions: [('2296x4080', 172), ('3048x4064', 135)]


## d) Label check
Contact sheets (4x8 random face crops, tag = photo time suffix, `Fn` = n faces detected): `contact_sheets/<USN>.png` for new ['1DA25AI001', '1DA25AI002', '1DA25AI003', '1DA25AI004', '1DA25AI005', '1DA25AI006', '1DA25AI007', '1DA25AI008', '1DA25AI009', '1DA25AI010'] and random originals ['1DA23AI042', '1DA23AI011', '1DA23AI047']. Visual findings are in the section below.

### Multi-face photos (93); chosen face = highest det_score (same rule as facial_pipeline.extract_primary_face). Full list: multi_face.csv

| USN | photo | faces | chosen score | chosen size | runner-up score |
|---|---|---|---|---|---|
| 1DA23AI001 | IMG_20260824_105040.jpg | 3 | 0.8984 | 247x299 | 0.8028 |
| 1DA23AI001 | IMG_20260824_105048.jpg | 2 | 0.8545 | 176x209 | 0.7462 |
| 1DA23AI001 | IMG_20260824_105110.jpg | 2 | 0.8446 | 113x136 | 0.7421 |
| 1DA23AI001 | IMG_20260824_105114.jpg | 3 | 0.8592 | 126x149 | 0.7437 |
| 1DA23AI001 | IMG_20260824_105117.jpg | 3 | 0.8886 | 134x168 | 0.7927 |
| 1DA23AI001 | IMG_20260824_105124.jpg | 3 | 0.8773 | 173x207 | 0.6973 |
| 1DA23AI001 | IMG_20260824_105238.jpg | 3 | 0.8598 | 134x156 | 0.5321 |
| 1DA23AI001 | IMG_20260824_105242.jpg | 2 | 0.8601 | 122x153 | 0.6565 |
| 1DA23AI001 | IMG_20260824_105250.jpg | 3 | 0.8642 | 118x140 | 0.7461 |
| 1DA23AI001 | IMG_20260824_105255.jpg | 3 | 0.8274 | 101x117 | 0.6519 |
| 1DA23AI001 | IMG_20260824_105259.jpg | 2 | 0.8715 | 103x120 | 0.5563 |
| 1DA23AI001 | IMG_20260824_105426.jpg | 2 | 0.8079 | 88x108 | 0.5035 |
| 1DA23AI001 | IMG_20260824_105437.jpg | 3 | 0.8151 | 81x97 | 0.7279 |
| 1DA23AI001 | IMG_20260824_105454.jpg | 2 | 0.7953 | 77x95 | 0.6741 |
| 1DA23AI005 | IMG20260824105818.jpg | 2 | 0.8076 | 91x101 | 0.714 |
| 1DA23AI005 | IMG20260824105947.jpg | 2 | 0.8185 | 103x123 | 0.6617 |
| 1DA23AI005 | IMG20260824105956.jpg | 2 | 0.8143 | 92x104 | 0.7958 |
| 1DA23AI009 | IMG20260824111745.jpg | 2 | 0.7798 | 81x93 | 0.7471 |
| 1DA23AI009 | IMG20260824111809.jpg | 2 | 0.7677 | 105x144 | 0.648 |
| 1DA23AI009 | IMG20260824112012.jpg | 2 | 0.7825 | 87x102 | 0.6407 |
| 1DA23AI009 | IMG20260824112017.jpg | 2 | 0.8051 | 81x97 | 0.7057 |
| 1DA23AI025 | IMG_20260824_105647.jpg | 2 | 0.7904 | 76x84 | 0.5429 |
| 1DA23AI025 | IMG_20260824_105652.jpg | 2 | 0.7727 | 61x85 | 0.7169 |
| 1DA23AI025 | IMG_20260824_105703.jpg | 3 | 0.882 | 96x120 | 0.7472 |
| 1DA23AI025 | IMG_20260824_105730.jpg | 2 | 0.843 | 106x127 | 0.7005 |
| 1DA23AI025 | IMG_20260824_105741.jpg | 3 | 0.8362 | 134x147 | 0.7667 |
| 1DA23AI025 | IMG_20260824_105746.jpg | 2 | 0.8387 | 137x147 | 0.7181 |
| 1DA23AI025 | IMG_20260824_105805.jpg | 2 | 0.8404 | 183x204 | 0.721 |
| 1DA23AI025 | IMG_20260824_105812.jpg | 4 | 0.8824 | 174x182 | 0.8142 |
| 1DA23AI025 | IMG_20260824_105820.jpg | 2 | 0.8824 | 237x250 | 0.6849 |
| 1DA23AI025 | IMG_20260824_105824.jpg | 4 | 0.8606 | 257x283 | 0.7836 |
| 1DA23AI025 | IMG_20260824_105842.jpg | 3 | 0.8857 | 185x202 | 0.7839 |
| 1DA23AI025 | IMG_20260824_105847.jpg | 2 | 0.8686 | 148x161 | 0.7483 |
| 1DA23AI025 | IMG_20260824_105852.jpg | 2 | 0.8175 | 130x141 | 0.5973 |
| 1DA23AI025 | IMG_20260824_105903.jpg | 3 | 0.891 | 149x165 | 0.7849 |
| 1DA23AI025 | IMG_20260824_105908.jpg | 4 | 0.8481 | 131x140 | 0.8073 |
| 1DA23AI025 | IMG_20260824_105913.jpg | 2 | 0.8554 | 127x138 | 0.7649 |
| 1DA23AI025 | IMG_20260824_105923.jpg | 7 | 0.8425 | 130x141 | 0.8241 |
| 1DA23AI025 | IMG_20260824_105930.jpg | 6 | 0.8624 | 116x120 | 0.7635 |
| 1DA23AI025 | IMG_20260824_105937.jpg | 4 | 0.8726 | 102x109 | 0.8152 |
| 1DA23AI033 | IMG_20260824_104351.jpg | 2 | 0.8936 | 167x206 | 0.6958 |
| 1DA23AI033 | IMG_20260824_104434.jpg | 2 | 0.8731 | 106x146 | 0.6964 |
| 1DA23AI033 | IMG_20260824_104442.jpg | 3 | 0.8652 | 117x152 | 0.7638 |
| 1DA23AI033 | IMG_20260824_104449.jpg | 4 | 0.9035 | 132x173 | 0.7983 |
| 1DA23AI033 | IMG_20260824_104500.jpg | 2 | 0.8702 | 164x218 | 0.7583 |
| 1DA23AI033 | IMG_20260824_104713.jpg | 2 | 0.8614 | 125x160 | 0.7325 |
| 1DA23AI033 | IMG_20260824_104724.jpg | 3 | 0.8135 | 113x148 | 0.7467 |
| 1DA23AI033 | IMG_20260824_104729.jpg | 5 | 0.881 | 104x133 | 0.8417 |
| 1DA23AI033 | IMG_20260824_104735.jpg | 3 | 0.8427 | 95x127 | 0.6754 |
| 1DA23AI033 | IMG_20260824_104751.jpg | 2 | 0.8238 | 98x125 | 0.705 |
| 1DA23AI033 | IMG_20260824_104832.jpg | 2 | 0.7071 | 81x111 | 0.5138 |
| 1DA23AI044 | IMG20260824104512.jpg | 2 | 0.891 | 170x211 | 0.7716 |
| 1DA23AI044 | IMG20260824104642.jpg | 2 | 0.7087 | 73x97 | 0.6919 |
| 1DA23AI044 | IMG20260824104807.jpg | 2 | 0.8789 | 212x265 | 0.5594 |
| 1DA23AI044 | IMG20260824104829.jpg | 2 | 0.8719 | 155x200 | 0.6887 |
| 1DA23AI044 | IMG20260824104833.jpg | 2 | 0.8476 | 142x196 | 0.7838 |
| 1DA23AI047 | IMG_6696.jpeg | 2 | 0.8831 | 329x418 | 0.7824 |
| 1DA23AI047 | IMG_6702.jpeg | 2 | 0.9075 | 533x705 | 0.7699 |
| 1DA23AI047 | IMG_6703.jpeg | 2 | 0.8949 | 408x535 | 0.7536 |
| 1DA23AI055 | IMG20260824105346.jpg | 2 | 0.8314 | 159x259 | 0.8163 |
| 1DA23AI059 | IMG_6659.jpeg | 2 | 0.836 | 201x265 | 0.8316 |
| 1DA24AI404 | IMG_6583.jpeg | 2 | 0.8125 | 165x182 | 0.6966 |
| 1DA25AI002 | IMG_20261112_151239.jpg | 2 | 0.8934 | 151x195 | 0.7245 |
| 1DA25AI005 | IMG_20261112_152225.jpg | 2 | 0.8638 | 304x363 | 0.7052 |
| 1DA25AI006 | IMG_20261112_151730.jpg | 2 | 0.8299 | 110x130 | 0.8045 |
| 1DA25AI007 | IMG_20261112_151533_350.jpg | 2 | 0.8589 | 204x241 | 0.7556 |
| 1DA25AI007 | IMG_20261112_151538_977.jpg | 2 | 0.86 | 168x187 | 0.5716 |
| 1DA25AI007 | IMG_20261112_151547_163.jpg | 2 | 0.8472 | 205x254 | 0.758 |
| 1DA25AI007 | IMG_20261112_151608_283.jpg | 2 | 0.8416 | 148x180 | 0.6399 |
| 1DA25AI007 | IMG_20261112_151616_701.jpg | 2 | 0.8593 | 120x132 | 0.7978 |
| 1DA25AI007 | IMG_20261112_151626_879.jpg | 2 | 0.8267 | 99x112 | 0.7064 |
| 1DA25AI007 | IMG_20261112_151629_866.jpg | 2 | 0.8578 | 107x115 | 0.8046 |
| 1DA25AI009 | IMG_20261112_151910_416.jpg | 2 | 0.8134 | 116x130 | 0.6548 |
| 1DA25AI009 | IMG_20261112_151927_912.jpg | 2 | 0.8246 | 159x206 | 0.6708 |
| 1DA25AI009 | IMG_20261112_152113_608.jpg | 2 | 0.8646 | 632x821 | 0.6386 |
| 1DA25AI009 | IMG_20261112_152118_887.jpg | 2 | 0.8618 | 686x693 | 0.5356 |
| 1DA25AI010 | IMG_20261112_150948_054.jpg | 2 | 0.8858 | 208x262 | 0.744 |
| 1DA25AI010 | IMG_20261112_151005_068.jpg | 2 | 0.8079 | 132x159 | 0.5453 |
| 1DA25AI010 | IMG_20261112_151009_476.jpg | 2 | 0.8533 | 129x145 | 0.7016 |
| 1DA25AI010 | IMG_20261112_151043_916.jpg | 2 | 0.7157 | 87x97 | 0.5969 |
| 1DA25AI010 | IMG_20261112_151047_578.jpg | 2 | 0.7447 | 82x88 | 0.6428 |
| 1DA25AI010 | IMG_20261112_151221_600.jpg | 2 | 0.8281 | 227x273 | 0.5859 |
| 1DA25AI010 | IMG_20261112_151224_739.jpg | 2 | 0.8398 | 210x254 | 0.559 |
| 1DA25AI010 | IMG_20261112_151229_619.jpg | 2 | 0.8705 | 206x226 | 0.7147 |
| 1DA25AI010 | IMG_20261112_151241_640.jpg | 2 | 0.8515 | 152x169 | 0.8494 |
| 1DA25AI010 | IMG_20261112_151246_682.jpg | 2 | 0.7742 | 119x135 | 0.5875 |
| 1DA25AI010 | IMG_20261112_151248_994.jpg | 2 | 0.8248 | 112x120 | 0.7615 |
| 1DA25AI010 | IMG_20261112_151251_392.jpg | 2 | 0.8156 | 108x119 | 0.6719 |
| 1DA25AI010 | IMG_20261112_151257_560.jpg | 3 | 0.8403 | 111x123 | 0.7908 |
| 1DA25AI010 | IMG_20261112_151300_445.jpg | 2 | 0.787 | 94x104 | 0.575 |
| 1DA25AI010 | IMG_20261112_151303_288.jpg | 3 | 0.8174 | 95x105 | 0.7915 |
| 1DA25AI010 | IMG_20261112_151311_230.jpg | 2 | 0.7661 | 84x94 | 0.6725 |
| 1DA25AI010 | IMG_20261112_151314_401.jpg | 3 | 0.8189 | 85x97 | 0.7901 |

### Photos with no detected face (4)
- 1DA23AI024\IMG_20260824_105652_141.jpg
- 1DA23AI024\IMG_20260824_105940_864.jpg
- 1DA23AI055\IMG20260824105047.jpg
- 1DA25AI002\IMG_20261112_151236.jpg

### Identity check of chosen face in multi-face photos
Cosine of each detected face to the student's centroid (from single-pass sampled embeddings). 93 photos checked; chosen face is not the closest-to-centroid face in 13; chosen face cosine < 0.3 in 13. Full table: multi_face_identity.csv

| USN | photo | faces | chosen cos | best cos |
|---|---|---|---|---|
| 1DA23AI009 | IMG20260824111809.jpg | 2 | 0.1 | 0.872 |
| 1DA23AI009 | IMG20260824112017.jpg | 2 | 0.104 | 0.906 |
| 1DA23AI025 | IMG_20260824_105652.jpg | 2 | 0.14 | 0.742 |
| 1DA23AI044 | IMG20260824104642.jpg | 2 | 0.164 | 0.8 |
| 1DA23AI055 | IMG20260824105346.jpg | 2 | 0.179 | 0.874 |
| 1DA23AI059 | IMG_6659.jpeg | 2 | 0.098 | 0.873 |
| 1DA25AI007 | IMG_20261112_151626_879.jpg | 2 | 0.206 | 0.755 |
| 1DA25AI007 | IMG_20261112_151629_866.jpg | 2 | 0.225 | 0.903 |
| 1DA25AI009 | IMG_20261112_151927_912.jpg | 2 | 0.136 | 0.924 |
| 1DA25AI010 | IMG_20261112_151043_916.jpg | 2 | 0.193 | 0.848 |
| 1DA25AI010 | IMG_20261112_151257_560.jpg | 3 | 0.166 | 0.865 |
| 1DA25AI010 | IMG_20261112_151303_288.jpg | 3 | 0.092 | 0.796 |
| 1DA25AI010 | IMG_20261112_151314_401.jpg | 3 | 0.259 | 0.718 |

- Old npz class means: cos(1DA22AI402, 1DA24AI403) = 0.999; 1DA22AI402 vs current dataset 1DA24AI403 centroid = 0.863; npz 1DA24AI403 vs current dataset 1DA24AI403 = 0.858
- Wrong-face photos (chosen face cos<0.3 to own centroid) added to exclude_photos: 13. Orphan aug-only class 1DA22AI402 is the same person/photos as 1DA24AI403 in the old npz (class-mean cos 0.999, identical source names) and is not a member: do not train on it.

## e) Stale-data check

- Augmented folders present: 20. Dataset folders: 29. Augmented folders with no dataset folder: ['1DA22AI402'].
- The `aug_*.jpg` files are Git LFS pointer stubs (133 bytes each), not images, so source-vs-augmented MD5 is not recoverable from them. Content was instead compared by re-detecting each photo and matching the face bbox (IoU>=0.9) with `original_bbox` of aug_idx 0 in the original npz (which holds the real 160x160 crops).
- Regen needed (10): ['1DA25AI001', '1DA25AI002', '1DA25AI003', '1DA25AI004', '1DA25AI005', '1DA25AI006', '1DA25AI007', '1DA25AI008', '1DA25AI009', '1DA25AI010']
- Keep (19): ['1DA23AI001', '1DA23AI004', '1DA23AI005', '1DA23AI009', '1DA23AI011', '1DA23AI024', '1DA23AI025', '1DA23AI031', '1DA23AI033', '1DA23AI036', '1DA23AI042', '1DA23AI044', '1DA23AI047', '1DA23AI049', '1DA23AI050', '1DA23AI055', '1DA23AI059', '1DA24AI403', '1DA24AI404']
  - 1DA25AI001: no augmented folder
  - 1DA25AI002: no augmented folder
  - 1DA25AI003: no augmented folder
  - 1DA25AI004: no augmented folder
  - 1DA25AI005: no augmented folder
  - 1DA25AI006: no augmented folder
  - 1DA25AI007: no augmented folder
  - 1DA25AI008: no augmented folder
  - 1DA25AI009: no augmented folder
  - 1DA25AI010: no augmented folder
- exclude_photos (17): ['1DA23AI024/IMG_20260824_105652_141.jpg', '1DA23AI024/IMG_20260824_105940_864.jpg', '1DA23AI055/IMG20260824105047.jpg', '1DA25AI002/IMG_20261112_151236.jpg', '1DA23AI009/IMG20260824111809.jpg', '1DA23AI009/IMG20260824112017.jpg', '1DA23AI025/IMG_20260824_105652.jpg', '1DA23AI044/IMG20260824104642.jpg', '1DA23AI055/IMG20260824105346.jpg', '1DA23AI059/IMG_6659.jpeg', '1DA25AI007/IMG_20261112_151626_879.jpg', '1DA25AI007/IMG_20261112_151629_866.jpg', '1DA25AI009/IMG_20261112_151927_912.jpg', '1DA25AI010/IMG_20261112_151043_916.jpg', '1DA25AI010/IMG_20261112_151257_560.jpg', '1DA25AI010/IMG_20261112_151303_288.jpg', '1DA25AI010/IMG_20261112_151314_401.jpg']; non-image `TEMP` files are ignored by the image filter.
- Untouched check: `agumented data` tree hash (name|size|mtime) b3eec7dda8e72337 over 20130 files, git status: clean; npz sha256[:16] c4dcdc085061c5a0, mtime 1794789259, git status: clean. Nothing was written to either by this audit.

### Visual review of contact sheets (opened and inspected, 13 sheets)
- All 10 new students and the 3 random originals (1DA23AI042, 1DA23AI011, 1DA23AI047) show one consistent person per sheet. No mislabeled identity found among the sampled crops.
- Wrong-face / non-face crops confirmed visually: 1DA25AI010 `..151303_288` and `..151314_401` (blurred side/partial head, not a frontal face), both in exclude_photos via the identity check.
- Low-quality but correct-person crops (kept, flagged only): 1DA25AI007 motion-blurred `..151626_879` and a blurred head turn; 1DA25AI004 near-black frame (~151020) and head-down profile (~151017); 1DA25AI008 extreme profiles/looking down; 1DA25AI009 looking up and profile; 1DA23AI042 many strong yaw/pitch poses and one blurred head turn (~111854). They match the pose goals but may cost accuracy.
- Multi-face crops are tagged F2..F3 on the sheets. In the sampled sheets the chosen face was the correct person except for the identity-check failures listed above.
