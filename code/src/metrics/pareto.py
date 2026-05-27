"""3-axis Pareto frontier — IF-PROTO §1.4 (latency × VRAM × recall).

For anomaly detection the *desired* direction is:
    - higher recall@FPR=0.1%   (maximise)
    - lower latency (ms/image)  (minimise)
    - lower peak VRAM (MB)       (minimise)

A point is on the Pareto frontier iff no other point dominates it on all three
axes simultaneously.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PareToPoint:
    name: str
    latency_ms: float
    vram_mb: float
    recall: float


def pareto_frontier(points: list[PareToPoint]) -> list[PareToPoint]:
    """Return only the Pareto-non-dominated points.

    A dominates B iff:
        A.latency_ms <= B.latency_ms
        A.vram_mb    <= B.vram_mb
        A.recall     >= B.recall
        and at least one of the inequalities is strict.
    """
    out: list[PareToPoint] = []
    for i, p in enumerate(points):
        dominated = False
        for j, q in enumerate(points):
            if i == j:
                continue
            le_lat = q.latency_ms <= p.latency_ms
            le_vram = q.vram_mb <= p.vram_mb
            ge_rec = q.recall >= p.recall
            strict = (
                q.latency_ms < p.latency_ms
                or q.vram_mb < p.vram_mb
                or q.recall > p.recall
            )
            if le_lat and le_vram and ge_rec and strict:
                dominated = True
                break
        if not dominated:
            out.append(p)
    return out
