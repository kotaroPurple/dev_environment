"""Fourth-stage pipeline prototype approaching production architecture."""

from .data import BaseTimeSeries, BlockBuffer
from .io import (
    AdapterDataset,
    CollateFn,
    IterableDataset,
    StreamDataLoader,
)
from .monitoring import ConsoleMonitor, ErrorPolicy, PipelineMonitor
from .nodes import (
    DecisionNode,
    MovingAverageNode,
    NormalizerNode,
    SlidingWindowNode,
    SplitSensorNode,
)
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
    "DecisionNode",
    "MovingAverageNode",
    "NormalizerNode",
    "SlidingWindowNode",
    "SplitSensorNode",
    "PipelineBuilder",
    "PipelineExecutionError",
    "PipelineOrchestrator",
]
