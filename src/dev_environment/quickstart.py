"""Executable example demonstrating the sequential pipeline."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

import numpy as np

from dev_environment.io import (
    CollatedStreamDataset,
    IterableDataSourceAdapter,
    StreamDataLoader,
)
from dev_environment.monitoring import ConsoleMonitor
from dev_environment.pipeline import (
    MovingAverageNode,
    NormaliseAmplitudeNode,
    PipelineBuilder,
    PipelineOrchestrator,
)


def generate_mock_samples(num_blocks: int = 3, block_size: int = 32) -> Iterable[dict[str, object]]:
    now = datetime.now(tz=timezone.utc)
    for idx in range(num_blocks):
        values = np.sin(np.linspace(0, np.pi * 2, block_size) + idx)
        yield {
            "values": values[:, None],
            "sample_rate": 128.0,
            "start_timestamp": now,
            "metadata": {"block_index": idx},
        }


def build_pipeline() -> PipelineOrchestrator:
    samples = generate_mock_samples()
    adapter = IterableDataSourceAdapter(samples)
    dataset = CollatedStreamDataset(adapter)
    loader = StreamDataLoader(dataset)

    builder = PipelineBuilder(input_key="raw", output_keys=["raw", "raw_norm", "raw_norm_ma5"])
    builder.add_node(NormaliseAmplitudeNode(input_key="raw", output_key="raw_norm"))
    builder.add_node(MovingAverageNode(input_key="raw_norm", output_key="raw_norm_ma5", window=5))

    monitor = ConsoleMonitor(prefix="[quickstart]")
    return builder.build(loader, monitor=monitor)


def main() -> None:
    orchestrator = build_pipeline()
    for block_index, outputs in enumerate(orchestrator.run()):
        print(f"Block {block_index}")
        for key, series in outputs.items():
            print(f"  {key}: shape={series.values.shape}, scale={series.metadata.get('scale')}" )


if __name__ == "__main__":
    main()
