"""Entry point for the minimal sequential pipeline."""

from __future__ import annotations

from typing import Iterable

import numpy as np

from .loader import iter_blocks
from .process import normalize


def run(blocks: Iterable[np.ndarray] | None = None) -> None:
    """Process blocks sequentially and print basic statistics."""

    if blocks is None:
        blocks = iter_blocks()

    for index, block in enumerate(blocks):
        normalised = normalize(block)
        peak = np.max(np.abs(normalised))
        first = normalised[0] if len(normalised) else float("nan")
        print(f"block {index}: samples={len(block)}, peak={peak:.3f}, first={first:.3f}")


if __name__ == "__main__":  # pragma: no cover - manual execution helper
    run()
