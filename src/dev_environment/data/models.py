"""Core data structures for sequential time-series processing."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping

import numpy as np
import numpy.typing as npt

FloatArray = npt.NDArray[np.floating[Any]]


def _ensure_datetime(value: datetime | float | int | str) -> datetime:
    """Convert supported timestamp inputs into a ``datetime`` instance."""

    if isinstance(value, datetime):
        return value

    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)

    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError as error:  # pragma: no cover - defensive
            raise ValueError(f"Invalid ISO timestamp string: {value!r}") from error

        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)

        return parsed

    raise TypeError(f"Unsupported timestamp type: {type(value)!r}")


@dataclass(slots=True, frozen=True)
class BaseTimeSeries:
    """Immutable container for a block of time-series data."""

    values: FloatArray
    sample_rate: float
    start_timestamp: datetime
    metadata: Mapping[str, Any] | None = field(default=None)

    def __post_init__(self) -> None:
        values = np.asarray(self.values)
        if values.ndim == 0:
            raise ValueError("values must be at least 1-D")

        object.__setattr__(self, "values", values)

        if values.shape[0] == 0:
            raise ValueError("values must contain at least one sample")

        if self.sample_rate <= 0:
            raise ValueError("sample_rate must be positive")

        start_ts = _ensure_datetime(self.start_timestamp)
        object.__setattr__(self, "start_timestamp", start_ts)

        metadata = self.metadata or {}
        object.__setattr__(self, "metadata", dict(metadata))

    @property
    def block_size(self) -> int:
        """Return the number of temporal samples stored in this block."""

        return int(self.values.shape[0])

    @property
    def duration_seconds(self) -> float:
        """Duration of the block in seconds."""

        return float(self.block_size / self.sample_rate)

    @property
    def end_timestamp(self) -> datetime:
        """Compute the timestamp at which this block ends."""

        offset_seconds = (self.block_size - 1) / self.sample_rate
        return self.start_timestamp + timedelta(seconds=offset_seconds)

    def time_axis(self) -> FloatArray:
        """Return relative time offsets in seconds for each sample in the block."""

        return np.arange(self.block_size, dtype=np.float64) / self.sample_rate

    def copy_with(
        self,
        *,
        values: FloatArray | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> "BaseTimeSeries":
        """Return a new instance with overridden data or metadata."""

        new_values = np.asarray(values) if values is not None else self.values.copy()
        new_metadata = dict(metadata) if metadata is not None else dict(self.metadata)
        return BaseTimeSeries(
            values=new_values,
            sample_rate=self.sample_rate,
            start_timestamp=self.start_timestamp,
            metadata=new_metadata,
        )


def build_timeseries(sample: Mapping[str, Any]) -> BaseTimeSeries:
    """Helper to construct ``BaseTimeSeries`` from a mapping."""

    return BaseTimeSeries(
        values=np.asarray(sample["values"]),
        sample_rate=float(sample["sample_rate"]),
        start_timestamp=sample["start_timestamp"],
        metadata=sample.get("metadata", {}),
    )
