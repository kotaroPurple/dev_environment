"""Sequential data loader that coordinates block-by-block execution."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Generic, TypeVar

from dev_environment.data import BaseTimeSeries, collate_block

from .dataset import StreamDataset

RawBlock = TypeVar("RawBlock")
Block = TypeVar("Block", bound=BaseTimeSeries)


class StreamDataLoader(Generic[RawBlock, Block]):
    """Serial data loader that fetches one block at a time."""

    def __init__(
        self,
        dataset: StreamDataset[RawBlock],
        *,
        collate_fn: Callable[[RawBlock], Block] = collate_block,
        max_blocks: int | None = None,
    ) -> None:
        self._dataset = dataset
        self._collate_fn = collate_fn
        self._max_blocks = max_blocks
        self._consumed = 0
        self._exhausted = False

    def reset(self) -> None:
        self._dataset.reset()
        self._consumed = 0
        self._exhausted = False

    def __iter__(self) -> Iterator[Block]:
        self.reset()
        return self

    def __next__(self) -> Block:
        block = self.next_block()
        if block is None:
            raise StopIteration
        return block

    def next_block(self) -> Block | None:
        if self._exhausted:
            return None

        if self._max_blocks is not None and self._consumed >= self._max_blocks:
            self._exhausted = True
            return None

        raw_block = self._dataset.next_block()
        if raw_block is None:
            self._exhausted = True
            return None

        block = self._collate_fn(raw_block)
        self._consumed += 1
        return block

    @property
    def consumed_blocks(self) -> int:
        """Return the total number of blocks emitted since the last reset."""

        return self._consumed

    @property
    def is_exhausted(self) -> bool:
        """Whether the loader has no more blocks to provide."""

        return self._exhausted
