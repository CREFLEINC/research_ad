"""Reproducible seeding across Python random, numpy, and torch."""

from __future__ import annotations

import os
import random


def set_seed(seed: int) -> None:
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    try:
        import numpy as np
        np.random.seed(seed)
    except ImportError:
        pass
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        # Deterministic algorithms have a non-trivial perf hit; opt in via env.
        if os.environ.get("ANOMALY_DETERMINISTIC") == "1":
            torch.use_deterministic_algorithms(True, warn_only=True)
    except ImportError:
        pass
