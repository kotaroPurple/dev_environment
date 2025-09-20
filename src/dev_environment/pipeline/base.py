"""Core pipeline orchestration primitives."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from typing import Dict, Sequence

from dev_environment.data import BaseTimeSeries, BlockBuffer
from dev_environment.io import StreamDataLoader


class ProcessingNode:
    """Base class for pipeline processing nodes."""

    def __init__(self, name: str | None = None) -> None:
        self.name = name or self.__class__.__name__

    def requires(self) -> Sequence[str]:
        """Names of data blocks required prior to execution."""

        return []

    def produces(self) -> Sequence[str]:
        """Names of data blocks produced by this node."""

        return []

    def reset(self) -> None:
        """Reset any internal state before a new run."""

    def process(self, inputs: Mapping[str, BaseTimeSeries]) -> Mapping[str, BaseTimeSeries]:
        """Perform processing and return outputs keyed by produced names."""

        raise NotImplementedError


@dataclass(frozen=True)
class PipelineSpec:
    input_key: str
    nodes: Sequence[ProcessingNode]
    output_keys: Sequence[str] | None


class PipelineBuilder:
    """Registers processing nodes and resolves an execution plan."""

    def __init__(
        self,
        *,
        input_key: str = "input",
        output_keys: Sequence[str] | None = None,
    ) -> None:
        self._input_key = input_key
        self._output_keys = tuple(output_keys) if output_keys is not None else None
        self._nodes: list[ProcessingNode] = []

    def add_node(self, node: ProcessingNode) -> "PipelineBuilder":
        self._nodes.append(node)
        return self

    def _resolve_order(self) -> list[ProcessingNode]:
        available = {self._input_key}
        pending = list(self._nodes)
        order: list[ProcessingNode] = []

        while pending:
            progressed = False
            for node in list(pending):
                if set(node.requires()).issubset(available):
                    order.append(node)
                    available.update(node.produces())
                    pending.remove(node)
                    progressed = True
            if not progressed:
                missing = {
                    dep
                    for node in pending
                    for dep in node.requires()
                    if dep not in available
                }
                raise ValueError(f"Unresolved dependencies: {sorted(missing)}")

        return order

    def build(self, dataloader: StreamDataLoader) -> "PipelineOrchestrator":
        order = self._resolve_order()
        spec = PipelineSpec(input_key=self._input_key, nodes=order, output_keys=self._output_keys)
        return PipelineOrchestrator(dataloader=dataloader, spec=spec)


class PipelineOrchestrator:
    """Coordinates the sequential execution of processing nodes per block."""

    def __init__(self, *, dataloader: StreamDataLoader, spec: PipelineSpec) -> None:
        self._dataloader = dataloader
        self._spec = spec
        self._buffer: BlockBuffer[BaseTimeSeries] | None = None

    def reset(self) -> None:
        self._dataloader.reset()
        for node in self._spec.nodes:
            node.reset()
        self._buffer = None

    def process_next(self) -> Mapping[str, BaseTimeSeries] | None:
        raw_block = self._dataloader.next_block()
        if raw_block is None:
            return None

        self._buffer = BlockBuffer()
        self._buffer.push(self._spec.input_key, raw_block)
        produced: Dict[str, BaseTimeSeries] = {self._spec.input_key: raw_block}

        for node in self._spec.nodes:
            required = {key: self._buffer.get(key) for key in node.requires()}
            outputs = node.process(required)
            for key, value in outputs.items():
                if key not in node.produces():
                    raise ValueError(f"Node {node.name} produced unexpected key '{key}'")
                self._buffer.push(key, value)
                produced[key] = value

        if self._spec.output_keys is None:
            return produced

        return {key: produced[key] for key in self._spec.output_keys if key in produced}

    def run(self, *, max_blocks: int | None = None) -> Iterator[Mapping[str, BaseTimeSeries]]:
        count = 0
        while True:
            if max_blocks is not None and count >= max_blocks:
                return
            result = self.process_next()
            if result is None:
                return
            count += 1
            yield result

    def available_outputs(self) -> Iterable[str]:
        produced = {self._spec.input_key}
        for node in self._spec.nodes:
            produced.update(node.produces())
        return produced
