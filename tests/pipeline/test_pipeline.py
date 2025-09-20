from __future__ import annotations

from typing import Iterable

import numpy as np
import pytest

from dev_environment.data import BaseTimeSeries
from dev_environment.io import (
    CollatedStreamDataset,
    IterableDataSourceAdapter,
    StreamDataLoader,
)
from dev_environment.monitoring import ErrorPolicy
from dev_environment.pipeline import (
    IdentityNode,
    MovingAverageNode,
    NormaliseAmplitudeNode,
    PipelineBuilder,
    PipelineExecutionError,
)


def make_blocks() -> Iterable[BaseTimeSeries]:
    for idx in range(3):
        values = np.full((8, 1), idx + 1, dtype=np.float64)
        metadata = {"idx": idx}
        yield BaseTimeSeries(values=values, sample_rate=100.0, start_timestamp=0.0, metadata=metadata)


def test_pipeline_executes_nodes_in_order() -> None:
    adapter = IterableDataSourceAdapter(make_blocks())
    dataset = CollatedStreamDataset(adapter)
    loader = StreamDataLoader(dataset)

    builder = PipelineBuilder(input_key="raw", output_keys=["raw_norm", "raw_norm_ma3"])
    builder.add_node(NormaliseAmplitudeNode("raw", output_key="raw_norm"))
    builder.add_node(MovingAverageNode("raw_norm", output_key="raw_norm_ma3", window=3))

    orchestrator = builder.build(loader)
    outputs = list(orchestrator.run())

    assert len(outputs) == 3
    first = outputs[0]
    assert "raw_norm" in first and "raw_norm_ma3" in first
    assert np.isclose(np.max(np.abs(first["raw_norm"].values)), 1.0)


def test_pipeline_continue_on_error() -> None:
    class FailingNode(NormaliseAmplitudeNode):
        def process(self, inputs):
            raise RuntimeError("boom")

    adapter = IterableDataSourceAdapter(make_blocks())
    dataset = CollatedStreamDataset(adapter)
    loader = StreamDataLoader(dataset)
    builder = PipelineBuilder(input_key="raw")
    builder.add_node(FailingNode("raw", output_key="bad"))

    orchestrator = builder.build(loader, on_error=ErrorPolicy.CONTINUE)
    outputs = list(orchestrator.run())

    assert outputs == []


def test_pipeline_stop_on_error() -> None:
    class FailingNode(NormaliseAmplitudeNode):
        def process(self, inputs):
            raise RuntimeError("boom")

    adapter = IterableDataSourceAdapter(make_blocks())
    dataset = CollatedStreamDataset(adapter)
    loader = StreamDataLoader(dataset)
    builder = PipelineBuilder(input_key="raw")
    builder.add_node(FailingNode("raw"))

    orchestrator = builder.build(loader, on_error=ErrorPolicy.STOP)

    with pytest.raises(PipelineExecutionError):
        next(orchestrator.run())


def test_pipeline_identity_node(sample_block: BaseTimeSeries) -> None:
    adapter = IterableDataSourceAdapter([sample_block])
    dataset = CollatedStreamDataset(adapter)
    loader = StreamDataLoader(dataset)
    builder = PipelineBuilder(input_key="raw", output_keys=["alias"])
    builder.add_node(IdentityNode("raw", output_key="alias"))

    orchestrator = builder.build(loader)
    outputs = list(orchestrator.run())
    assert outputs[0]["alias"].metadata == sample_block.metadata
