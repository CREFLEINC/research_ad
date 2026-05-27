"""Error-correlation rho between two zero-shot detectors — critic K5.

CS-BRIDGE assumes MuSc and AnomalyCLIP make independent errors when both
agree a sample is "normal", so `pseudo-label noise = noise_a * noise_b`.
Both models, however, share a CLIP-family backbone, so the independence
assumption is most likely violated (`rho ~ 0.3-0.6`, per deep-ensemble
literature).

This module measures rho on a labeled hold-out and decides whether the
agreement filter is justified or the pipeline must fall back to MuSc-only.

Two rho variants are reported:

    rho_score      : Pearson correlation between the two raw scores (image-level)
    rho_error      : Pearson correlation between the two ERROR signals — i.e.
                     between `1[score_a > t_a] != label` and the equivalent for
                     model B. This is the rho that actually matters for the
                     "independent errors" claim.

Decision rule (consolidated_proposals.md §2 P2):
    rho > 0.6                       → abort agreement filter, fall back to MuSc-only
    0.3 <= rho <= 0.6  (caution)   → continue with agreement filter, double-check
                                      pseudo-label noise on labeled hold-out
    rho < 0.3                       → assumption defensible
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ErrorCorrelationResult:
    rho_score: float
    rho_error: float
    n: int
    threshold_a: float
    threshold_b: float
    decision: str  # "abort" | "caution" | "continue"


def _pearson(x: np.ndarray, y: np.ndarray) -> float:
    """Pearson correlation. Robust to zero-variance inputs (returns 0)."""
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if x.size < 2:
        return 0.0
    sx, sy = float(x.std()), float(y.std())
    if sx < 1e-12 or sy < 1e-12:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def _decision(rho: float, abort_above: float, caution_above: float) -> str:
    if rho > abort_above:
        return "abort"
    if rho > caution_above:
        return "caution"
    return "continue"


def error_correlation(
    scores_a: np.ndarray,
    scores_b: np.ndarray,
    labels: np.ndarray,
    fpr_target_for_threshold: float = 0.001,
    abort_above: float = 0.6,
    caution_above: float = 0.3,
) -> ErrorCorrelationResult:
    """Measure the score- and error-correlation between detector A and B.

    Args:
        scores_a, scores_b: image-level anomaly scores (higher = more anomalous)
        labels:             0/1 ground-truth (1 = anomalous)
        fpr_target_for_threshold: each detector's threshold is set so its
            empirical FPR on the labeled normals matches this target.

    The "error" used for `rho_error` is the per-sample 0/1 mistake indicator
    (1 if the detector's decision disagrees with the label, 0 otherwise).
    """
    sa = np.asarray(scores_a, dtype=np.float64)
    sb = np.asarray(scores_b, dtype=np.float64)
    y = np.asarray(labels, dtype=np.int64)
    if not (sa.shape == sb.shape == y.shape):
        raise ValueError("scores_a, scores_b, and labels must have the same shape")

    rho_s = _pearson(sa, sb)

    # Threshold each detector at the requested FPR over normals.
    normals_a = sa[y == 0]
    normals_b = sb[y == 0]
    if normals_a.size == 0 or normals_b.size == 0:
        # No normals to estimate FPR — fall back to median.
        ta = float(np.median(sa))
        tb = float(np.median(sb))
    else:
        ta = float(np.quantile(normals_a, 1.0 - fpr_target_for_threshold, method="higher"))
        tb = float(np.quantile(normals_b, 1.0 - fpr_target_for_threshold, method="higher"))

    err_a = ((sa > ta).astype(np.int64) != y).astype(np.float64)
    err_b = ((sb > tb).astype(np.int64) != y).astype(np.float64)
    rho_e = _pearson(err_a, err_b)

    # Decision uses the *error* correlation — that is what the independence
    # assumption is really about.
    return ErrorCorrelationResult(
        rho_score=rho_s,
        rho_error=rho_e,
        n=int(sa.size),
        threshold_a=ta,
        threshold_b=tb,
        decision=_decision(rho_e, abort_above, caution_above),
    )
