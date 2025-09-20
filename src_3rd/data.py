"""Data structures for the third-stage prototype."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict

import numpy as np
import numpy.typing as npt

Array = npt.NDArray[np.float64]


@dataclass(slots=True, frozen=True)
class TimeSeriesBlock:
    """Immutable block with 1-D samples and metadata."""

    values: Array
    sample_rate: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        array = np.asarray(self.values, dtype=np.float64)
        if array.ndim != 1 or array.size == 0:
            raise ValueError("TimeSeriesBlock expects non-empty 1-D arrays")
        object.__setattr__(self, "values", array)

        if self.sample_rate <= 0:
            raise ValueError("sample_rate must be positive")

        ts = self.timestamp
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        object.__setattr__(self, "timestamp", ts)

        object.__setattr__(self, "metadata", dict(self.metadata))

    @property
    def block_size(self) -> int:
        return int(self.values.shape[0])

    @property
    def duration_seconds(self) -> float:
        return float(self.block_size / self.sample_rate)

    def copy_with(
        self,
        *,
        values: npt.ArrayLike | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> "TimeSeriesBlock":
        new_values = (
            np.asarray(values, dtype=np.float64) if values is not None else self.values.copy()
        )
        new_metadata = dict(metadata) if metadata is not None else dict(self.metadata)
        return TimeSeriesBlock(
            values=new_values,
            sample_rate=self.sample_rate,
            timestamp=self.timestamp,
            metadata=new_metadata,
        )


class BlockBuffer:
    """Minimal buffer storing latest blocks keyed by name."""

    def __init__(self) -> None:
        self._store: Dict[str, TimeSeriesBlock] = {}

    def set(self, key: str, block: TimeSeriesBlock) -> None:
        self._store[key] = block

    def get(self, key: str) -> TimeSeriesBlock:
        if key not in self._store:
            raise KeyError(f"Key '{key}' not found in BlockBuffer")
        return self._store[key]

    def items(self) -> Dict[str, TimeSeriesBlock].items:
        return self._store.items()

    def clear(self) -> None:
        self._store.clear()
