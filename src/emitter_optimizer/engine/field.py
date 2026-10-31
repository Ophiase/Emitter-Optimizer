from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np

from emitter_optimizer.engine.geometry import visibility
from emitter_optimizer.engine.laws import FloatArray, Law, Positions

CELLS_PER_CHUNK = 4096
MINIMUM_DISTANCE = 1e-12


@dataclass(frozen=True)
class Signal:
    offsets: FloatArray
    distances: FloatArray
    visible: FloatArray
    received: FloatArray


@dataclass(eq=False)
class Field:
    grid: FloatArray
    map_scale: tuple[float, float]
    grid_size: tuple[int, int]
    density: FloatArray | None
    obstacles: FloatArray | None
    emitter_law: Law
    sensor_law: Law

    @property
    def cells(self) -> FloatArray:
        return self.grid.reshape(-1, 2)

    @property
    def measure(self) -> FloatArray:
        if self.density is None:
            return np.ones(len(self.cells))
        return self.density

    def value_map(self, emitters: Positions) -> FloatArray:
        values = np.empty(len(self.cells))
        for start, cells, _measure in self._chunks():
            values[start : start + len(cells)] = self.sensor_law.value(
                self._signals(cells, emitters).received
            )
        weighted = values * self.measure
        return weighted.reshape(self.grid_size)

    def gain(self, emitters: Positions) -> float:
        total = 0.0
        for _start, cells, measure in self._chunks():
            received = self._signals(cells, emitters).received
            total += float(np.sum(self.sensor_law.value(received) * measure))
        return total / len(self.cells)

    def gradient(self, emitters: Positions) -> Positions:
        return self.gain_and_gradient(emitters)[1]

    def gain_and_gradient(self, emitters: Positions) -> tuple[float, Positions]:
        total = 0.0
        gradient = np.zeros_like(emitters)
        for _start, cells, measure in self._chunks():
            signal = self._signals(cells, emitters)
            total += float(np.sum(self.sensor_law.value(signal.received) * measure))
            gradient -= self._pull(signal, measure)
        return total / len(self.cells), gradient / len(self.cells)

    def _chunks(self) -> Iterator[tuple[int, FloatArray, FloatArray]]:
        for start in range(0, len(self.cells), CELLS_PER_CHUNK):
            stop = start + CELLS_PER_CHUNK
            yield start, self.cells[start:stop], self.measure[start:stop]

    def _signals(self, cells: FloatArray, emitters: Positions) -> Signal:
        offsets = cells[:, None, :] - emitters[None, :, :]
        distances = np.linalg.norm(offsets, axis=-1)
        visible = visibility(cells, emitters, self.obstacles)
        received = np.sum(self.emitter_law.value(distances) * visible, axis=1)
        return Signal(offsets, distances, visible, received)

    def _pull(self, signal: Signal, measure: FloatArray) -> Positions:
        sensor_weight = measure * self.sensor_law.slope(signal.received)
        emitter_slope = self.emitter_law.slope(signal.distances)
        safe_distance = np.where(
            signal.distances > MINIMUM_DISTANCE,
            signal.distances,
            1.0,
        )
        unit_direction = signal.offsets / safe_distance[..., None]
        contribution = (sensor_weight[:, None] * signal.visible * emitter_slope)[
            ..., None
        ] * unit_direction
        return np.sum(contribution, axis=0)
