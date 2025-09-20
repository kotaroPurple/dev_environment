"""Simple block generator for the first-stage prototype."""

from __future__ import annotations

from typing import Iterable, Iterator

import numpy as np


def iter_blocks(num_blocks: int = 3, block_size: int = 16) -> Iterator[np.ndarray]:
    """Yield ``num_blocks`` arrays of length ``block_size`` for demonstration."""

    for index in range(num_blocks):
        phase = index * np.pi / 4
        block = np.sin(np.linspace(0.0, 2 * np.pi, block_size, endpoint=False) + phase)
        yield block.astype(np.float64)


def load_from(iterable: Iterable[float], block_size: int) -> Iterator[np.ndarray]:
    """Yield arrays chunked from ``iterable`` in order."""

    chunk: list[float] = []
    for value in iterable:
        chunk.append(float(value))
        if len(chunk) == block_size:
            yield np.array(chunk, dtype=np.float64)
            chunk.clear()
    if chunk:
        yield np.array(chunk, dtype=np.float64)
