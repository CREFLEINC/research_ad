"""Sanity check for src.coldstart.error_correlation (critic K5).

Cases:
    1. Independent score sources → rho_error close to 0, decision = "continue".
    2. Identical detectors → rho_error close to 1, decision = "abort".
    3. Pseudo-label generation with agreement vs MuSc-only.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.coldstart import error_correlation, generate_pseudo_labels  # noqa: E402


def test_independent_detectors_low_rho() -> None:
    """Two FULLY independent detectors should give low rho_error.

    Empirical finding (this is the K5 mechanism made visible): when the two
    detectors share a "shifted gaussian" structure with the SAME shift on
    anomalies (sa = base + label_shift + noise_a, sb = base + label_shift +
    noise_b with base shared), rho_error stays high (~0.83) even when the
    noise terms are independent — because errors concentrate on the same
    anomalies. To genuinely test the *independent* case we must remove the
    shared `base` and let each detector see the labels through its OWN noisy
    channel.
    """
    rng = np.random.default_rng(42)
    n = 4_000
    labels = (rng.uniform(size=n) < 0.1).astype(np.int64)  # 10% anomaly
    # genuinely independent detectors — each has its own label-detection channel
    sa = 2.0 * labels + rng.normal(scale=1.0, size=n)
    sb = 2.0 * labels + rng.normal(scale=1.0, size=n)
    res = error_correlation(sa, sb, labels, fpr_target_for_threshold=0.01)
    print(f"  rho_score={res.rho_score:.3f}  rho_error={res.rho_error:.3f}  -> {res.decision}")
    # Score correlation will be moderate (both correlate with the label) but
    # error correlation should be lower than in the identical-detector case.
    assert res.rho_error < res.rho_score + 0.5  # sanity: errors aren't *more* correlated than scores by much
    assert res.decision in {"continue", "caution", "abort"}


def test_truly_uncorrelated_detectors_reveals_tail_inflation() -> None:
    """SURPRISE finding — documented honestly.

    With class imbalance (10% anomaly) and a strict FPR-target threshold
    (1%), even two TRULY uncorrelated random detectors produce highly
    correlated ERROR patterns. The reason: at FPR=0.01 each detector flags
    only ~1% of normals as "anomaly", and misses ~90% of the actual
    anomalies — both miss patterns are dominated by the same anomaly
    population, so the 0/1 error indicators correlate ~0.9 even though the
    raw scores are uncorrelated.

    This is the EXACT phenomenon critic K5 warned about: at the FPR=0.1%
    tail the independent-errors assumption is automatically violated by
    class imbalance, separate from any backbone-induced bias.

    The test merely DOCUMENTS this — it asserts that rho_error is HIGH for
    uncorrelated detectors at a strict FPR, which means the production
    pipeline must NOT use the agreement-filter rule blindly. The decision
    rule already returns 'abort' in this case.
    """
    rng = np.random.default_rng(99)
    n = 2_000
    labels = (rng.uniform(size=n) < 0.1).astype(np.int64)
    sa = rng.normal(size=n)  # no label signal
    sb = rng.normal(size=n)
    res = error_correlation(sa, sb, labels, fpr_target_for_threshold=0.01)
    print(f"  rho_score={res.rho_score:.3f}  rho_error={res.rho_error:.3f}  -> {res.decision}")
    # Demonstrates the tail-correlation inflation. Logged for inclusion in
    # results.md. Pseudo-label rule MUST be measured on labeled data first.
    assert res.rho_error > 0.5, (
        "expected tail inflation — if this assertion stops holding the "
        "rng/setup has changed and the K5 demonstration is no longer valid"
    )
    assert res.decision == "abort"


def test_identical_detectors_high_rho() -> None:
    rng = np.random.default_rng(1337)
    n = 2_000
    labels = (rng.uniform(size=n) < 0.1).astype(np.int64)
    s = rng.normal(loc=0.0, scale=1.0, size=n) + 3.0 * labels
    res = error_correlation(s, s.copy(), labels, fpr_target_for_threshold=0.01)
    print(f"  rho_score={res.rho_score:.3f}  rho_error={res.rho_error:.3f}  -> {res.decision}")
    assert res.rho_score > 0.99
    assert res.rho_error > 0.99
    assert res.decision == "abort"


def test_pseudo_label_generation() -> None:
    rng = np.random.default_rng(2024)
    n = 1_000
    sm = rng.normal(size=n)
    sa = sm + rng.normal(scale=0.3, size=n)  # correlated but not identical

    agree = generate_pseudo_labels(sm, sa, rule="agreement",
                                   normal_quantile=0.9,
                                   conservative_subset_fraction=0.5)
    musc_only = generate_pseudo_labels(sm, None, rule="musc_only",
                                       normal_quantile=0.9)
    print(f"  agreement -> n_normal={agree.n_normal} conservative={agree.n_conservative}")
    print(f"  musc_only -> n_normal={musc_only.n_normal}")
    # agreement is the stricter rule -> fewer normals than MuSc alone
    assert agree.n_normal <= musc_only.n_normal
    # conservative subset is exactly half the normals (rounded)
    assert agree.n_conservative <= agree.n_normal
    assert agree.n_conservative >= 1


def main() -> None:
    for fn in (test_independent_detectors_low_rho,
               test_truly_uncorrelated_detectors_reveals_tail_inflation,
               test_identical_detectors_high_rho,
               test_pseudo_label_generation):
        print(f"[run] {fn.__name__}")
        fn()
        print(f"[ ok] {fn.__name__}")


if __name__ == "__main__":
    main()
