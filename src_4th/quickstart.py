"""Quickstart for src_4th showing sliding window and smoothing."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

import numpy as np

from .io import AdapterDataset, StreamDataLoader
from .monitoring import ConsoleMonitor
from .nodes import MovingAverageNode, NormalizerNode, SlidingWindowNode
from .pipeline import PipelineBuilder


def sine_source(num_blocks: int = 120, *, block_size: int = 256) -> Iterable[object]:
    now = datetime.now(tz=timezone.utc)
    grid = np.linspace(0.0, 2 * np.pi, block_size, endpoint=False)
    for idx in range(num_blocks):
        phase = idx * np.pi / 16
        values = np.sin(grid + phase)
        yield {
            "values": values[:, None],
            "sample_rate": 256.0,
            "timestamp": now,
            "metadata": {"block_index": idx},
        }


def build_pipeline() -> None:
    dataset = AdapterDataset(lambda: sine_source())
    loader = StreamDataLoader(dataset)

    builder = PipelineBuilder(input_key="raw", output_keys=["raw_norm", "raw_norm_ma5", "raw_fft"])
    builder.add_node(NormalizerNode("raw", "raw_norm"))
    builder.add_node(MovingAverageNode("raw_norm", "raw_norm_ma5", window=5))
    builder.add_node(
        SlidingWindowNode(
            key_in="raw_norm",
            key_out="raw_fft",
            window_seconds=5.0,
            hop_seconds=1.0,
        )
    )

    monitor = ConsoleMonitor(prefix="[quickstart]")
    pipeline = builder.build(loader, monitor=monitor)

    emitted = 0
    for outputs in pipeline.run():
        if "raw_fft" not in outputs:
            continue
        block = outputs["raw_fft"]
        print(
            "FFT window: samples={}, duration={:.2f}s".format(
                block.block_size,
                block.duration_seconds,
            )
        )
        emitted += 1
        if emitted >= 3:
            break


def main() -> None:
    build_pipeline()


if __name__ == "__main__":  # pragma: no cover
    main()
