"""Monitoring hooks and error policies for pipeline execution."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Protocol, runtime_checkable


class ErrorPolicy(str, Enum):
    """Controls how the orchestrator reacts to processing errors."""

    STOP = "stop"
    CONTINUE = "continue"


@dataclass(slots=True, frozen=True)
class BlockSummary:
    """Basic telemetry returned when a block completes."""

    block_index: int
    duration_seconds: float
    outputs: Mapping[str, object] | None


@runtime_checkable
class PipelineMonitor(Protocol):
    """Interface for observing pipeline execution events."""

    def on_block_start(self, block_index: int) -> None:  # pragma: no cover - runtime hook
        ...

    def on_block_end(self, summary: BlockSummary) -> None:  # pragma: no cover - runtime hook
        ...

    def on_node_start(
        self,
        block_index: int,
        node_name: str,
    ) -> None:  # pragma: no cover - runtime hook
        ...

    def on_node_end(
        self,
        block_index: int,
        node_name: str,
        duration_seconds: float,
    ) -> None:  # pragma: no cover
        ...

    def on_error(
        self,
        block_index: int,
        node_name: str | None,
        error: Exception,
    ) -> None:  # pragma: no cover
        ...


class ConsoleMonitor(PipelineMonitor):
    """Simple monitor that prints execution events to stdout."""

    def __init__(self, *, prefix: str = "[pipeline]") -> None:
        self._prefix = prefix

    def on_block_start(self, block_index: int) -> None:
        print(f"{self._prefix} block {block_index} start")

    def on_block_end(self, summary: BlockSummary) -> None:
        duration = summary.duration_seconds
        print(f"{self._prefix} block {summary.block_index} end duration={duration:.4f}s")

    def on_node_start(self, block_index: int, node_name: str) -> None:
        print(f"{self._prefix} block {block_index} node {node_name} start")

    def on_node_end(self, block_index: int, node_name: str, duration_seconds: float) -> None:
        print(
            f"{self._prefix} block {block_index} node {node_name} end "
            f"duration={duration_seconds:.4f}s"
        )

    def on_error(self, block_index: int, node_name: str | None, error: Exception) -> None:
        location = node_name or "dataloader"
        print(f"{self._prefix} block {block_index} error in {location}: {error!r}")
