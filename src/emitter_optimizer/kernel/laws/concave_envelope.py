from dataclasses import dataclass
from typing import Self

import jax.numpy as jnp
import numpy as np
from jax import Array

from emitter_optimizer.kernel.laws.law import Law

SAMPLES = 8193


@dataclass(frozen=True, slots=True)
class ConcaveEnvelope:
    """The smallest concave, non-decreasing law above `sensor` on a range of signal.

    Above the sensor, its best gain bounds the sensor's; and being concave and
    non-decreasing, it admits an online bound where the sensor itself does not.
    Each sample takes the score of the next one, so that a jump between two samples
    stays under it.
    """

    signal: Array
    score: Array

    @classmethod
    def of(cls, sensor: Law, largest_signal: float) -> Self:
        signal = np.linspace(0.0, largest_signal, SAMPLES)
        score = np.maximum.accumulate(
            np.asarray(sensor(jnp.asarray(signal)), dtype=np.float64)
        )
        score = np.append(score[1:], score[-1])
        hull = _upper_hull(signal, score)
        return cls(jnp.asarray(signal[hull]), jnp.asarray(score[hull]))

    def __call__(self, values: Array, /) -> Array:
        return jnp.interp(values, self.signal, self.score)


def _upper_hull(signal: np.ndarray, score: np.ndarray) -> list[int]:
    hull: list[int] = []
    for index in range(signal.shape[0]):
        while len(hull) >= 2 and _turns_up(signal, score, hull[-2], hull[-1], index):
            hull.pop()
        hull.append(index)
    return hull


def _turns_up(
    signal: np.ndarray, score: np.ndarray, first: int, middle: int, last: int
) -> bool:
    return (score[middle] - score[first]) * (signal[last] - signal[first]) <= (
        score[last] - score[first]
    ) * (signal[middle] - signal[first])
