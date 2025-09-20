"""Run the third-stage prototype pipeline."""

from __future__ import annotations

import numpy as np

from .dataloader import DataLoader
from .loader import sine_dataset
from .monitor import ConsoleMonitor
from .nodes import IdentityNode, MovingAverageNode, NormalizerNode, SplitNode
from .pipeline import PipelineBuilder


def run() -> None:
    dataset = sine_dataset(num_blocks=3, block_size=64)
    loader = DataLoader(dataset)

    builder = PipelineBuilder(input_key="raw", output_keys=["raw_norm", "raw_norm_ma5"])
    builder.add_node(SplitNode("raw", outputs=["raw_a", "raw_b"]))
    builder.add_node(NormalizerNode("raw_a", key_out="raw_norm"))
    builder.add_node(MovingAverageNode("raw_norm", key_out="raw_norm_ma5", window=5))
    builder.add_node(IdentityNode("raw_b", alias="raw"))

    monitor = ConsoleMonitor()
    pipeline = builder.build(loader, monitor=monitor)

    for index, outputs in enumerate(pipeline.run()):
        norm_peak = float(np.max(np.abs(outputs["raw_norm"].values)))
        print(f"block {index}: norm_peak={norm_peak:.3f}, keys={list(outputs.keys())}")


if __name__ == "__main__":
    run()
