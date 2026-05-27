"""Sanity checks for the IF-PROTO metric modules using synthetic scores.

Runnable in an env with only numpy. Verifies:

    1. recall@FPR returns the analytically expected value when two
       well-separated normal/anomaly populations are fed.
    2. Bootstrap CI half-width shrinks as the sample size grows (so we are
       actually estimating uncertainty rather than returning a fixed number).
    3. Per-defect-size bins partition the anomalies correctly.
    4. Pareto frontier removes dominated points.
    5. Calibration (Platt/Isotonic) does NOT change a single model's
       recall@FPR — the K1 ranking-invariance guard.

If sklearn is missing the calibration block is skipped instead of failing.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

# Allow `python -m tests.test_metrics_synth` to find `src/`.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.metrics import (  # noqa: E402
    recall_at_fpr,
    recall_at_fpr_with_ci,
    ci_half_width,
    per_size_recall_at_fpr,
    pareto_frontier,
    PareToPoint,
    expected_calibration_error,
)


def _gaussian_scores(rng: np.random.Generator, n_normal: int, n_anomaly: int,
                     mu_normal: float = 0.0, mu_anomaly: float = 2.0,
                     sigma: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    n = rng.normal(loc=mu_normal, scale=sigma, size=n_normal)
    a = rng.normal(loc=mu_anomaly, scale=sigma, size=n_anomaly)
    return n, a


def test_recall_at_fpr_basic() -> None:
    rng = np.random.default_rng(42)
    n, a = _gaussian_scores(rng, n_normal=10_000, n_anomaly=2_000,
                            mu_normal=0.0, mu_anomaly=4.0, sigma=1.0)
    # FPR=0.1% with mu=0/sigma=1 normals ⇒ threshold ≈ 3.09 (norm inv 0.999)
    # anomalies are N(4, 1) ⇒ recall = P(N(4,1) > 3.09) ≈ Phi(0.91) ≈ 0.819
    recall, t = recall_at_fpr(n, a, fpr_target=0.001)
    assert 3.0 < t < 3.2, f"threshold off: {t}"
    assert 0.75 < recall < 0.88, f"recall off: {recall}"


def test_bootstrap_ci_shrinks_with_n() -> None:
    rng = np.random.default_rng(123)
    n_small, a_small = _gaussian_scores(rng, 200, 50,
                                        mu_anomaly=3.0)
    n_large, a_large = _gaussian_scores(rng, 5_000, 1_000,
                                        mu_anomaly=3.0)

    small = recall_at_fpr_with_ci(n_small, a_small, 0.01, bootstrap_n=200)
    large = recall_at_fpr_with_ci(n_large, a_large, 0.01, bootstrap_n=200)
    hw_s, hw_l = ci_half_width(small), ci_half_width(large)
    assert hw_l < hw_s, f"CI did not shrink with N: hw_small={hw_s}, hw_large={hw_l}"


def test_per_size_recall_buckets() -> None:
    rng = np.random.default_rng(7)
    n, a = _gaussian_scores(rng, 5_000, 600, mu_anomaly=3.0)
    # mark a third of anomalies as small / mid / large defects
    sizes = rng.choice([8.0, 80.0, 800.0], size=a.size, p=[1/3, 1/3, 1/3])
    res = per_size_recall_at_fpr(n, a, sizes, bin_boundaries=(16, 256),
                                 fpr_target=0.01, bootstrap_n=50)
    assert len(res.per_bin) == 3, "expected 3 bins"
    assert sum(res.bin_counts) == a.size, "bin counts must sum to total anomalies"
    assert all(0.0 <= r.recall <= 1.0 for r in res.per_bin)


def test_pareto_filter() -> None:
    pts = [
        PareToPoint("A", latency_ms=10.0, vram_mb=2000.0, recall=0.50),
        PareToPoint("B", latency_ms=20.0, vram_mb=4000.0, recall=0.60),
        PareToPoint("C", latency_ms=5.0,  vram_mb=8000.0, recall=0.40),
        PareToPoint("D", latency_ms=30.0, vram_mb=6000.0, recall=0.55),  # dominated by B
    ]
    frontier = {p.name for p in pareto_frontier(pts)}
    assert "D" not in frontier, "D should be dominated by B on all 3 axes"
    assert "A" in frontier
    assert "B" in frontier
    assert "C" in frontier  # best latency — non-dominated


def test_calibration_does_not_change_recall_at_fpr() -> None:
    """Critic K1 guard: calibration is monotonic on a single model.

    If sklearn is missing the Platt path is skipped but a hand-rolled
    monotonic transform (exp) is used instead so the invariance property is
    still exercised by the test.
    """
    rng = np.random.default_rng(2024)
    n, a = _gaussian_scores(rng, 2_000, 400, mu_anomaly=2.5)
    scores = np.concatenate([n, a])
    labels = np.concatenate([np.zeros_like(n, dtype=np.int64),
                             np.ones_like(a, dtype=np.int64)])

    rec_raw, _ = recall_at_fpr(n, a, fpr_target=0.01)

    try:
        from src.calibration import fit_platt, apply_calibrator
        cal = fit_platt(scores, labels)
        s_cal = apply_calibrator(cal, scores)
        which = "platt"
    except ImportError:
        # Fall back: any strictly-monotonic mapping must preserve ranks.
        s_cal = np.exp(scores - scores.max())  # avoids overflow
        which = "exp (sklearn unavailable; using hand-rolled monotone transform)"

    n_cal = s_cal[:n.size]
    a_cal = s_cal[n.size:]
    rec_cal, _ = recall_at_fpr(n_cal, a_cal, fpr_target=0.01)

    assert math.isclose(rec_raw, rec_cal, abs_tol=1e-9), (
        f"K1 guard failed — monotone transform should be ranking-invariant, but "
        f"recall changed under {which}: raw={rec_raw}, calibrated={rec_cal}"
    )
    print(f"  K1 guard verified using {which}: recall_raw={rec_raw:.6f} == recall_cal={rec_cal:.6f}")


def test_ece_perfectly_calibrated() -> None:
    rng = np.random.default_rng(0)
    p = rng.uniform(0.0, 1.0, size=10_000)
    y = (rng.uniform(0.0, 1.0, size=10_000) < p).astype(np.int64)
    ece = expected_calibration_error(p, y, n_bins=15)
    # for a perfectly-calibrated source the ECE should be small (<5%).
    assert ece < 0.05, f"ECE unexpectedly large: {ece}"


def main() -> None:
    fns = [
        test_recall_at_fpr_basic,
        test_bootstrap_ci_shrinks_with_n,
        test_per_size_recall_buckets,
        test_pareto_filter,
        test_calibration_does_not_change_recall_at_fpr,
        test_ece_perfectly_calibrated,
    ]
    for fn in fns:
        print(f"[run] {fn.__name__}")
        fn()
        print(f"[ ok] {fn.__name__}")


if __name__ == "__main__":
    main()
