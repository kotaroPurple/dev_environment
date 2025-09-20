"""Sequential pipeline for the second-stage prototype."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import List

from .data import TimeSeriesBlock
from .nodes import BaseNode


class SequentialPipeline:
    """Apply nodes sequentially to each incoming block."""

    def __init__(self, nodes: Iterable[BaseNode]):
        self._nodes: List[BaseNode] = list(nodes)

    def process_block(self, block: TimeSeriesBlock) -> TimeSeriesBlock:
        current = block
        for node in self._nodes:
            current = node.process(current)
        return current

    def run(self, blocks: Iterable[TimeSeriesBlock]) -> Iterator[TimeSeriesBlock]:
        for block in blocks:
            yield self.process_block(block)
