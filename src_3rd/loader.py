"""Helper to build sample datasets for third-stage prototype."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterator

import numpy as np

from .data import TimeSeriesBlock
from .dataset import IterableDataset


def sine_dataset(
    num_blocks: int = 3,
    *,
    block_size: int = 64,
    sample_rate: float = 256.0,
) -> IterableDataset:
    blocks = list(_generate_blocks(num_blocks, block_size=block_size, sample_rate=sample_rate))
    return IterableDataset(blocks)


def _generate_blocks(
    num_blocks: int,
    *,
    block_size: int,
    sample_rate: float,
) -> Iterator[TimeSeriesBlock]:
    now = datetime.now(tz=timezone.utc)
    grid = np.linspace(0.0, 2 * np.pi, block_size, endpoint=False)

    for index in range(num_blocks):
        phase = index * np.pi / 5
        values = np.sin(grid + phase)
        metadata = {"block_index": index}
        yield TimeSeriesBlock(
            values=values,
            sample_rate=sample_rate,
            timestamp=now,
            metadata=metadata,
        )


def bulk_dataset(
    duration_seconds: int = 120,
    *,
    sample_rate: float = 256.0,
) -> IterableDataset:
    now = datetime.now(tz=timezone.utc)
    total_samples = int(duration_seconds * sample_rate)
    timeline = np.linspace(0.0, duration_seconds, total_samples, endpoint=False)
    values = np.sin(2 * np.pi * timeline / duration_seconds)
    metadata = {"duration_seconds": duration_seconds}
    block = TimeSeriesBlock(
        values=values,
        sample_rate=sample_rate,
        timestamp=now,
        metadata=metadata,
    )
    return IterableDataset([block])
