"""Run the second-stage pipeline example."""

from __future__ import annotations

import numpy as np

from .loader import SimpleDataLoader, generate_sine_blocks
from .nodes import MovingAverageNode, NormalizerNode
from .pipeline import SequentialPipeline


def run() -> None:
    blocks = list(generate_sine_blocks())
    loader = SimpleDataLoader(blocks)

    pipeline = SequentialPipeline(
        nodes=[
            NormalizerNode(),
            MovingAverageNode(window=5),
        ]
    )

    for index, block in enumerate(pipeline.run(loader)):
        peak = np.max(np.abs(block.values))
        message = (
            "block {index}: samples={samples}, duration={duration:.4f}s, peak={peak:.3f}".format(
                index=index,
                samples=block.block_size,
                duration=block.duration_seconds,
                peak=peak,
            )
        )
        print(message)


if __name__ == "__main__":  # pragma: no cover - manual execution helper
    run()
