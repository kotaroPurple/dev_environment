from __future__ import annotations

import numpy as np
import pytest

from ..data import BaseTimeSeries


def test_base_time_series_enforces_shape(sample_block: BaseTimeSeries) -> None:
    assert sample_block.block_size == 64
    assert pytest.approx(sample_block.duration_seconds) == 1.0


def test_copy_with(sample_block: BaseTimeSeries) -> None:
    scaled = sample_block.copy_with(values=sample_block.values * 2)
    assert np.allclose(scaled.values, sample_block.values * 2)
    assert scaled.metadata == sample_block.metadata
