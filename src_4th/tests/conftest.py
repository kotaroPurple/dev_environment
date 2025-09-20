from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pytest

from ..data import BaseTimeSeries


@pytest.fixture
def sample_block() -> BaseTimeSeries:
    now = datetime.now(tz=timezone.utc)
    values = np.arange(64, dtype=np.float64)[:, None]
    return BaseTimeSeries(values=values, sample_rate=64.0, timestamp=now)
