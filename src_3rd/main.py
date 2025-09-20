"""Run the third-stage prototype pipeline."""

from __future__ import annotations

import numpy as np

from .dataloader import DataLoader
from .loader import bulk_dataset, sine_dataset
from .monitor import ConsoleMonitor
from .nodes import (
    ChunkingRMSNode,
    NormalizerNode,
    SlidingWindowNode,
    SplitNode,
)
from .pipeline import PipelineBuilder


def run() -> None:
    demo_sliding_window()
    print("---")
    demo_chunking()


def demo_sliding_window() -> None:
    dataset = sine_dataset(num_blocks=120, block_size=64, sample_rate=64.0)
    loader = DataLoader(dataset)

    builder = PipelineBuilder(input_key="raw", output_keys=["raw_norm", "fft_window"])
    builder.add_node(SplitNode("raw", outputs=["raw_direct", "raw_buffer"]))
    builder.add_node(NormalizerNode("raw_direct", key_out="raw_norm"))
    builder.add_node(
        SlidingWindowNode(
            "raw_buffer",
            "fft_window",
            window_seconds=60.0,
            hop_seconds=2.0,
        )
    )

    monitor = ConsoleMonitor(prefix="[window]")
    pipeline = builder.build(loader, monitor=monitor)

    emitted = 0
    for outputs in pipeline.run():
        if "fft_window" not in outputs:
            continue
        window_block = outputs["fft_window"]
        peak = float(np.max(np.abs(window_block.values)))
        print(
            "sliding window: samples={}, duration={:.1f}s, peak={:.3f}".format(
                window_block.block_size,
                window_block.duration_seconds,
                peak,
            )
        )
        emitted += 1
        if emitted >= 3:
            break


def demo_chunking() -> None:
    dataset = bulk_dataset(duration_seconds=120, sample_rate=64.0)
    loader = DataLoader(dataset)

    builder = PipelineBuilder(input_key="bulk", output_keys=["bulk_rms"])
    builder.add_node(ChunkingRMSNode("bulk", "bulk_rms", chunk_seconds=1.0))

    monitor = ConsoleMonitor(prefix="[chunk]")
    pipeline = builder.build(loader, monitor=monitor)

    for outputs in pipeline.run():
        rms_block = outputs["bulk_rms"]
        print(
            "chunk RMS: count={}, first={:.3f}, last={:.3f}".format(
                rms_block.block_size,
                rms_block.values[0],
                rms_block.values[-1],
            )
        )


if __name__ == "__main__":
    run()
