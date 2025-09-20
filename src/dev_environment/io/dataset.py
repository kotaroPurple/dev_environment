"""Sequential dataset abstractions for streaming blocks."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Generic, Iterator, List, Optional, Sequence, TypeVar

from dev_environment.data import collate_block

from .adapters import DataSourceAdapter

RawBlock = TypeVar("RawBlock")
Block = TypeVar("Block")


class StreamDataset(ABC, Generic[Block]):
    """Abstract dataset that yields blocks sequentially."""

    def __iter__(self) -> Iterator[Block]:
        for block in self.stream():
            yield block

    def stream(self) -> Iterator[Block]:
        while True:
            block = self.next_block()
            if block is None:
                break
            yield block

    @abstractmethod
    def next_block(self) -> Block | None:
        """Return the next block or ``None`` when the dataset is exhausted."""

    def reset(self) -> None:
        """Reset the dataset to its initial position if supported."""

        raise NotImplementedError

    def __len__(self) -> int:
        raise TypeError("StreamDataset does not expose length by default")


class IteratorStreamDataset(StreamDataset[Block]):
    """Dataset backed by a user-provided iterator factory."""

    def __init__(self, factory: Callable[[], Iterator[Block]]) -> None:
        self._factory = factory
        self._iterator: Optional[Iterator[Block]] = None

    def next_block(self) -> Block | None:
        if self._iterator is None:
            self._iterator = self._factory()

        try:
            return next(self._iterator)
        except StopIteration:
            return None

    def reset(self) -> None:
        self._iterator = None


class AdapterStreamDataset(StreamDataset[Block], Generic[RawBlock, Block]):
    """Dataset that wraps a ``DataSourceAdapter`` with optional transformation."""

    def __init__(
        self,
        source: DataSourceAdapter[RawBlock],
        *,
        transform: Callable[[RawBlock], Block] | None = None,
    ) -> None:
        self._source = source
        self._transform = transform or (lambda item: item)  # type: ignore[assignment]

    def next_block(self) -> Block | None:
        raw = self._source.read_block()
        if raw is None:
            return None
        return self._transform(raw)

    def reset(self) -> None:
        try:
            self._source.reset()
        except NotImplementedError:
            pass

    def __len__(self) -> int:
        if hasattr(self._source, "__len__"):
            return len(self._source)  # type: ignore[arg-type]
        raise TypeError("Underlying source does not expose length")


class BufferedStreamDataset(StreamDataset[Block]):
    """Dataset that replays a finite list of precomputed blocks."""

    def __init__(self, blocks: Sequence[Block]) -> None:
        self._blocks: List[Block] = list(blocks)
        self._cursor = 0

    def next_block(self) -> Block | None:
        if self._cursor >= len(self._blocks):
            return None
        block = self._blocks[self._cursor]
        self._cursor += 1
        return block

    def reset(self) -> None:
        self._cursor = 0

    def __len__(self) -> int:
        return len(self._blocks)


class CollatedStreamDataset(AdapterStreamDataset[RawBlock, Block]):
    """Convenience wrapper that applies ``collate_block`` to raw samples."""

    def __init__(self, source: DataSourceAdapter[RawBlock], transform=None) -> None:
        super().__init__(source, transform=transform or collate_block)
