"""Per-defect-size recall bins — IF-PROTO §1.3 (Top-3 / L3 measurement axis).

Each anomalous sample is bucketed by the area (in pixels) of its ground-truth
mask. The boundaries default to {16, 256} px^2, giving three bins:

    bin 0: defect_area_px2 < 16          (very small / sub-pixel)
    bin 1: 16 <= defect_area_px2 < 256   (small)
    bin 2: defect_area_px2 >= 256        (medium / large)

Inputs are kept generic (numpy arrays) so the same module is reused for both
anomalib's `MaskedAnomalyDataset` and external evaluation dumps.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .recall_at_fpr import recall_at_fpr_with_ci, RecallAtFPRResult


@dataclass(frozen=True)
class PerSizeRecall:
    fpr_target: float
    bin_edges: tuple[float, ...]
    per_bin: list[RecallAtFPRResult]
    bin_counts: list[int]


def per_size_recall_at_fpr(
    normal_scores: Sequence[float] | np.ndarray,
    anomaly_scores: Sequence[float] | np.ndarray,
    anomaly_defect_area_px2: Sequence[float] | np.ndarray,
    bin_boundaries: Sequence[float] = (16, 256),
    fpr_target: float = 0.001,
    bootstrap_n: int = 100,
    ci: float = 0.95,
    random_state: int | None = 42,
) -> PerSizeRecall:
    """Compute recall@FPR separately per defect-size bin.

    The FPR threshold is computed on the full normal population (shared across
    bins) — this matches what an industrial operator would set on the line.
    """
    a_scores = np.asarray(anomaly_scores, dtype=np.float64)
    a_size = np.asarray(anomaly_defect_area_px2, dtype=np.float64)
    if a_scores.shape != a_size.shape:
        raise ValueError(
            f"anomaly_scores and anomaly_defect_area_px2 must have same shape; "
            f"got {a_scores.shape} vs {a_size.shape}"
        )

    edges = sorted(set(float(x) for x in bin_boundaries))
    bins: list[tuple[float, float]] = []
    prev = -np.inf
    for e in edges:
        bins.append((prev, e))
        prev = e
    bins.append((prev, np.inf))

    per_bin: list[RecallAtFPRResult] = []
    counts: list[int] = []
    for lo, hi in bins:
        mask = (a_size >= lo) & (a_size < hi)
        scores_in_bin = a_scores[mask]
        counts.append(int(scores_in_bin.size))
        res = recall_at_fpr_with_ci(
            normal_scores=normal_scores,
            anomaly_scores=scores_in_bin,
            fpr_target=fpr_target,
            bootstrap_n=bootstrap_n,
            ci=ci,
            random_state=random_state,
        )
        per_bin.append(res)

    return PerSizeRecall(
        fpr_target=fpr_target,
        bin_edges=tuple(edges),
        per_bin=per_bin,
        bin_counts=counts,
    )
