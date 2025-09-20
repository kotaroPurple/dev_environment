from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pytest

from dev_environment.data import BaseTimeSeries


def test_base_time_series_validates_dimensions() -> None:
    now = datetime.now(tz=timezone.utc)
    with pytest.raises(ValueError):
        BaseTimeSeries(values=np.array(1.0), sample_rate=1.0, start_timestamp=now)


def test_base_time_series_properties(sample_block: BaseTimeSeries) -> None:
    assert sample_block.block_size == 10
    assert pytest.approx(sample_block.duration_seconds) == 0.1
    assert sample_block.start_timestamp.tzinfo == timezone.utc


def test_copy_with_overrides(sample_block: BaseTimeSeries) -> None:
    new_values = sample_block.values * 2
    result = sample_block.copy_with(values=new_values, metadata={"scale": 2})
    assert np.allclose(result.values, new_values)
    assert result.metadata["scale"] == 2
    assert result.sample_rate == sample_block.sample_rate
