#!/usr/bin/env bash
# Trigger anomalib's built-in MVTec AD downloader for one category at a time.
# anomalib downloads to <root>/<category>/{train,test,ground_truth}.
# Total MVTec AD is ~5 GB. CC BY-NC-SA 4.0 — non-commercial / academic.

set -euo pipefail

ROOT="${1:-./datasets/MVTecAD}"
mkdir -p "${ROOT}"

# anomalib MVTecAD datamodule auto-downloads on first instantiation.
python - <<PY
from anomalib.data import MVTecAD
for cat in ["bottle", "hazelnut", "cable", "capsule", "screw"]:
    print(f"[+] downloading MVTec AD: {cat}")
    dm = MVTecAD(root="${ROOT}", category=cat)
    dm.prepare_data()
print("done.")
PY
