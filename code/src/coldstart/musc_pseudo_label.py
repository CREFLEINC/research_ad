"""Pseudo-label generation for cold-start — CS-BRIDGE / P2.

Pipeline:
    1. Run MuSc and AnomalyCLIP zero-shot on a batch of unlabeled images.
    2. (REQUIRED) Verify error_correlation.rho_error <= 0.6 first (critic K5).
    3. Generate pseudo-labels with the chosen rule:
         - `agreement`:   both models score the image in the bottom
                          `normal_quantile` of their respective distributions.
         - `musc_only`:   fallback when rho > 0.6.
         - `average`:     a robust baseline — mean of the two min-max-normalised
                          scores below the joint quantile.
    4. Optionally split the "confirmed normal" pool into a *conservative subset*
       (bottom 50% of normals) so that downstream calibration (R1.1) sees the
       cleanest possible distribution.

This module is intentionally inference-tool agnostic — it consumes raw score
arrays. The MuSc and AnomalyCLIP wrappers in `src/models/zero_shot.py` produce
those arrays.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

Rule = Literal["agreement", "musc_only", "average"]


@dataclass(frozen=True)
class PseudoLabelResult:
    rule: Rule
    pseudo_normal_indices: np.ndarray  # indices into the input batch that we treat as "normal"
    conservative_subset_indices: np.ndarray  # subset for calibration fit
    n_input: int
    n_normal: int
    n_conservative: int


def _bottom_quantile_mask(scores: np.ndarray, q: float) -> np.ndarray:
    """Mask of samples whose score is in the bottom `q` quantile."""
    if scores.size == 0:
        return np.zeros(0, dtype=bool)
    cutoff = float(np.quantile(scores, q))
    return scores <= cutoff


def generate_pseudo_labels(
    scores_musc: np.ndarray,
    scores_anomaly_clip: np.ndarray | None,
    rule: Rule = "agreement",
    normal_quantile: float = 0.9,
    conservative_subset_fraction: float = 0.5,
) -> PseudoLabelResult:
    """Produce pseudo-normal labels from one or two zero-shot detectors.

    Args:
        scores_musc:           higher = more anomalous
        scores_anomaly_clip:   may be None if `rule == "musc_only"`
        rule:                  see module docstring
        normal_quantile:       e.g. 0.9 → use bottom 90% of MuSc as "normal"
        conservative_subset_fraction: of the chosen normals, the bottom
            `frac` slice is used as the *conservative subset* for calibration
            (residual_risks.md R1.1 mitigation).
    """
    sm = np.asarray(scores_musc, dtype=np.float64)
    n = sm.size

    if rule == "musc_only" or scores_anomaly_clip is None:
        m = _bottom_quantile_mask(sm, normal_quantile)
    elif rule == "agreement":
        sa = np.asarray(scores_anomaly_clip, dtype=np.float64)
        if sa.shape != sm.shape:
            raise ValueError("MuSc and AnomalyCLIP score arrays must match in shape")
        m_m = _bottom_quantile_mask(sm, normal_quantile)
        m_a = _bottom_quantile_mask(sa, normal_quantile)
        m = m_m & m_a
    elif rule == "average":
        sa = np.asarray(scores_anomaly_clip, dtype=np.float64)
        # min-max normalise each, then average — robust to scale differences
        def _norm(x: np.ndarray) -> np.ndarray:
            lo, hi = float(x.min()), float(x.max())
            if hi - lo < 1e-12:
                return np.zeros_like(x)
            return (x - lo) / (hi - lo)
        avg = 0.5 * (_norm(sm) + _norm(sa))
        m = _bottom_quantile_mask(avg, normal_quantile)
    else:
        raise ValueError(f"unknown rule: {rule}")

    normal_idx = np.flatnonzero(m)
    # conservative subset = lowest MuSc scores among the chosen normals
    if normal_idx.size > 0:
        order = np.argsort(sm[normal_idx])
        k = max(1, int(round(conservative_subset_fraction * normal_idx.size)))
        conservative_idx = normal_idx[order[:k]]
    else:
        conservative_idx = np.zeros(0, dtype=np.int64)

    return PseudoLabelResult(
        rule=rule,
        pseudo_normal_indices=normal_idx,
        conservative_subset_indices=conservative_idx,
        n_input=n,
        n_normal=int(normal_idx.size),
        n_conservative=int(conservative_idx.size),
    )
