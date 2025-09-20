"""Buffer primitives for sharing blocks between sequential processing stages."""

from __future__ import annotations

from collections import OrderedDict
from typing import Generic, Iterable, Iterator, MutableMapping, TypeVar

T = TypeVar("T")


class BlockBuffer(Generic[T]):
    """Simple ordered buffer that stores the latest block per key."""

    def __init__(self) -> None:
        self._store: MutableMapping[str, T] = OrderedDict()

    def push(self, key: str, block: T) -> None:
        """Insert or replace a block for ``key`` while keeping insertion order."""

        if key in self._store:
            del self._store[key]

        self._store[key] = block

    def get(self, key: str) -> T:
        """Return the block associated with ``key``."""

        if key not in self._store:
            raise KeyError(f"Block '{key}' not found")

        return self._store[key]

    def pop(self, key: str) -> T:
        """Remove and return the block for ``key``."""

        if key not in self._store:
            raise KeyError(f"Block '{key}' not found")

        block = self._store[key]
        del self._store[key]
        return block

    def latest(self) -> T:
        """Return the most recently inserted block."""

        if not self._store:
            raise LookupError("BlockBuffer is empty")

        return next(reversed(self._store.values()))

    def keys(self) -> Iterable[str]:
        return list(self._store.keys())

    def values(self) -> Iterable[T]:
        return list(self._store.values())

    def items(self) -> Iterable[tuple[str, T]]:
        return list(self._store.items())

    def clear(self) -> None:
        self._store.clear()

    def __contains__(self, key: object) -> bool:
        return key in self._store

    def __len__(self) -> int:
        return len(self._store)

    def __iter__(self) -> Iterator[tuple[str, T]]:
        return iter(self._store.items())
