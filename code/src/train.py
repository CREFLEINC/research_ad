"""anomalib Engine driver — single-category training.

Usage:
    python -m src.train --config configs/p1_protocol.yaml \
                        --model patchcore --category bottle --seed 42

For 5 models × 5 categories × 3 seeds = 75 runs; orchestrated by
`scripts/run_p1_demo.sh` (single demo) and `scripts/run_p1_full.sh` (full
grid; created in the GPU-machine phase).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from .utils import set_seed


def _build_model(model_cfg: dict):
    name = model_cfg["name"].lower()
    if name == "patchcore":
        from anomalib.models import Patchcore
        return Patchcore(
            backbone=model_cfg.get("backbone", "wide_resnet50_2"),
            layers=tuple(model_cfg.get("layers", ["layer2", "layer3"])),
            coreset_sampling_ratio=model_cfg.get("coreset_sampling_ratio", 0.1),
            num_neighbors=model_cfg.get("num_neighbors", 9),
        )
    if name == "efficient_ad":
        from anomalib.models import EfficientAd
        return EfficientAd(model_size=model_cfg.get("model_size", "small"))
    if name == "fastflow":
        from anomalib.models import Fastflow
        return Fastflow(backbone=model_cfg.get("backbone", "wide_resnet50_2"))
    if name == "rd4ad":
        from anomalib.models import ReverseDistillation
        return ReverseDistillation(backbone=model_cfg.get("backbone", "wide_resnet50_2"))
    if name == "dinomaly_base":
        raise NotImplementedError(
            "Dinomaly fork is not yet merged into anomalib (Issue #2782). "
            "Run it from the upstream `guojiajeremy/Dinomaly` checkout in a "
            "separate env and feed scores via ZeroShotScores."
        )
    raise ValueError(f"Unknown model: {name}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument("--model", required=True, help="model name as in config models[*].name")
    p.add_argument("--category", required=True)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--output", default=None)
    args = p.parse_args(argv)

    set_seed(args.seed)

    cfg = yaml.safe_load(Path(args.config).read_text())
    model_cfg = next(m for m in cfg["models"] if m["name"] == args.model)
    ds_cfg = dict(cfg["dataset"])
    ds_cfg["category"] = args.category

    # anomalib imports are deferred to here so that this script's --help works
    # even when anomalib is not installed.
    from anomalib.engine import Engine
    from .data.datasets import build_datamodule

    datamodule = build_datamodule(ds_cfg)
    model = _build_model(model_cfg)

    out_root = Path(args.output or cfg["output"]["root"]) / f"{args.model}_{args.category}_seed{args.seed}"
    engine = Engine(default_root_dir=str(out_root))
    engine.fit(model=model, datamodule=datamodule)
    results = engine.test(model=model, datamodule=datamodule)

    # Persist anomalib's standard metrics; recall@FPR is computed in evaluate.py
    # over the predicted scores dumped by anomalib.
    print(f"Done: {args.model}/{args.category}/seed={args.seed} -> {out_root}")
    print(f"anomalib test summary: {results}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
