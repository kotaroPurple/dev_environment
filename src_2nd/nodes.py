"""Processing nodes for the second-stage prototype."""

from __future__ import annotations

import numpy as np

from .data import TimeSeriesBlock


class BaseNode:
    """Minimal processing node interface."""

    def __init__(self, name: str | None = None) -> None:
        self.name = name or self.__class__.__name__

    def process(self, block: TimeSeriesBlock) -> TimeSeriesBlock:
        raise NotImplementedError


class NormalizerNode(BaseNode):
    """Scale block values into [-1, 1] range."""

    def __init__(self, *, eps: float = 1e-9) -> None:
        super().__init__()
        self._eps = eps

    def process(self, block: TimeSeriesBlock) -> TimeSeriesBlock:
        peak = np.max(np.abs(block.values))
        if peak < self._eps:
            return block
        scaled = block.values / peak
        metadata = {**block.metadata, "scale": float(1.0 / peak)}
        return block.copy_with(values=scaled, metadata=metadata)


class MovingAverageNode(BaseNode):
    """Apply a simple moving average filter."""

    def __init__(self, window: int = 5) -> None:
        if window <= 0:
            raise ValueError("window must be positive")
        super().__init__()
        self._window = window
        self._kernel = np.ones(window, dtype=np.float64) / window

    def process(self, block: TimeSeriesBlock) -> TimeSeriesBlock:
        if block.values.size < self._window:
            return block

        convolved = np.convolve(block.values, self._kernel, mode="valid")
        pad = block.values.size - convolved.size
        if pad > 0:
            prefix = np.full(pad, convolved[0], dtype=np.float64)
            smoothed = np.concatenate([prefix, convolved])
        else:
            smoothed = convolved
        return block.copy_with(values=smoothed)
