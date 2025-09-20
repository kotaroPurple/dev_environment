"""Public package exports for dev_environment."""

from .data import BaseTimeSeries, BlockBuffer, build_timeseries, collate_block

__all__ = [
    "BaseTimeSeries",
    "BlockBuffer",
    "build_timeseries",
    "collate_block",
    "main",
]


def main() -> None:
    """Entry point placeholder to keep package executable via ``uv run``."""

    print("dev_environment library")
