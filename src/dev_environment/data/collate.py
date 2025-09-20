"""Utility helpers to translate raw dataset samples into ``BaseTimeSeries`` blocks."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .models import BaseTimeSeries, build_timeseries


def collate_block(sample: Any) -> BaseTimeSeries:
    """Normalize dataset output into a ``BaseTimeSeries`` instance."""

    if isinstance(sample, BaseTimeSeries):
        return sample

    if isinstance(sample, Mapping):
        return build_timeseries(dict(sample))

    if isinstance(sample, Sequence) and not isinstance(sample, (str, bytes, bytearray)):
        if len(sample) not in (3, 4):
            message = (
                "Sequence sample must be (values, sample_rate, start_timestamp[, metadata])"
            )
            raise ValueError(message)

        values, sample_rate, start_timestamp, *rest = sample
        metadata = rest[0] if rest else {}
        mapping = {
            "values": values,
            "sample_rate": sample_rate,
            "start_timestamp": start_timestamp,
            "metadata": metadata,
        }
        return build_timeseries(mapping)

    has_attrs = all(
        hasattr(sample, attr) for attr in ("values", "sample_rate", "start_timestamp")
    )
    if has_attrs:
        metadata = getattr(sample, "metadata", {})
        mapping = {
            "values": getattr(sample, "values"),
            "sample_rate": getattr(sample, "sample_rate"),
            "start_timestamp": getattr(sample, "start_timestamp"),
            "metadata": metadata,
        }
        return build_timeseries(mapping)

    raise TypeError("Unsupported sample type for collate_block")
