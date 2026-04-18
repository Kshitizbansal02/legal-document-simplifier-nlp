import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
sys.path.insert(0, str(BASE_DIR))

import numpy as np
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix


def main():
    # ── Load data ─────────────────────────────────────────────────────────────
    print("Loading data…")
    df = pd.read_csv(BASE_DIR / "data" / "cleaned_clauses.csv")
    X  = np.load(BASE_DIR / "data" / "embeddings.npy")

    if len(df) != len(X):
        raise ValueError(
            f"Mismatch: CSV has {len(df)} rows but embeddings have {len(X)} rows. "
            "Re-run your embedding generation script."
        )

    y = df["risk_level"].str.lower().str.strip()

    # Drop rows where risk_level is missing or invalid
    valid_labels = {"low", "medium", "high"}
    mask = y.isin(valid_labels)
    if (~mask).sum() > 0:
        print(f"  Dropping {(~mask).sum()} rows with invalid risk labels")
    X, y = X[mask], y[mask]

    print(f"  Dataset: {len(X)} samples")
    print(f"  Class distribution:\n{y.value_counts().to_string()}\n")

    # ── Train/test split ──────────────────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size    = 0.2,
        random_state = 42,
        stratify     = y,
    )

    # ── Train ─────────────────────────────────────────────────────────────────
    print("Training LogisticRegression…")
    clf = LogisticRegression(
        max_iter     = 1000,
        C            = 1.0,
        class_weight = "balanced",
        solver       = "lbfgs",
        random_state = 42,
    )
    clf.fit(X_train, y_train)

    # ── Evaluate ──────────────────────────────────────────────────────────────
    print("\n── Test Set Results ──────────────────────────────────────")
    y_pred = clf.predict(X_test)
    print(classification_report(y_test, y_pred))

    print("── Confusion Matrix ──────────────────────────────────────")
    labels = sorted(valid_labels)
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    print(f"{'':10s}", "  ".join(f"{l:6s}" for l in labels))
    for row_label, row in zip(labels, cm):
        print(f"{row_label:10s}", "  ".join(f"{v:6d}" for v in row))

    print("\n── Cross-Validation (5-fold) ─────────────────────────────")
    cv_scores = cross_val_score(clf, X, y, cv=StratifiedKFold(5), scoring="f1_weighted")
    print(f"F1 (weighted): {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")

    # ── Save ──────────────────────────────────────────────────────────────────
    (BASE_DIR / "models").mkdir(exist_ok=True)
    out_path = BASE_DIR / "models" / "risk_clf.pkl"
    joblib.dump(clf, out_path)
    print(f"\nSaved → {out_path}")
    print("Start the API: uvicorn main:app --reload")


if __name__ == "__main__":
    main()