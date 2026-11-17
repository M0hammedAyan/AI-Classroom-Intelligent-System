# Part B: original 20 vs new 12 students (photo quality, detection, labels)

Method: SCRFD (InsightFace buffalo_l, det_size 640, CPU) run on all 1018 raw photos in `dataset\<USN>\` (no sampling). Face selection, clamping and 160x160 resize reuse `vista\vision\facial_pipeline.py` (`preprocess_face`; primary face = highest `det_score`). Blur = variance of Laplacian on the grayscale 160x160 crop; brightness = mean gray of the same crop. Scripts: `part_b_quality.py`, `part_b_analyze.py`. Dataset not modified.

Files: `quality_per_photo.csv`, `quality_per_student.csv`, `quality_groups.csv`, `quality_comparison.png`, `duplicate_photos_cross_student.csv`.

## 1. Critical finding: the 12 new folders contain only 6 distinct people's photos

Byte-identical (MD5) photos appear under two different labels:

| Student pair | Identical photos |
|---|---|
| 1DA25AI001 / 1DA25AI009 | 30 |
| 1DA25AI002 / 1DA25AI007 | 31 |
| 1DA25AI003 / 1DA25AI012 | 26 |
| 1DA25AI004 / 1DA25AI008 | 30 |
| 1DA25AI005 / 1DA25AI011 | 28 |
| 1DA25AI006 / 1DA25AI010 | 27 |

Each pair has every photo duplicated (the per-student quality medians are identical too). The same photo set is therefore labelled as two different classes. A classifier cannot separate them; the best possible accuracy on those 12 classes is about 50%, and the contradictory labels also hurt the other classes. The split by source photo does not help, because the two copies sit in different classes and the same image can land in train for one label and test for the other.

The original 20 have the same problem: 1DA22AI402 and 1DA24AI403 share 33 identical photos. One further photo is shared by 1DA22AI402, 1DA23AI004, 1DA23AI011, 1DA23AI024, 1DA23AI036 and 1DA23AI049 (probably a group shot). In total, 206 duplicate groups, all across students and none within a student. This means the 20-class baseline also had a 402/403 label conflict (not necessarily new in v1).

Which folder in each pair is the true owner of the photos cannot be determined from the files. The user must say which USN each set belongs to, or supply the missing photos.

## 2. Quality comparison (all photos)

Medians and means by group (full table in `quality_groups.csv`; Mann-Whitney p-values orig vs new). Note the new-group numbers are effectively from 6 distinct sets, each counted twice.

| Metric | orig 20 median / mean | new 12 median / mean | p |
|---|---|---|---|
| Source resolution (MP) | 12.39 / 13.37 | 9.37 / 9.37 | 7e-94 |
| Source size | mixed (7 sizes, up to 4284x5712) | all 2296x4080 | |
| Face crop side (px, original photo) | 139.6 / 160.4 | 143.1 / 173.0 | 0.016 |
| Face area / photo area | 0.002 / 0.002 | 0.002 / 0.004 | 2e-13 |
| Detection score | 0.827 / 0.813 | 0.833 / 0.830 | 0.018 |
| Blur (Laplacian var, 160x160) | 68.1 / 108.4 | 103.8 / 125.6 | 5e-13 |
| Brightness (mean gray) | 77.4 / 78.4 | 81.0 / 78.9 | 0.20 |

Reading: the new students do differ systematically in source format (all one phone camera setting, 9.4 MP, 2296x4080, versus a mix) and are slightly sharper. Face crop size, detection confidence and brightness are close to the originals: differences are small (median crop 143 vs 140 px, det 0.833 vs 0.827, brightness 81 vs 77). The new set is not lower quality than the original; if anything it is sharper. Image quality does not explain the accuracy drop. Duplicated labels (section 1) do.

The original 20 are themselves heterogeneous: per-student median blur ranges 34 to 224 and source size 9 to 24 MP, which is a possible confound inside the baseline too.

## 3. Detection failures

3 photos in the original 20 and 2 in the new 12 had no face (0.4% and 0.6%). Per student: 1DA23AI024 has 2, 1DA23AI055 has 1, 1DA25AI005 has 1, 1DA25AI011 has 1 (the last two are the same duplicated photo). No student lost enough photos to matter.

## 4. Multiple faces and crop selection

The pipeline crops the face with the highest detection score (`max(faces, key=det_score)`), not the largest or most central face. No identity check is made, so with several faces the wrong person can be labelled.

- Photos with more than one face: orig 62 of 674 detected-or-not photos, new 6 of 344.
- Per student (orig): 1DA23AI025 19, 1DA23AI001 14, 1DA23AI033 11, 1DA23AI044 5, 1DA23AI009 4, 1DA23AI005 3, 1DA23AI047 3, 1DA23AI055 1, 1DA23AI059 1, 1DA24AI404 1.
- Per student (new): 1DA25AI004, 005, 006, 008, 010, 011 have 1 each (pairs of the same duplicated photo, so 3 distinct photos).
- In 61 of these 68 photos the second face scored at least 0.6, so it is a real competing face and not noise. In 6 orig photos the chosen face (highest score) is not the largest face; the new group has none.

Risk: the original students 1DA23AI025, 1DA23AI001 and 1DA23AI033 have 11 to 19 multi-face photos, so some of their crops may be another person. This is the more likely label-noise source among the originals. The new 12 are lower risk on this point (3 distinct multi-face photos). Contact-sheet inspection (Part D) is the way to confirm which crops are wrong; this part only counts them.

## Summary

1. The 12 new classes are 6 duplicated photo sets under two labels each (and 402/403 in the originals). This alone explains a large part of the 32-class accuracy drop.
2. Apart from source format, the new students do not differ in resolution, crop size, detection confidence or brightness, and are slightly sharper.
3. Detection failures are negligible (5 photos).
4. Multi-face selection is by highest score only; the originals have 62 multi-face photos, mostly from three students.
