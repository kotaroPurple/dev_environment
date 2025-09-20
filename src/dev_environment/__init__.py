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
    "main",
]


def main() -> None:
    """Entry point placeholder to keep package executable via ``uv run``."""

    print("dev_environment library")
