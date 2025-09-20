"""Shared pytest fixtures for sequential pipeline tests."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

import numpy as np
import pytest

from dev_environment.data import BaseTimeSeries


@pytest.fixture
def sample_block() -> BaseTimeSeries:
    now = datetime.now(tz=timezone.utc)
    values = np.arange(10, dtype=np.float64)[:, None]
    return BaseTimeSeries(
        values=values,
        sample_rate=100.0,
        start_timestamp=now,
        metadata={"fixture": True},
    )


@pytest.fixture
def block_sequence() -> Iterable[BaseTimeSeries]:
    now = datetime.now(tz=timezone.utc)
    for idx in range(3):
        values = (np.ones((8, 1)) * idx).astype(np.float64)
        yield BaseTimeSeries(
            values=values,
            sample_rate=50.0,
            start_timestamp=now,
            metadata={"idx": idx},
        )
