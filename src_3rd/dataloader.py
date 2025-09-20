"""Sequential data loader for the third-stage prototype."""

from __future__ import annotations

from typing import Iterator

from .data import TimeSeriesBlock
from .dataset import Dataset


class DataLoader:
    """Lightweight loader that yields blocks from a dataset."""

    def __init__(self, dataset: Dataset) -> None:
        self._dataset = dataset

    def __iter__(self) -> Iterator[TimeSeriesBlock]:
        for block in self._dataset:
            yield block
