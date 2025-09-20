"""Pipeline building and execution for the third-stage prototype."""

from __future__ import annotations

from collections import deque
from typing import Dict, Iterable, Iterator, List, Sequence

from .data import BlockBuffer, TimeSeriesBlock
from .dataloader import DataLoader
from .monitor import PipelineMonitor
from .nodes import ProcessingNode


class PipelineBuilder:
    """Register nodes and build a sequential pipeline with dependency resolution."""

    def __init__(
        self,
        *,
        input_key: str = "input",
        output_keys: Sequence[str] | None = None,
    ) -> None:
        self._input_key = input_key
        self._output_keys = tuple(output_keys) if output_keys else None
        self._nodes: List[ProcessingNode] = []

    def add_node(self, node: ProcessingNode) -> "PipelineBuilder":
        self._nodes.append(node)
        return self

    def build(self, dataloader: DataLoader, monitor: PipelineMonitor | None = None) -> "Pipeline":
        order = resolve_order(self._nodes, available={self._input_key})
        return Pipeline(
            dataloader=dataloader,
            nodes=order,
            input_key=self._input_key,
            output_keys=self._output_keys,
            monitor=monitor,
        )


def resolve_order(
    nodes: Sequence[ProcessingNode],
    *,
    available: Iterable[str],
) -> List[ProcessingNode]:
    available_keys = set(available)
    pending = deque(nodes)
    order: List[ProcessingNode] = []

    while pending:
        progressed = False
        for _ in range(len(pending)):
            node = pending.popleft()
            if set(node.requires()).issubset(available_keys):
                order.append(node)
                available_keys.update(node.produces())
                progressed = True
            else:
                pending.append(node)
        if not progressed:
            missing = sorted(
                {
                    dep
                    for node in pending
                    for dep in node.requires()
                    if dep not in available_keys
                }
            )
            raise ValueError(f"Unresolved dependencies: {missing}")

    return order


class Pipeline:
    """Execute processing nodes for each block."""

    def __init__(
        self,
        *,
        dataloader: DataLoader,
        nodes: Sequence[ProcessingNode],
        input_key: str,
        output_keys: Sequence[str] | None,
        monitor: PipelineMonitor | None,
    ) -> None:
        self._dataloader = dataloader
        self._nodes = list(nodes)
        self._input_key = input_key
        self._output_keys = tuple(output_keys) if output_keys else None
        self._monitor = monitor

    def run(self) -> Iterator[Dict[str, TimeSeriesBlock]]:
        for node in self._nodes:
            node.reset()

        buffer = BlockBuffer()
        for index, block in enumerate(self._dataloader):
            if self._monitor:
                self._monitor.on_block_start(index)
            buffer.clear()
            buffer.set(self._input_key, block)
            produced: Dict[str, TimeSeriesBlock] = {self._input_key: block}

            for node in self._nodes:
                inputs = {key: buffer.get(key) for key in node.requires()}
                outputs = node.process(inputs)
                for key, value in outputs.items():
                    buffer.set(key, value)
                    produced[key] = value

            if self._monitor:
                self._monitor.on_block_end(index, produced)

            if self._output_keys is None:
                yield dict(produced)
            else:
                yield {key: produced[key] for key in self._output_keys if key in produced}
