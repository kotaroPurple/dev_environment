from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pytest

from ..data import BaseTimeSeries
from ..io import IterableDataset, MultiSensorDataset, StreamDataLoader
from ..monitoring import ErrorPolicy
from ..nodes import (
    DecisionNode,
    MovingAverageNode,
    NormalizerNode,
    SlidingWindowNode,
    SplitSensorNode,
)
from ..pipeline import PipelineBuilder, PipelineExecutionError


def make_blocks(count: int = 5) -> list[BaseTimeSeries]:
    blocks = []
    for idx in range(count):
        values = np.sin(np.linspace(0, 2 * np.pi, 64) + idx)[:, None]
        blocks.append(
            BaseTimeSeries(
                values=values,
                sample_rate=64.0,
                timestamp=datetime.now(tz=timezone.utc),
                metadata={"idx": idx},
            )
        )
    return blocks


def test_pipeline_normal_flow() -> None:
    dataset = IterableDataset(make_blocks(10))
    loader = StreamDataLoader(dataset)
    builder = PipelineBuilder(input_key="raw", output_keys=["raw_norm", "raw_norm_ma5"])
    builder.add_node(NormalizerNode("raw", "raw_norm"))
    builder.add_node(MovingAverageNode("raw_norm", "raw_norm_ma5", window=5))

    pipeline = builder.build(loader)
    outputs = list(pipeline.run())
    assert len(outputs) == 10
    assert all("raw_norm" in block for block in outputs)


def test_pipeline_stop_on_error() -> None:
    class FailingNode(NormalizerNode):
        def process(self, inputs):
            raise RuntimeError("boom")

    dataset = IterableDataset(make_blocks(2))
    loader = StreamDataLoader(dataset)
    builder = PipelineBuilder(input_key="raw")
    builder.add_node(FailingNode("raw"))
    pipeline = builder.build(loader, on_error=ErrorPolicy.STOP)

    with pytest.raises(PipelineExecutionError):
        next(pipeline.run())


def test_sliding_window_emits_after_fill(sample_block: BaseTimeSeries) -> None:
    blocks = [sample_block] * 3
    dataset = IterableDataset(blocks)
    loader = StreamDataLoader(dataset)
    builder = PipelineBuilder(input_key="raw", output_keys=["fft"])
    builder.add_node(
        SlidingWindowNode(
            "raw",
            "fft",
            window_seconds=sample_block.duration_seconds * 2,
            hop_seconds=sample_block.duration_seconds,
        )
    )
    pipeline = builder.build(loader)
    outputs = list(pipeline.run())
    # Expect last block to emit window, earlier ones empty
    assert len(outputs) == 3
    assert "fft" in outputs[-1]


def test_multisensor_decision() -> None:
    now = datetime.now(tz=timezone.utc)
    sensors = {
        "sensor_a": [
            BaseTimeSeries(values=np.full((10, 1), 1.0), sample_rate=10.0, timestamp=now),
            BaseTimeSeries(values=np.full((10, 1), 2.0), sample_rate=10.0, timestamp=now),
        ],
        "sensor_b": [
            BaseTimeSeries(values=np.full((10, 1), 3.0), sample_rate=10.0, timestamp=now),
            BaseTimeSeries(values=np.full((10, 1), 4.0), sample_rate=10.0, timestamp=now),
        ],
    }
    dataset = MultiSensorDataset(sensors)
    loader = StreamDataLoader(dataset)
    builder = PipelineBuilder(input_key="multi", output_keys=["decision"])
    builder.add_node(SplitSensorNode("multi", ["sensor_a", "sensor_b"]))
    builder.add_node(NormalizerNode("sensor_a_raw", "sensor_a_norm"))
    builder.add_node(NormalizerNode("sensor_b_raw", "sensor_b_norm"))
    builder.add_node(
        DecisionNode(
            required_keys=["sensor_a_norm", "sensor_b_norm"],
            output_key="decision",
        )
    )
    pipeline = builder.build(loader)
    outputs = list(pipeline.run())
    assert len(outputs) == 2
    assert "decision" in outputs[-1]
