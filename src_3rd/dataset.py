"""Dataset abstractions for the third-stage prototype."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Iterator, List

from .data import TimeSeriesBlock


class Dataset(ABC):
    """Minimal dataset interface."""

    @abstractmethod
    def __iter__(self) -> Iterator[TimeSeriesBlock]:
        ...

    def __len__(self) -> int:
        raise TypeError("Dataset length not supported")


class IterableDataset(Dataset):
    """Wrap an iterable of blocks as a dataset."""

    def __init__(self, blocks: Iterable[TimeSeriesBlock]) -> None:
        self._blocks: List[TimeSeriesBlock] = list(blocks)

    def __iter__(self) -> Iterator[TimeSeriesBlock]:
        for block in self._blocks:
            yield block

    def __len__(self) -> int:
        return len(self._blocks)
