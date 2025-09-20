"""Single-step processing for the first-stage prototype."""

from __future__ import annotations

import numpy as np


def normalize(block: np.ndarray, *, eps: float = 1e-9) -> np.ndarray:
    """Scale ``block`` so that its max absolute value becomes 1."""

    peak = np.max(np.abs(block))
    if peak < eps:
        return block.copy()
    return block / peak
