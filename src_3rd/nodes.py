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

    def reset(self) -> None:
        """Hook for stateful nodes to reset between pipeline runs."""

        return


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


class SlidingWindowNode(ProcessingNode):
    """Accumulate samples until a window is full, then emit it with a hop."""

    def __init__(
        self,
        key_in: str,
        key_out: str,
        *,
        window_seconds: float,
        hop_seconds: float,
    ) -> None:
        super().__init__()
        if window_seconds <= 0 or hop_seconds <= 0:
            raise ValueError("window_seconds and hop_seconds must be positive")
        self._key_in = key_in
        self._key_out = key_out
        self._window_seconds = window_seconds
        self._hop_seconds = hop_seconds
        self._buffer: List[float] = []
        self._sample_rate: float | None = None
        self._window_samples: int | None = None
        self._hop_samples: int | None = None

    def requires(self) -> Iterable[str]:
        return [self._key_in]

    def produces(self) -> Iterable[str]:
        return [self._key_out]

    def reset(self) -> None:
        self._buffer.clear()
        self._sample_rate = None
        self._window_samples = None
        self._hop_samples = None

    def process(self, inputs: Dict[str, TimeSeriesBlock]) -> Dict[str, TimeSeriesBlock]:
        block = inputs[self._key_in]
        if self._sample_rate is None:
            self._sample_rate = block.sample_rate
            self._window_samples = max(
                int(round(self._window_seconds * self._sample_rate)),
                1,
            )
            self._hop_samples = max(
                int(round(self._hop_seconds * self._sample_rate)),
                1,
            )
        elif not np.isclose(self._sample_rate, block.sample_rate):
            raise ValueError("Sample rate changed during sliding window accumulation")

        self._buffer.extend(block.values.tolist())

        if self._window_samples is None or len(self._buffer) < self._window_samples:
            return {}

        window_vals = np.array(self._buffer[: self._window_samples], dtype=np.float64)
        metadata = {**block.metadata, "window_seconds": self._window_seconds}
        window_block = block.copy_with(values=window_vals, metadata=metadata)

        # advance by hop
        del self._buffer[: self._hop_samples]

        return {self._key_out: window_block}


class ChunkingRMSNode(ProcessingNode):
    """Split incoming samples into fixed-length chunks and compute RMS per chunk."""

    def __init__(
        self,
        key_in: str,
        key_out: str,
        *,
        chunk_seconds: float = 1.0,
    ) -> None:
        if chunk_seconds <= 0:
            raise ValueError("chunk_seconds must be positive")
        super().__init__()
        self._key_in = key_in
        self._key_out = key_out
        self._chunk_seconds = chunk_seconds
        self._buffer: List[float] = []
        self._sample_rate: float | None = None
        self._chunk_samples: int | None = None

    def requires(self) -> Iterable[str]:
        return [self._key_in]

    def produces(self) -> Iterable[str]:
        return [self._key_out]

    def reset(self) -> None:
        self._buffer.clear()
        self._sample_rate = None
        self._chunk_samples = None

    def process(self, inputs: Dict[str, TimeSeriesBlock]) -> Dict[str, TimeSeriesBlock]:
        block = inputs[self._key_in]
        if self._sample_rate is None:
            self._sample_rate = block.sample_rate
            self._chunk_samples = max(
                int(round(self._chunk_seconds * self._sample_rate)),
                1,
            )
        elif not np.isclose(self._sample_rate, block.sample_rate):
            raise ValueError("Sample rate changed during chunking")

        self._buffer.extend(block.values.tolist())

        if self._chunk_samples is None:
            return {}

        rms_values: List[float] = []
        while len(self._buffer) >= self._chunk_samples:
            chunk = np.array(self._buffer[: self._chunk_samples], dtype=np.float64)
            rms = float(np.sqrt(np.mean(np.square(chunk))))
            rms_values.append(rms)
            del self._buffer[: self._chunk_samples]

        if not rms_values:
            return {}

        values = np.array(rms_values, dtype=np.float64)
        metadata = {
            **block.metadata,
            "chunk_seconds": self._chunk_seconds,
            "chunks": len(rms_values),
        }
        rms_block = TimeSeriesBlock(
            values=values,
            sample_rate=1.0 / self._chunk_seconds,
            timestamp=block.timestamp,
            metadata=metadata,
        )

        return {self._key_out: rms_block}
