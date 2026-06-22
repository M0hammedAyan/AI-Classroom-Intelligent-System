# VISTA Dataset Analysis — Academic Risk Prediction

**Owner:** Risk AI Lead  
**Purpose:** Evaluate publicly available datasets for training a future ML risk model (Phase 2 upgrade — see `RISK_SYSTEM_DESIGN.md` Section 7). The rule-based pilot does not use any of these; this analysis informs what to train on when real outcome labels become available.

---

## 1. UCI Student Performance Dataset

**Source:** https://archive.ics.uci.edu/ml/datasets/student+performance  
**Format:** CSV, ~650 rows, 33 columns  
**Domain:** Portuguese secondary school students (Math and Portuguese subjects)

### Features Available

| Feature | Description |
|---|---|
| `absences` | Number of school absences (0–93) |
| `studytime` | Weekly study time (1–4 scale) |
| `failures` | Number of past class failures |
| `G1`, `G2`, `G3` | Grades period 1, 2, 3 (0–20 scale) |
| `famrel` | Family relationship quality |
| `freetime`, `goout` | Lifestyle indicators |
| `health` | Current health status |
| `higher` | Wants to pursue higher education (yes/no) |
| `internet` | Home internet access |
| `Medu`, `Fedu` | Mother/Father education level |

### Target Variable

`G3` — final grade (0–20). Binarise as `pass = G3 >= 10`, `fail = G3 < 10` for classification. Alternatively use directly as a regression target.

### Pros

- Clean, well-structured, ready to use with no preprocessing complexity
- Has both attendance (`absences`) and grade trend (`G1 → G2 → G3`) — maps directly to VISTA's two core signals
- Widely used in academic risk research — benchmarks available
- Small enough to iterate on quickly during Phase 2 development
- Includes socioeconomic context features useful for explaining model decisions

### Cons

- Portuguese secondary school — not Indian college context; distributions may differ
- Only ~650 rows — limited for tree-based models; fine for logistic regression
- `absences` is a count, not a percentage — requires normalisation against total sessions
- No real-time or weekly granularity — snapshot data only
- Social features (alcohol, relationships) are not available in VISTA's data collection

### VISTA Fit Score: 8/10

---

## 2. OULAD — Open University Learning Analytics Dataset

**Source:** https://analyse.kmi.open.ac.uk/open_dataset  
**Format:** Multiple CSV tables, ~32,000 students, 7 linked tables  
**Domain:** UK Open University online courses (2013–2014)

### Features Available

| Feature | Description |
|---|---|
| `studied_credits` | Credits registered |
| `num_of_prev_attempts` | Prior attempts at the module |
| `date_registration` / `date_unregistration` | Enrollment timeline |
| `sum_click` | VLE (online platform) interaction count per week |
| `score` | Assessment scores per submission |
| `is_banked` | Whether credit was previously banked |
| `disability` | Disability status |
| `imd_band` | Deprivation index (socioeconomic proxy) |

### Target Variable

`final_result` — four classes: `Pass`, `Distinction`, `Fail`, `Withdrawn`. For binary classification: `Pass/Distinction = 0`, `Fail/Withdrawn = 1`.

### Pros

- Very large dataset — excellent for training robust models
- Has temporal data (weekly VLE clicks, assessment timeline) — enables sequence-based features
- Real withdrawal/dropout labels, not just failure
- Multiple assessment submissions per student — supports trend computation
- Widely benchmarked in learning analytics research

### Cons

- Online university context — very different from in-person classroom attendance
- No face-to-face attendance signal — the closest proxy is VLE click count, which has no direct equivalent in VISTA
- Complex multi-table join required before use — significant preprocessing overhead
- UK-specific socioeconomic indices (IMD band) not relevant to India
- 32,000 rows from one institution — may not generalise to Indian college patterns

### VISTA Fit Score: 5/10

---

## 3. Student Dropout Prediction Datasets (Kaggle)

**Primary source:** https://www.kaggle.com/datasets/thedevastator/higher-education-predictors-of-student-dropout  
**Format:** Single CSV, ~4,400 students, 37 columns  
**Domain:** Portuguese higher education institutions

### Features Available

| Feature | Description |
|---|---|
| `Curricular units credited/enrolled/approved/grade` | Per-semester academic progress |
| `Age at enrollment` | Student age |
| `Application mode` | How student applied |
| `Scholarship holder` | Financial aid flag |
| `Tuition fees up to date` | Whether fees are paid |
| `GDP`, `Inflation rate`, `Unemployment rate` | Macroeconomic context |
| `Daytime/evening attendance` | Session type |

### Target Variable

`Target` — three classes: `Graduate`, `Dropout`, `Enrolled` (still enrolled). For binary: `Dropout = 1`, `Graduate/Enrolled = 0`.

### Pros

- Closest domain match to VISTA — higher education, not secondary school
- Has actual dropout labels, not just grade failure
- Semester-level academic performance (enrolled vs approved units) maps to VISTA's marks tracking
- 4,400 rows — adequate for logistic regression and random forest
- Includes financial signals (fees paid) that correlate with dropout in Indian colleges too

### Cons

- Portuguese institutions again — cultural and institutional differences
- No attendance percentage column — only enrolled/approved units as proxy
- Macroeconomic features (GDP, inflation) are not useful for per-student prediction
- Three-class target requires either multiclass handling or careful binarisation
- No assignment completion or weekly granularity

### VISTA Fit Score: 7/10

---

## 4. Academic Success / Early Alert Datasets

**Source:** Various — no single canonical dataset. Key examples:
- **SECOM dataset** (manufacturing, not academic — exclude)
- **EduNet / Campus Analytics** (institutional, often not public)
- **Predict Students' Dropout and Academic Success** (same Kaggle dataset as #3 above)
- **National Student Clearinghouse Research Center** (US, aggregated, not per-student)

Most "academic success" datasets in the public domain are either the UCI or Kaggle datasets already covered above, or are institutional datasets that require data sharing agreements.

### Publicly Available Options

| Dataset | Rows | Attendance Signal | Grade Trend | Dropout Label | Notes |
|---|---|---|---|---|---|
| UCI Student Performance | ~650 | Absence count | G1→G2→G3 | No (grade only) | Best small dataset |
| OULAD | ~32,000 | VLE clicks (proxy) | Assessment timeline | Yes (Withdrawn) | Best large dataset |
| Kaggle Dropout | ~4,400 | Units enrolled/approved | Semester grades | Yes | Best domain match |
| xAPI-Edu-Data (Kaggle) | ~480 | `StudentAbsenceDays` | Raising hand, resource visits | No | Too small, behavioural proxy only |

---

## Recommendation for VISTA Phase 2

**Primary recommendation: UCI Student Performance Dataset**

**Reasoning:**

1. **Feature overlap is highest.** It has both an absence count and a grade sequence (G1 → G2 → G3), which maps directly onto VISTA's `attendance_percentage` and `performance_trend` features. The feature engineering pipeline in `ml/features.py` can be adapted with minimal changes.

2. **Right size for the team.** At ~650 rows, it is small enough to iterate on quickly with logistic regression (Phase 2 target model). The Kaggle dropout dataset at 4,400 rows is better for random forest/XGBoost but premature for Phase 2.

3. **Benchmarks exist.** The dataset has dozens of published results — the team can immediately verify whether their model implementation is plausible.

4. **Practical to download and use today.** No account, no agreement, direct CSV download from the UCI repository.

**Secondary recommendation: Kaggle Dropout Dataset** (for Phase 3 — Random Forest)

When the team moves to tree-based models, the Kaggle dropout dataset provides a better training base: higher education domain, actual dropout labels, and enough rows for train/val/test splits with stratification.

**Do not use OULAD for the pilot ML phase.** The preprocessing complexity and domain mismatch (online VLE clicks vs in-person attendance) will consume more time than the accuracy gain justifies at this scale.

---

## Bridging to VISTA's Own Data

The external datasets above are a **bootstrap** — they let the team build and validate the ML pipeline before VISTA has enough pilot data. The long-term training set is VISTA's own DB:

```
attendance table  +  scores table  ──▶  features.py  ──▶  training rows
                                                               +
                                                  end-of-semester outcome (pass/fail)
                                                  manually labelled by teacher
```

After 1–2 pilot semesters (200–400 student-semester records with outcomes), replace the external dataset with VISTA's own data. At that point, the model is trained on the actual student population it will predict — which is always better than any external dataset.
