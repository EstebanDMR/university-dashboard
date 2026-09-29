# University Student Analytics Dashboard

## Purpose

Interactive analytical dashboard for admissions, enrollment, retention, and
satisfaction. A separate case study demonstrates student-level outcome
classification with Python; its data come from a Portuguese institution.

## Dataset

`university_student_data.csv` — contains the following columns:

| Column | Description |
|---|---|
| Year | Academic year (2015–2024) |
| Term | Semester — Spring or Fall |
| Applications | Total applications received |
| Admitted | Students admitted |
| Enrolled | Students who enrolled |
| Retention Rate (%) | Percentage of students retained year-over-year |
| Student Satisfaction (%) | Average satisfaction score |
| Engineering Enrolled | Enrollment in Engineering department |
| Business Enrolled | Enrollment in Business department |
| Arts Enrolled | Enrollment in Arts department |
| Science Enrolled | Enrollment in Science department |

This original file has only **20 aggregate rows** (2015–2024 × Spring/Fall).
Each year's two terms have identical values apart from `Term`. It has no
student-level identifier, predictors, or dropout outcome. It is retained for
the original dashboard and is **not used to train the classifier**.

### Student-level case study

`data/student_dropout_uci.csv` is the UCI Machine Learning Repository's
[Predict Students' Dropout and Academic Success (dataset 697)](https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success).
It contains **4,424 individual records**, **36 features**, and a `Target`
column: `Dropout` (1,421), `Enrolled` (794), and `Graduate` (2,209).
The downloaded file has no missing cells or exact duplicate rows. The case
study is independent of the university data shown in the original dashboard.

Source: Realinho, V., Vieira Martins, M., Machado, J., & Baptista, L. (2021),
*Predict Students' Dropout and Academic Success*, UCI Machine Learning
Repository, [DOI: 10.24432/C5MC89](https://doi.org/10.24432/C5MC89).
The dataset is distributed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
The downloaded CSV has SHA-256
`a1b1a6531bbb93a5c7fdf0093b47172776652a4ffb12342fb79655c85b74801b`.

### Method

1. `student_dropout_analysis.ipynb` uses Pandas to inspect and prepare the
   individual data and Seaborn to explore the outcome distribution and
   first-semester academic performance.
2. `analysis/train_model.py` predicts the three original outcome classes.
   It drops all second-semester variables and the three macroeconomic
   variables. Encoded categories are one-hot encoded; numerical variables
   are median-imputed. Preprocessing is fitted inside the training pipeline.
3. A stratified 80/20 split (random seed 42) reserves the test set. Five-fold
   stratified cross-validation runs on training data only. A random forest
   is compared with a most-frequent-class baseline. Recall, F1, and a
   confusion matrix are calculated on the untouched test set.
4. Permutation importance reports how much shuffling each original feature
   reduces macro F1 on the test set. The reproducible outputs are in `results/`.

On the 885-student test set, the random forest reached **macro F1 0.663** and
**Dropout recall 0.701** (199 of 284 Dropout cases identified). The
most-frequent baseline reached macro F1 0.222 and Dropout recall 0.000.
Five-fold training cross-validation gave macro F1 0.679 ± 0.027 (mean ±
standard deviation). The full per-class report and confusion matrix are in
`results/model_metrics.json`; ranked factors are in
`results/permutation_importance.csv`.
The `Enrolled` class remains harder to distinguish (test F1 0.448), and the
model misses 85 of the 284 `Dropout` students in the test set.

Run the analysis locally:

```bash
pip install -r requirements.txt
python -m analysis.train_model
streamlit run app.py
```

Open `student_dropout_analysis.ipynb` in a Python notebook environment from
the repository root. The Streamlit section reads the checked-in result files
and does not retrain on page load. Its results do not change with the
aggregate-data filters.

### Interpretation and limitations

`Enrolled` is an unresolved status, not a final graduation/dropout outcome.
The source lacks a usable cohort or year field for temporal validation, and
comes from one Portuguese institution. A random split can overstate performance
on future cohorts or a different university. Variables measured at the end of
the first semester are unavailable at admission, so this is a **post-first-semester**
assessment. Permutation importance is predictive association, not a causal
effect. Do not use this demonstration for individual decisions without local
validation, fairness review, and human oversight.
Some students may have dropped out before first-semester measurements were
complete, so these fields can partly reflect an event already underway.

## Dashboard features

- **KPI cards** — avg retention, avg satisfaction, total enrolled, admission rate
- **Line chart** — retention rate trend over time
- **Bar chart** — student satisfaction by year
- **Grouped bar chart** — Spring vs Fall comparison
- **Pie/donut chart** — enrollment breakdown by department
- **Scatter plot** — retention vs satisfaction colored by year
- **Horizontal bar chart** — applications → admitted → enrolled funnel
- **Interactive filters** — year, term, department (sidebar)
- **Raw data viewer** — expandable table of the filtered dataset

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deployment

Deployed on **Streamlit Cloud** directly from this repository.

Live URL: https://university-dashboard-nud6vkg7cqcjcu9izmhczt.streamlit.app/

## Repository structure

```text
├── app.py                         # Streamlit dashboard
├── requirements.txt              # Python dependencies
├── university_student_data.csv   # Dataset
├── activity1_data_visualization.ipynb
├── student_dropout_analysis.ipynb # Student-level EDA and evaluation
├── analysis/train_model.py        # Reproducible training script
├── data/student_dropout_uci.csv   # UCI 697, CC BY 4.0
├── results/                      # Test metrics and permutation importance
└── README.md                     # Project documentation
```

## Technologies Used

- Python
- Pandas
- Matplotlib
- Streamlit
- GitHub
- Streamlit Cloud
- Seaborn
- scikit-learn
