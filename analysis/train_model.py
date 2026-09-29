"""Train and evaluate a first-semester student outcome classifier.

Run from the repository root with ``python -m analysis.train_model``.
"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.metrics import classification_report, confusion_matrix, f1_score, recall_score
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "student_dropout_uci.csv"
OUTPUT_DIR = ROOT / "results"
CLASSES = ["Dropout", "Enrolled", "Graduate"]
RANDOM_STATE = 42

# These are coded categories in the UCI dictionary. Treating them as continuous
# numbers would invent a distance between codes that the source does not define.
CATEGORICAL = [
    "Marital Status", "Application mode", "Course",
    "Daytime/evening attendance", "Previous qualification", "Nacionality",
    "Mother's qualification", "Father's qualification",
    "Mother's occupation", "Father's occupation", "Displaced",
    "Educational special needs", "Debtor", "Tuition fees up to date",
    "Gender", "Scholarship holder", "International",
]


def prepare_data(path: Path = DATA_PATH) -> tuple[pd.DataFrame, pd.Series, dict]:
    raw = pd.read_csv(path)
    raw.columns = raw.columns.str.strip()
    if "Target" not in raw or not set(raw["Target"].dropna().unique()) <= set(CLASSES):
        raise ValueError("Expected UCI 697 data with Target = Dropout, Enrolled or Graduate")
    if len(raw) < 1000 or raw["Target"].value_counts().min() < 100:
        raise ValueError("Too few individual records per class for this evaluation")

    # The outcome is student-level. Exact duplicate records cannot be identified
    # as the same person without an ID, so report them rather than deleting them.
    audit = {
        "rows": int(len(raw)),
        "columns": int(raw.shape[1]),
        "missing_cells": int(raw.isna().sum().sum()),
        "exact_duplicate_rows": int(raw.duplicated().sum()),
        "class_counts": {name: int(raw["Target"].eq(name).sum()) for name in CLASSES},
    }
    excluded = [column for column in raw if column.startswith("Curricular units 2nd sem")]
    excluded += ["Unemployment rate", "Inflation rate", "GDP"]
    features = raw.drop(columns=["Target", *excluded])
    target = raw["Target"].astype(str)
    audit["excluded_features"] = excluded
    audit["features_used"] = list(features.columns)
    return features, target, audit


def make_model(columns: list[str]) -> Pipeline:
    categorical = [column for column in CATEGORICAL if column in columns]
    numeric = [column for column in columns if column not in categorical]
    transform = ColumnTransformer(
        [
            ("categorical", Pipeline([
                ("impute", SimpleImputer(strategy="most_frequent")),
                ("encode", OneHotEncoder(handle_unknown="ignore")),
            ]), categorical),
            ("numeric", SimpleImputer(strategy="median"), numeric),
        ]
    )
    return Pipeline([
        ("prepare", transform),
        ("classifier", RandomForestClassifier(
            n_estimators=300,
            min_samples_leaf=3,
            class_weight="balanced_subsample",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )),
    ])


def run_training(data_path: Path = DATA_PATH, output_dir: Path = OUTPUT_DIR) -> dict:
    features, target, audit = prepare_data(data_path)
    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, stratify=target, random_state=RANDOM_STATE
    )
    model = make_model(list(features.columns))
    cv = cross_validate(
        model, x_train, y_train,
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE),
        scoring={"f1_macro": "f1_macro", "recall_macro": "recall_macro"},
        n_jobs=1,
    )
    model.fit(x_train, y_train)
    predicted = model.predict(x_test)
    baseline = DummyClassifier(strategy="most_frequent").fit(x_train, y_train)
    baseline_predicted = baseline.predict(x_test)

    importance = permutation_importance(
        model, x_test, y_test, scoring="f1_macro", n_repeats=5,
        random_state=RANDOM_STATE, n_jobs=1,
    )
    factors = pd.DataFrame({
        "feature": features.columns,
        "importance_mean": importance.importances_mean,
        "importance_std": importance.importances_std,
    }).sort_values("importance_mean", ascending=False)
    output_dir.mkdir(parents=True, exist_ok=True)
    factors.to_csv(output_dir / "permutation_importance.csv", index=False)

    report = classification_report(y_test, predicted, labels=CLASSES, output_dict=True, zero_division=0)
    results = {
        "source": "UCI Machine Learning Repository, dataset 697",
        "dataset_sha256": hashlib.sha256(data_path.read_bytes()).hexdigest(),
        "package_versions": {"pandas": pd.__version__, "scikit_learn": sklearn.__version__},
        "random_state": RANDOM_STATE,
        "train_rows": len(x_train),
        "test_rows": len(x_test),
        "audit": audit,
        "cross_validation_train": {
            name: {"mean": float(np.mean(values)), "std": float(np.std(values))}
            for name, values in cv.items() if name.startswith("test_")
        },
        "test": {
            "f1_macro": float(f1_score(y_test, predicted, average="macro")),
            "recall_macro": float(recall_score(y_test, predicted, average="macro")),
            "dropout_recall": float(recall_score(y_test, predicted, labels=["Dropout"], average="macro")),
            "classification_report": report,
            "labels": CLASSES,
            "confusion_matrix": confusion_matrix(y_test, predicted, labels=CLASSES).tolist(),
        },
        "baseline_test": {
            "f1_macro": float(f1_score(y_test, baseline_predicted, average="macro")),
            "dropout_recall": float(recall_score(y_test, baseline_predicted, labels=["Dropout"], average="macro")),
        },
    }
    (output_dir / "model_metrics.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return results


if __name__ == "__main__":
    scores = run_training()
    print(json.dumps({
        "test": scores["test"], "baseline_test": scores["baseline_test"]
    }, indent=2))
