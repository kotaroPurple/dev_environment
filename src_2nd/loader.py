"""Sequential data loader for second-stage prototype."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, Iterator

import numpy as np

from .data import TimeSeriesBlock, make_block


def generate_sine_blocks(
    num_blocks: int = 3,
    *,
    block_size: int = 32,
    sample_rate: float = 128.0,
) -> Iterator[TimeSeriesBlock]:
    """Yield deterministic sine wave blocks with phase offsets."""

    now = datetime.now(tz=timezone.utc)
    timeline = np.linspace(0.0, 2 * np.pi, block_size, endpoint=False)
    for index in range(num_blocks):
        phase = index * np.pi / 6
        values = np.sin(timeline + phase)
        yield make_block(values, sample_rate=sample_rate, timestamp=now, block_index=index)


class SimpleDataLoader:
    """Very small wrapper that iterates over pre-built blocks."""

    def __init__(self, blocks: Iterable[TimeSeriesBlock]):
        self._blocks = list(blocks)

    def __iter__(self) -> Iterator[TimeSeriesBlock]:
        for block in self._blocks:
            yield block

    def __len__(self) -> int:
        return len(self._blocks)
