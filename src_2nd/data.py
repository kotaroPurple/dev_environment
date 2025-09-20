"""Dataclasses and helpers for second-stage pipeline prototype."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import numpy as np
import numpy.typing as npt

Array = npt.NDArray[np.float64]


def ensure_array(values: npt.ArrayLike) -> Array:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim == 1:
        return array
    raise ValueError("TimeSeriesBlock expects 1-D arrays in this stage")


@dataclass(slots=True, frozen=True)
class TimeSeriesBlock:
    """Immutable time-series block with minimal metadata."""

    values: Array
    sample_rate: float
    timestamp: datetime
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        array = ensure_array(self.values)
        if array.size == 0:
            raise ValueError("values must not be empty")
        object.__setattr__(self, "values", array)

        if self.sample_rate <= 0:
            raise ValueError("sample_rate must be positive")

        if self.timestamp.tzinfo is None:
            object.__setattr__(self, "timestamp", self.timestamp.replace(tzinfo=timezone.utc))

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
        timestamp: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "TimeSeriesBlock":
        new_values = ensure_array(values) if values is not None else self.values.copy()
        new_timestamp = timestamp or self.timestamp
        new_metadata = dict(metadata) if metadata is not None else dict(self.metadata)
        return TimeSeriesBlock(
            values=new_values,
            sample_rate=self.sample_rate,
            timestamp=new_timestamp,
            metadata=new_metadata,
        )


def make_block(
    values: npt.ArrayLike,
    *,
    sample_rate: float,
    timestamp: datetime | None = None,
    **metadata: Any,
) -> TimeSeriesBlock:
    ts = timestamp or datetime.now(tz=timezone.utc)
    return TimeSeriesBlock(
        values=values,
        sample_rate=sample_rate,
        timestamp=ts,
        metadata=metadata,
    )
