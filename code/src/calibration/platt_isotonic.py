"""Platt and isotonic calibration — sklearn wrappers.

CRITIC K1 (READ FIRST):

    Platt sigmoid and isotonic regression are *monotonic* transforms of the
    raw score. Applied to a single model:

        - The ROC curve is UNCHANGED.
        - recall@FPR is UNCHANGED for every FPR target.
        - What IS changed is how well `score → prob_of_anomaly` reflects the
          true posterior: this is what ECE / reliability diagrams measure.

    Any reported `recall@FPR` improvement attributed to "calibration" is
    really a `score-fusion / stacking` improvement (multiple models combined
    after each is calibrated). The two effects MUST be reported separately
    in `_workspace/04_implementation/results.md` (consolidated_proposals.md
    §2 P1: "calibration 효과와 분리 측정").
"""

from __future__ import annotations

from typing import Callable, Protocol

import numpy as np


class _Calibrator(Protocol):
    def predict(self, x: np.ndarray) -> np.ndarray: ...


def score_to_prob_minmax(scores: np.ndarray) -> np.ndarray:
    """Cheap [0, 1] mapping for visualisation only — DO NOT use as the
    calibration baseline. min-max squashes the tail and inflates ECE for the
    `none` ablation row; use a fixed sigmoid (e.g. exp(-z)) for the `none`
    baseline in the actual ablation."""
    s = np.asarray(scores, dtype=np.float64)
    if s.size == 0:
        return s
    lo, hi = float(s.min()), float(s.max())
    if hi - lo < 1e-12:
        return np.full_like(s, 0.5)
    return (s - lo) / (hi - lo)


def fit_platt(scores: np.ndarray, labels: np.ndarray):
    """Platt scaling = logistic regression on the raw score → prob_of_anomaly.

    Returns an object with `.predict_proba` style call via `apply_calibrator`.
    """
    from sklearn.linear_model import LogisticRegression  # local import — optional dep

    s = np.asarray(scores, dtype=np.float64).reshape(-1, 1)
    y = np.asarray(labels, dtype=np.int64)
    clf = LogisticRegression(C=1e6, solver="lbfgs")  # essentially MLE
    clf.fit(s, y)
    return clf


def fit_isotonic(scores: np.ndarray, labels: np.ndarray):
    """Isotonic (non-parametric, monotone non-decreasing) calibrator."""
    from sklearn.isotonic import IsotonicRegression  # local import

    s = np.asarray(scores, dtype=np.float64)
    y = np.asarray(labels, dtype=np.float64)
    iso = IsotonicRegression(out_of_bounds="clip")
    iso.fit(s, y)
    return iso


def apply_calibrator(cal: _Calibrator, scores: np.ndarray) -> np.ndarray:
    """Apply either a Platt LogisticRegression or an IsotonicRegression to scores.

    The dispatch is duck-typed so that this module does not import sklearn at
    its own top level (keeps the metrics path importable without sklearn).
    """
    s = np.asarray(scores, dtype=np.float64)
    if hasattr(cal, "predict_proba"):  # Platt (LogisticRegression)
        return cal.predict_proba(s.reshape(-1, 1))[:, 1]
    if hasattr(cal, "predict"):        # Isotonic
        return np.asarray(cal.predict(s))
    raise TypeError(f"Unknown calibrator type: {type(cal)}")
