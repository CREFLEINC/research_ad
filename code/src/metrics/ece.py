"""Expected Calibration Error (ECE) — calibration-quality metric.

Used as the *primary* axis for the calibration ablation (critic K1):
calibration is ranking-invariant, so recall@FPR is unchanged on a single
model — what changes is how well the score corresponds to a probability,
which ECE captures.

Implementation: equal-width binning in [0, 1].
"""

from __future__ import annotations

import numpy as np


def expected_calibration_error(
    probs: np.ndarray,
    labels: np.ndarray,
    n_bins: int = 15,
) -> float:
    """ECE for binary classification.

    Args:
        probs:  predicted probability of the positive class (anomaly), in [0, 1].
        labels: 0/1 ground-truth labels.
        n_bins: number of equal-width bins.
    """
    probs = np.asarray(probs, dtype=np.float64)
    labels = np.asarray(labels, dtype=np.int64)
    if probs.shape != labels.shape:
        raise ValueError("probs and labels must have the same shape")
    if probs.size == 0:
        return 0.0
    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    total = probs.size
    for i in range(n_bins):
        lo, hi = bin_edges[i], bin_edges[i + 1]
        if i == n_bins - 1:
            mask = (probs >= lo) & (probs <= hi)
        else:
            mask = (probs >= lo) & (probs < hi)
        if not mask.any():
            continue
        acc = float(labels[mask].mean())
        conf = float(probs[mask].mean())
        ece += (mask.sum() / total) * abs(acc - conf)
    return float(ece)
