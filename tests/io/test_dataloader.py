from __future__ import annotations

from typing import Iterable

import numpy as np
from numpy.typing import NDArray

from dev_environment.data import BaseTimeSeries
from dev_environment.io import (
    CollatedStreamDataset,
    IterableDataSourceAdapter,
    StreamDataLoader,
)


def make_blocks(num_blocks: int = 3) -> Iterable[BaseTimeSeries]:
    for idx in range(num_blocks):
        values: NDArray[np.float64] = np.full((4, 1), idx, dtype=np.float64)
        yield BaseTimeSeries(values=values, sample_rate=10.0, start_timestamp=0.0)


def test_stream_dataloader_consumes_block_by_block() -> None:
    adapter = IterableDataSourceAdapter(make_blocks())
    dataset = CollatedStreamDataset(adapter)
    loader = StreamDataLoader(dataset)

    blocks = list(loader)
    assert len(blocks) == 3
    assert [block.metadata.get("block_index") for block in blocks] == [None, None, None]


def test_stream_dataloader_respects_max_blocks() -> None:
    adapter = IterableDataSourceAdapter(make_blocks())
    dataset = CollatedStreamDataset(adapter)
    loader = StreamDataLoader(dataset, max_blocks=1)

    blocks = list(loader)
    assert len(blocks) == 1


def test_stream_dataloader_reset() -> None:
    adapter = IterableDataSourceAdapter(make_blocks())
    dataset = CollatedStreamDataset(adapter)
    loader = StreamDataLoader(dataset, max_blocks=2)

    first_pass = list(loader)
    second_pass = list(loader)

    assert len(first_pass) == len(second_pass) == 2
