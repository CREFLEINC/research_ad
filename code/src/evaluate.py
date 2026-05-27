"""P1 evaluation driver — consume anomalib's per-image score dump and emit:

    - recall@FPR={0.001, 0.005, 0.01, 0.05} with 100-iter bootstrap 95% CI
    - per-defect-size recall bins
    - ECE (calibration ablation: none / Platt / isotonic)
    - latency / VRAM (when --measure-latency)

Inputs:
    --scores-npz: a .npz containing
        image_scores (float[N]), labels (int[N]),
        mask_area_px2 (float[N], optional, NaN for normals)

Usage:
    python -m src.evaluate \
        --config configs/p1_protocol.yaml \
        --scores-npz ./results/p1/patchcore_bottle_seed42/test_scores.npz \
        --output ./results/p1/patchcore_bottle_seed42/protocol.json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np
import yaml

from .metrics import (
    recall_at_fpr_with_ci,
    ci_half_width,
    per_size_recall_at_fpr,
    expected_calibration_error,
)
from .calibration import fit_platt, fit_isotonic, apply_calibrator, score_to_prob_minmax


def _evaluate_protocol(
    scores: np.ndarray,
    labels: np.ndarray,
    mask_area: np.ndarray | None,
    cfg: dict,
) -> dict:
    metrics_cfg = cfg["metrics"]
    fpr_targets = metrics_cfg["recall_at_fpr"]["fpr_targets"]
    bootstrap_n = metrics_cfg["recall_at_fpr"]["bootstrap_n"]
    ci = metrics_cfg["recall_at_fpr"]["ci"]
    random_state = metrics_cfg["recall_at_fpr"].get("random_state", 42)

    normal_scores = scores[labels == 0]
    anomaly_scores = scores[labels == 1]

    out: dict = {"recall_at_fpr": []}
    for t in fpr_targets:
        res = recall_at_fpr_with_ci(
            normal_scores, anomaly_scores, t, bootstrap_n, ci, random_state
        )
        d = asdict(res)
        d["ci_half_width"] = ci_half_width(res)
        # P1 abort criterion (consolidated_proposals.md §2 P1)
        d["abort_recommended"] = d["ci_half_width"] > 0.05
        out["recall_at_fpr"].append(d)

    # Per-defect-size bins (uses 0.001 as the canonical FPR target)
    if mask_area is not None:
        bin_boundaries = metrics_cfg["per_size_bins"]["boundaries_px2"]
        # only the anomalies contribute to size bins; mask_area for normals is NaN
        anomaly_mask_area = mask_area[labels == 1]
        psr = per_size_recall_at_fpr(
            normal_scores=normal_scores,
            anomaly_scores=anomaly_scores,
            anomaly_defect_area_px2=anomaly_mask_area,
            bin_boundaries=bin_boundaries,
            fpr_target=0.001,
            bootstrap_n=bootstrap_n,
            ci=ci,
            random_state=random_state,
        )
        out["per_size_recall"] = {
            "bin_edges": list(psr.bin_edges),
            "bin_counts": psr.bin_counts,
            "per_bin": [asdict(r) for r in psr.per_bin],
        }

    # Calibration ablation
    # NOTE (critic K1): single-model recall@FPR is unchanged by Platt/isotonic;
    # only ECE / reliability move. This block reports ECE only, by design.
    n_bins = metrics_cfg["ece"]["n_bins"]
    base_prob = score_to_prob_minmax(scores)
    ece_none = expected_calibration_error(base_prob, labels, n_bins=n_bins)
    out["ece"] = {"none": ece_none}

    # split scores into a calibration fit set vs a held-out eval set (50/50)
    # only used for the ablation, NOT for the main recall@FPR numbers.
    rng = np.random.default_rng(random_state)
    idx = np.arange(scores.size)
    rng.shuffle(idx)
    cut = idx.size // 2
    fit_idx, eval_idx = idx[:cut], idx[cut:]
    if fit_idx.size > 1 and eval_idx.size > 1:
        try:
            platt = fit_platt(scores[fit_idx], labels[fit_idx])
            p_platt = apply_calibrator(platt, scores[eval_idx])
            out["ece"]["platt"] = expected_calibration_error(
                p_platt, labels[eval_idx], n_bins=n_bins
            )

            iso = fit_isotonic(scores[fit_idx], labels[fit_idx])
            p_iso = apply_calibrator(iso, scores[eval_idx])
            out["ece"]["isotonic"] = expected_calibration_error(
                p_iso, labels[eval_idx], n_bins=n_bins
            )
        except ImportError:
            out["ece"]["note"] = "sklearn not installed; Platt/isotonic skipped"

    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument("--scores-npz", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args(argv)

    cfg = yaml.safe_load(Path(args.config).read_text())
    npz = np.load(args.scores_npz, allow_pickle=True)
    scores = np.asarray(npz["image_scores"], dtype=np.float64)
    labels = np.asarray(npz["labels"], dtype=np.int64)
    mask_area = np.asarray(npz["mask_area_px2"], dtype=np.float64) if "mask_area_px2" in npz.files else None

    result = _evaluate_protocol(scores, labels, mask_area, cfg)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
