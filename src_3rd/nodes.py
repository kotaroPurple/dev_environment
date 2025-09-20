"""Processing nodes with multi-key support for third-stage prototype."""

from __future__ import annotations

from typing import Dict, Iterable, List

import numpy as np

from .data import TimeSeriesBlock


class ProcessingNode:
    """Base class for processing nodes with declared dependencies."""

    def __init__(self, name: str | None = None) -> None:
        self.name = name or self.__class__.__name__

    def requires(self) -> Iterable[str]:
        return []

    def produces(self) -> Iterable[str]:
        return []

    def process(self, inputs: Dict[str, TimeSeriesBlock]) -> Dict[str, TimeSeriesBlock]:
        raise NotImplementedError


class IdentityNode(ProcessingNode):
    def __init__(self, key: str, alias: str | None = None) -> None:
        super().__init__()
        self._key = key
        self._alias = alias or key

    def requires(self) -> Iterable[str]:
        return [self._key]

    def produces(self) -> Iterable[str]:
        return [self._alias]

    def process(self, inputs: Dict[str, TimeSeriesBlock]) -> Dict[str, TimeSeriesBlock]:
        return {self._alias: inputs[self._key]}


class NormalizerNode(ProcessingNode):
    def __init__(self, key_in: str, key_out: str | None = None, *, eps: float = 1e-9) -> None:
        super().__init__()
        self._key_in = key_in
        self._key_out = key_out or f"{key_in}_norm"
        self._eps = eps

    def requires(self) -> Iterable[str]:
        return [self._key_in]

    def produces(self) -> Iterable[str]:
        return [self._key_out]

    def process(self, inputs: Dict[str, TimeSeriesBlock]) -> Dict[str, TimeSeriesBlock]:
        block = inputs[self._key_in]
        peak = np.max(np.abs(block.values))
        if peak < self._eps:
            return {self._key_out: block}
        scaled = block.values / peak
        metadata = {**block.metadata, "scale": float(1.0 / peak)}
        return {self._key_out: block.copy_with(values=scaled, metadata=metadata)}


class MovingAverageNode(ProcessingNode):
    def __init__(self, key_in: str, key_out: str | None = None, *, window: int = 5) -> None:
        if window <= 0:
            raise ValueError("window must be positive")
        super().__init__()
        self._key_in = key_in
        self._key_out = key_out or f"{key_in}_ma{window}"
        self._window = window
        self._kernel = np.ones(window, dtype=np.float64) / window

    def requires(self) -> Iterable[str]:
        return [self._key_in]

    def produces(self) -> Iterable[str]:
        return [self._key_out]

    def process(self, inputs: Dict[str, TimeSeriesBlock]) -> Dict[str, TimeSeriesBlock]:
        block = inputs[self._key_in]
        if block.values.size < self._window:
            return {self._key_out: block}
        convolved = np.convolve(block.values, self._kernel, mode="valid")
        pad = block.values.size - convolved.size
        if pad > 0:
            prefix = np.full(pad, convolved[0], dtype=np.float64)
            smoothed = np.concatenate([prefix, convolved])
        else:
            smoothed = convolved
        return {self._key_out: block.copy_with(values=smoothed)}


class SplitNode(ProcessingNode):
    """Duplicate an input block under multiple keys."""

    def __init__(self, key_in: str, outputs: Iterable[str]) -> None:
        super().__init__()
        self._key_in = key_in
        self._outputs: List[str] = list(outputs)

    def requires(self) -> Iterable[str]:
        return [self._key_in]

    def produces(self) -> Iterable[str]:
        return list(self._outputs)

    def process(self, inputs: Dict[str, TimeSeriesBlock]) -> Dict[str, TimeSeriesBlock]:
        block = inputs[self._key_in]
        return {key: block for key in self._outputs}
