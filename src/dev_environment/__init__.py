"""Public package exports for dev_environment."""

from .data import BaseTimeSeries, BlockBuffer, build_timeseries, collate_block
from .io import (
    AdapterStreamDataset,
    BufferedStreamDataset,
    CollatedStreamDataset,
    DataSourceAdapter,
    IterableDataSourceAdapter,
    IteratorStreamDataset,
    SequenceDataSourceAdapter,
    StreamDataLoader,
    StreamDataset,
)
from .monitoring import ConsoleMonitor, ErrorPolicy, PipelineMonitor
from .pipeline import (
    IdentityNode,
    MovingAverageNode,
    NormaliseAmplitudeNode,
    PipelineBuilder,
    PipelineOrchestrator,
    ProcessingNode,
)

__all__ = [
    "BaseTimeSeries",
    "BlockBuffer",
    "build_timeseries",
    "collate_block",
    "AdapterStreamDataset",
    "BufferedStreamDataset",
    "CollatedStreamDataset",
    "DataSourceAdapter",
    "IterableDataSourceAdapter",
    "IteratorStreamDataset",
    "SequenceDataSourceAdapter",
    "StreamDataLoader",
    "StreamDataset",
    "ConsoleMonitor",
    "ErrorPolicy",
    "PipelineMonitor",
    "IdentityNode",
    "MovingAverageNode",
    "NormaliseAmplitudeNode",
    "PipelineBuilder",
    "PipelineOrchestrator",
    "ProcessingNode",
    "main",
]


def main() -> None:
    """Entry point placeholder to keep package executable via ``uv run``."""

    print("dev_environment library")
