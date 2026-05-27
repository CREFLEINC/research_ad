"""Empirical study of the bootstrap-CI half-width as a function of sample size.

Motivation (consolidated_proposals.md §2 P1 abort criterion):
    "bootstrap 95% CI half-width > 5%p → fusion claims dropped".

The question this script answers experimentally:
    How many test samples (per category) do we need before the CI half-width
    is small enough to make SOTA-vs-SOTA comparisons informative?

We simulate a PatchCore-like score distribution (separable Gaussians with
moderate overlap, mu_anomaly = 2.5 sigma) and sweep N_normal in {50, 100,
200, 500, 1000, 5000}, anomaly count proportional. We report CI half-width
and the implied "go/no-go" for the protocol.

Run:
    python -m tests.test_ci_budget
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.metrics import recall_at_fpr_with_ci, ci_half_width  # noqa: E402


def main() -> None:
    print(f"{'N_normal':>10} {'N_anom':>8} {'fpr':>6} {'recall':>8} "
          f"{'ci_low':>8} {'ci_high':>8} {'half':>8} {'go/no-go':>10}")
    print("-" * 78)
    rng_master = np.random.default_rng(2024)
    for n_normal in (50, 100, 200, 500, 1000, 5000):
        n_anom = max(20, n_normal // 5)
        # use a fresh rng for each row so the same seed gives the same numbers
        rng = np.random.default_rng(int(rng_master.integers(2**31)))
        n = rng.normal(loc=0.0, scale=1.0, size=n_normal)
        a = rng.normal(loc=2.5, scale=1.0, size=n_anom)
        for fpr in (0.001, 0.01):
            res = recall_at_fpr_with_ci(n, a, fpr_target=fpr, bootstrap_n=200,
                                        random_state=42)
            hw = ci_half_width(res)
            go = "PASS" if hw <= 0.05 else "fail"
            print(f"{n_normal:>10} {n_anom:>8} {fpr:>6.3f} "
                  f"{res.recall:>8.3f} {res.ci_low:>8.3f} {res.ci_high:>8.3f} "
                  f"{hw:>8.3f}  {go:>9}")


if __name__ == "__main__":
    main()
