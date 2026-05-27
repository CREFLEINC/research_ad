"""recall@FPR with bootstrap confidence intervals — core of IF-PROTO (P1).

Critic K1 (calibration ranking-invariance) and validation_report Top-1
(industrial recall@FPR=0.1% is the missing axis) are addressed here:

- A higher score MUST denote "more anomalous".
- The threshold is chosen so that FPR on the *normal* test population is at most
  the requested target (e.g. 0.001 → 0.1%).
- Bootstrap CIs are computed by resampling normal and anomaly populations
  independently, recomputing the threshold and the recall each iteration —
  this is what guards against the "tail measurement noise" critique
  (critique_notes.md K1, ±5-15%p) by exposing the noise instead of hiding it.

Dependency: numpy only (no scipy). This is intentional so the module is
exercisable in environments without the full PyTorch stack.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class RecallAtFPRResult:
    fpr_target: float
    threshold: float
    recall: float
    ci_low: float
    ci_high: float
    n_normal: int
    n_anomaly: int
    bootstrap_n: int


def _threshold_for_fpr(normal_scores: np.ndarray, fpr_target: float) -> float:
    """Pick the smallest threshold t such that mean(normal_scores > t) <= fpr_target.

    Returns +inf if no finite threshold can hit the target (i.e. fewer normals
    than 1/fpr_target — the protocol must flag this in the report).
    """
    if normal_scores.size == 0:
        return float("inf")
    # quantile at (1 - fpr_target). e.g. fpr=0.001 → 99.9 percentile.
    q = 1.0 - float(fpr_target)
    # numpy.quantile with method="higher" gives the smallest value such that
    # the empirical FPR is at most the target (closest to industrial usage).
    return float(np.quantile(normal_scores, q, method="higher"))


def recall_at_fpr(
    normal_scores: Sequence[float] | np.ndarray,
    anomaly_scores: Sequence[float] | np.ndarray,
    fpr_target: float,
) -> tuple[float, float]:
    """Single-pass recall@FPR. Returns (recall, threshold)."""
    n = np.asarray(normal_scores, dtype=np.float64)
    a = np.asarray(anomaly_scores, dtype=np.float64)
    t = _threshold_for_fpr(n, fpr_target)
    if not np.isfinite(t) or a.size == 0:
        return 0.0, t
    recall = float(np.mean(a > t))
    return recall, t


def recall_at_fpr_with_ci(
    normal_scores: Sequence[float] | np.ndarray,
    anomaly_scores: Sequence[float] | np.ndarray,
    fpr_target: float,
    bootstrap_n: int = 100,
    ci: float = 0.95,
    random_state: int | None = 42,
) -> RecallAtFPRResult:
    """Bootstrap CI over independently resampled normal and anomaly populations.

    This is the K1 polish: each iteration redraws *both* populations and
    recomputes the FPR threshold. The 95% CI half-width directly answers
    "is the SOTA gap measurable?" — `consolidated_proposals.md` §2 P1 abort
    criterion: CI half-width > 5%p → fusion claims dropped.
    """
    n = np.asarray(normal_scores, dtype=np.float64)
    a = np.asarray(anomaly_scores, dtype=np.float64)
    rng = np.random.default_rng(random_state)

    point_recall, point_t = recall_at_fpr(n, a, fpr_target)
    if n.size == 0 or a.size == 0:
        return RecallAtFPRResult(
            fpr_target=fpr_target,
            threshold=point_t,
            recall=point_recall,
            ci_low=0.0,
            ci_high=0.0,
            n_normal=int(n.size),
            n_anomaly=int(a.size),
            bootstrap_n=bootstrap_n,
        )

    boot = np.empty(bootstrap_n, dtype=np.float64)
    for i in range(bootstrap_n):
        n_b = rng.choice(n, size=n.size, replace=True)
        a_b = rng.choice(a, size=a.size, replace=True)
        t_b = _threshold_for_fpr(n_b, fpr_target)
        boot[i] = np.mean(a_b > t_b) if np.isfinite(t_b) else 0.0

    alpha = (1.0 - ci) / 2.0
    lo = float(np.quantile(boot, alpha))
    hi = float(np.quantile(boot, 1.0 - alpha))
    return RecallAtFPRResult(
        fpr_target=fpr_target,
        threshold=point_t,
        recall=point_recall,
        ci_low=lo,
        ci_high=hi,
        n_normal=int(n.size),
        n_anomaly=int(a.size),
        bootstrap_n=bootstrap_n,
    )


def ci_half_width(result: RecallAtFPRResult) -> float:
    """Half-width of the bootstrap CI in points (e.g. 0.07 = ±7%p).

    P1 abort criterion: if this exceeds 0.05 (5 percentage points), the
    SOTA-comparison claims are dropped.
    """
    return 0.5 * (result.ci_high - result.ci_low)
