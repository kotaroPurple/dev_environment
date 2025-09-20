"""Simple monitoring hooks for third-stage prototype."""

from __future__ import annotations

from typing import Dict

from .data import TimeSeriesBlock


class PipelineMonitor:
    """Interface for observing pipeline events."""

    def on_block_start(self, block_index: int) -> None:  # pragma: no cover
        ...

    def on_block_end(
        self,
        block_index: int,
        outputs: Dict[str, TimeSeriesBlock],
    ) -> None:  # pragma: no cover
        ...


class ConsoleMonitor(PipelineMonitor):
    """Print pipeline events to stdout."""

    def __init__(self, prefix: str = "[src_3rd]") -> None:
        self._prefix = prefix

    def on_block_start(self, block_index: int) -> None:
        print(f"{self._prefix} block {block_index} start")

    def on_block_end(self, block_index: int, outputs: Dict[str, TimeSeriesBlock]) -> None:
        keys = ", ".join(outputs.keys())
        print(f"{self._prefix} block {block_index} end outputs=[{keys}]")
