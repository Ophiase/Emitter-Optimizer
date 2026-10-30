from dataclasses import dataclass

import numpy as np

from emitter_optimizer.engine.geometry import visibility
from emitter_optimizer.engine.laws import FloatArray, Law, Positions

CELLS_PER_CHUNK = 4096
MINIMUM_DISTANCE = 1e-12


@dataclass(eq=False)
class Field:
    """The cells, the measure, the obstacles and the two laws of one map."""

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
        return (self._values(self.cells, emitters) * self.measure).reshape(
            self.grid_size
        )

    def gain(self, emitters: Positions) -> float:
        return float((self._values(self.cells, emitters) * self.measure).mean())

    def gradient(self, emitters: Positions) -> Positions:
        return self.gain_and_gradient(emitters)[1]

    def gain_and_gradient(self, emitters: Positions) -> tuple[float, Positions]:
        """The gain and its exact gradient in the emitter positions."""
        cells = self.cells
        measure = self.measure
        gradient = np.zeros_like(emitters)
        total = 0.0
        for start in range(0, len(cells), CELLS_PER_CHUNK):
            chunk = cells[start : start + CELLS_PER_CHUNK]
            weight = measure[start : start + CELLS_PER_CHUNK]
            delta = chunk[:, None, :] - emitters[None, :, :]
            distance = np.linalg.norm(delta, axis=-1)
            visible = visibility(chunk, emitters, self.obstacles)
            received = np.sum(self.emitter_law.value(distance) * visible, axis=1)
            total += float(np.sum(self.sensor_law.value(received) * weight))
            shared = weight * self.sensor_law.slope(received)
            slope = self.emitter_law.slope(distance)
            direction = (
                delta / np.where(distance > MINIMUM_DISTANCE, distance, 1.0)[..., None]
            )
            contribution = (shared[:, None] * visible * slope)[..., None] * direction
            gradient -= np.sum(contribution, axis=0)
        return total / len(cells), gradient / len(cells)

    def _values(self, cells: FloatArray, emitters: Positions) -> FloatArray:
        values = np.empty(len(cells))
        for start in range(0, len(cells), CELLS_PER_CHUNK):
            chunk = cells[start : start + CELLS_PER_CHUNK]
            distance = np.linalg.norm(chunk[:, None, :] - emitters[None, :, :], axis=-1)
            visible = visibility(chunk, emitters, self.obstacles)
            received = np.sum(self.emitter_law.value(distance) * visible, axis=1)
            values[start : start + CELLS_PER_CHUNK] = self.sensor_law.value(received)
        return values
