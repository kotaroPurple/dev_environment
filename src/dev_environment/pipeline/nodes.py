"""Reference processing nodes for sequential pipelines."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Iterable

import numpy as np

from dev_environment.data import BaseTimeSeries

from .base import ProcessingNode


class IdentityNode(ProcessingNode):
    """Pass-through node that optionally renames the incoming block."""

    def __init__(
        self,
        input_key: str,
        output_key: str | None = None,
        *,
        name: str | None = None,
    ) -> None:
        super().__init__(name)
        self._input_key = input_key
        self._output_key = output_key or input_key

    def requires(self) -> Iterable[str]:
        return [self._input_key]

    def produces(self) -> Iterable[str]:
        return [self._output_key]

    def process(self, inputs: Mapping[str, BaseTimeSeries]) -> Mapping[str, BaseTimeSeries]:
        return {self._output_key: inputs[self._input_key]}


class NormaliseAmplitudeNode(ProcessingNode):
    """Scale a block to the range [-1, 1] by peak amplitude."""

    def __init__(
        self,
        input_key: str,
        output_key: str | None = None,
        *,
        eps: float = 1e-12,
    ) -> None:
        super().__init__()
        self._input_key = input_key
        self._output_key = output_key or f"{input_key}_norm"
        self._eps = eps

    def requires(self) -> Iterable[str]:
        return [self._input_key]

    def produces(self) -> Iterable[str]:
        return [self._output_key]

    def process(self, inputs: Mapping[str, BaseTimeSeries]) -> Mapping[str, BaseTimeSeries]:
        source = inputs[self._input_key]
        values = source.values
        peak = np.max(np.abs(values))
        scale = 1.0 if peak < self._eps else 1.0 / peak
        metadata = {**source.metadata, "scale": scale}
        normalised = source.copy_with(values=values * scale, metadata=metadata)
        return {self._output_key: normalised}


class MovingAverageNode(ProcessingNode):
    """Apply a simple moving average across the first axis."""

    def __init__(
        self,
        input_key: str,
        output_key: str | None = None,
        *,
        window: int = 5,
    ) -> None:
        if window <= 0:
            raise ValueError("window must be positive")
        super().__init__()
        self._input_key = input_key
        self._output_key = output_key or f"{input_key}_ma{window}"
        self._window = window

    def requires(self) -> Iterable[str]:
        return [self._input_key]

    def produces(self) -> Iterable[str]:
        return [self._output_key]

    def process(self, inputs: Mapping[str, BaseTimeSeries]) -> Mapping[str, BaseTimeSeries]:
        source = inputs[self._input_key]
        values = source.values
        if values.shape[0] < self._window:
            averaged = values
        else:
            kernel = np.ones(self._window) / self._window
            averaged = np.apply_along_axis(
                lambda m: np.convolve(m, kernel, mode="valid"),
                0,
                values,
            )
            pad = values.shape[0] - averaged.shape[0]
            if pad > 0:
                front = np.repeat(averaged[0:1], pad, axis=0)
                averaged = np.vstack([front, averaged])
        result = source.copy_with(values=averaged)
        return {self._output_key: result}
