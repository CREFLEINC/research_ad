# IF-PROTO + CS-BRIDGE — Implementation

Code accompanying `_workspace/03_research/consolidated_proposals.md` adopted plans **P1 (IF-PROTO)** and **P2 (CS-BRIDGE)**.

Two independent contributions (per `critique_notes.md` K6 — no "unified" label until pseudo-label-based calibration is empirically shown to lower ECE):

- **P1 — Industrial-FPR Evaluation Protocol**: `recall@FPR ∈ {0.1%, 0.5%, 1%, 5%}` with 100-iter bootstrap 95% CI, per-defect-size recall bins, `latency × VRAM × recall` Pareto frontier, Platt/Isotonic calibration as a side result.
- **P2 — Cold-Start Bridge**: MuSc + AnomalyCLIP zero-shot agreement → pseudo-labels → PatchCore training with 4-8 normal samples. Error-correlation `rho` between MuSc and AnomalyCLIP is measured first (critic K5).

## Status

This repository contains the **code scaffold and metric modules**, validated against synthetic score distributions. **No real MVTec training was run in the current session** — see `_workspace/04_implementation/results.md` for what is measured vs unmeasured and the 13-15 day execution plan.

## Layout

```
code/
├── README.md
├── requirements.txt            pinned versions (torch 2.4.1, anomalib 2.4.2, ...)
├── configs/
│   ├── p1_protocol.yaml        five-SOTA evaluation protocol
│   └── p2_coldstart.yaml       cold-start scenario knobs
├── src/
│   ├── data/datasets.py        anomalib MVTecAD / Visa wrappers
│   ├── models/zero_shot.py     MuSc / AnomalyCLIP loader skeletons
│   ├── metrics/
│   │   ├── recall_at_fpr.py    recall@FPR + bootstrap CI (validated)
│   │   ├── per_size_recall.py  per-defect-size bin recall
│   │   ├── pareto.py           3-axis latency × VRAM × recall Pareto frontier
│   │   └── ece.py              expected calibration error (validated)
│   ├── calibration/
│   │   └── platt_isotonic.py   sklearn wrappers; ranking-invariance noted (K1)
│   ├── coldstart/
│   │   ├── musc_pseudo_label.py     agreement filter + pseudo-label gen
│   │   └── error_correlation.py     rho between two zero-shot models (K5)
│   ├── train.py                anomalib Engine().fit() driver
│   ├── evaluate.py             P1 protocol runner
│   └── utils/seed.py           reproducible seed control
├── scripts/
│   ├── download_data.sh        anomalib's MVTecAD downloader
│   └── run_p1_demo.sh          single-category demo
└── tests/
    ├── test_metrics_synth.py   metric-module sanity tests (run in current session)
    └── test_correlation.py     K5 correlation module sanity test
```

## Reproduction

```bash
# 1. environment
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. data (downloads MVTec AD into ./datasets — about 5 GB)
bash scripts/download_data.sh

# 3. P1: train PatchCore on one category and emit a recall@FPR CI
bash scripts/run_p1_demo.sh bottle

# 4. metric-module sanity (no GPU needed)
python -m tests.test_metrics_synth
python -m tests.test_correlation
```

## Seeds

`utils.seed.set_seed(seed)` sets `random`, `numpy`, `torch`, and `torch.cuda`. Three seeds for all reported numbers: **42, 1337, 2024** (per `implementation-and-verification` skill §3).

## Critic K1 — calibration ranking-invariance (must read)

Platt and isotonic regression are **monotonic** post-hoc transforms. For a *single* model the ROC curve and therefore `recall@FPR` are unchanged by calibration. What calibration *does* change is the absolute-threshold accuracy (ECE / reliability diagram). Any improvement in `recall@FPR` from a "calibrated" pipeline must come from **score fusion / stacking** (multiple models combined after calibration), not calibration itself. This is asserted in code comments in `src/calibration/platt_isotonic.py` and in the evaluation report layout.
