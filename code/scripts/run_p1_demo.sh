#!/usr/bin/env bash
# Single-category PatchCore demo for P1 (IF-PROTO).
# Train -> dump test scores -> evaluate with the IF-PROTO module.

set -euo pipefail

CATEGORY="${1:-bottle}"
SEED="${2:-42}"
CONFIG="${3:-configs/p1_protocol.yaml}"

OUT="./results/p1/patchcore_${CATEGORY}_seed${SEED}"
mkdir -p "${OUT}"

# Step 1: train + persist anomalib's test scores
python -m src.train \
    --config "${CONFIG}" \
    --model patchcore \
    --category "${CATEGORY}" \
    --seed "${SEED}" \
    --output "${OUT}"

# Step 2: IF-PROTO evaluation on the dumped score npz.
# (anomalib writes per-image predictions; a small helper script is added in
#  the GPU-machine phase to convert that into the expected .npz layout.)
python -m src.evaluate \
    --config "${CONFIG}" \
    --scores-npz "${OUT}/test_scores.npz" \
    --output "${OUT}/protocol.json"

echo "[done] ${OUT}/protocol.json"
