"""Zero-shot detector wrappers for P2 (CS-BRIDGE).

Two MIT-licensed repos are used as installed-from-source dependencies:
    - MuSc          (xrli-U/MuSc)         — mutual scoring, no training
    - AnomalyCLIP   (zqhang/AnomalyCLIP)  — prompt-tuned CLIP

Because the two repos pin overlapping but slightly different `timm` and
`open_clip` versions, the recommendation in `pre_check.md` is to use
SEPARATE conda envs, dump scores to `.npy`, and feed both arrays to the
P2 modules in this repo.

This wrapper file documents the EXPECTED call signature so the upstream
inference script can be written quickly when the GPU machine is available.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class ZeroShotScores:
    """Persisted output of a zero-shot detector for a dataset split."""
    image_paths: list[str]
    image_scores: np.ndarray  # higher = more anomalous
    # pixel_scores intentionally omitted in this minimal wrapper — P2 only
    # uses image-level scores for pseudo-labeling.

    @classmethod
    def load(cls, npz_path: str | Path) -> "ZeroShotScores":
        npz_path = Path(npz_path)
        d = np.load(npz_path, allow_pickle=True)
        return cls(
            image_paths=list(d["image_paths"]),
            image_scores=np.asarray(d["image_scores"], dtype=np.float64),
        )

    def save(self, npz_path: str | Path) -> None:
        npz_path = Path(npz_path)
        npz_path.parent.mkdir(parents=True, exist_ok=True)
        np.savez(
            npz_path,
            image_paths=np.asarray(self.image_paths, dtype=object),
            image_scores=self.image_scores,
        )


# Placeholder inference signatures — implemented in their own envs.
def run_musc(images: Iterable[str], cfg: dict) -> ZeroShotScores:
    """Stub.

    Implementation will live in `scripts/run_musc.py` and import the
    `xrli-U/MuSc` repo as a local checkout. It dumps a `.npz` consumed by
    `coldstart/musc_pseudo_label.py`.
    """
    raise NotImplementedError(
        "Run xrli-U/MuSc in its own env and save output via ZeroShotScores.save()."
    )


def run_anomaly_clip(images: Iterable[str], cfg: dict) -> ZeroShotScores:
    """Stub. See run_musc for the same pattern."""
    raise NotImplementedError(
        "Run zqhang/AnomalyCLIP in its own env and save output via ZeroShotScores.save()."
    )
