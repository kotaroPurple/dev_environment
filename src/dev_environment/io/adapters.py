"""Data source adapters for sequential block acquisition."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Iterator, List, Sequence, TypeVar

T = TypeVar("T")


class DataSourceAdapter(ABC):
    """Abstract interface that exposes sequential block reads."""

    @abstractmethod
    def read_block(self) -> T | None:
        """Return the next raw block or ``None`` when the stream is exhausted."""

    def reset(self) -> None:
        """Reset the stream to its initial position if supported."""

        raise NotImplementedError


class IterableDataSourceAdapter(DataSourceAdapter[T]):
    """Simple adapter that steps through an in-memory iterable."""

    def __init__(self, data: Iterable[T], *, cycle: bool = False) -> None:
        self._original: List[T] = list(data)
        self._cycle = cycle
        self._cursor = 0

    def read_block(self) -> T | None:
        if not self._original:
            return None

        if self._cursor >= len(self._original):
            if not self._cycle:
                return None

            self._cursor = 0

        item = self._original[self._cursor]
        self._cursor += 1
        return item

    def reset(self) -> None:
        self._cursor = 0

    def __iter__(self) -> Iterator[T]:
        for item in self._original:
            yield item

    def __len__(self) -> int:
        return len(self._original)


class SequenceDataSourceAdapter(DataSourceAdapter[T]):
    """Adapter backed by a random-access sequence."""

    def __init__(self, data: Sequence[T]) -> None:
        self._data = data
        self._cursor = 0

    def read_block(self) -> T | None:
        if self._cursor >= len(self._data):
            return None

        item = self._data[self._cursor]
        self._cursor += 1
        return item

    def reset(self) -> None:
        self._cursor = 0

    def __len__(self) -> int:
        return len(self._data)
