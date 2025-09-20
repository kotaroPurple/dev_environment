"""Fourth-stage pipeline prototype approaching production architecture."""

from .data import BaseTimeSeries, BlockBuffer
from .io import (
    AdapterDataset,
    CollateFn,
    IterableDataset,
    StreamDataLoader,
)
from .monitoring import ConsoleMonitor, ErrorPolicy, PipelineMonitor
from .nodes import MovingAverageNode, NormalizerNode, SlidingWindowNode
from .pipeline import PipelineBuilder, PipelineExecutionError, PipelineOrchestrator

__all__ = [
    "BaseTimeSeries",
    "BlockBuffer",
    "AdapterDataset",
    "CollateFn",
    "IterableDataset",
    "StreamDataLoader",
    "ConsoleMonitor",
    "ErrorPolicy",
    "PipelineMonitor",
    "MovingAverageNode",
    "NormalizerNode",
    "SlidingWindowNode",
    "PipelineBuilder",
    "PipelineExecutionError",
    "PipelineOrchestrator",
]
