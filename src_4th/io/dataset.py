"""Dataset implementations for src_4th."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Iterator, List

from ..data import BaseTimeSeries


class Dataset(ABC):
    @abstractmethod
    def __iter__(self) -> Iterator[BaseTimeSeries]:  # pragma: no cover - interface
        ...

    def __len__(self) -> int:
        raise TypeError("Dataset length not available")


class IterableDataset(Dataset):
    def __init__(self, blocks: Iterable[BaseTimeSeries]) -> None:
        self._blocks: List[BaseTimeSeries] = list(blocks)

    def __iter__(self) -> Iterator[BaseTimeSeries]:
        for block in self._blocks:
            yield block

    def __len__(self) -> int:
        return len(self._blocks)
