"""The arrays and the two laws the engine is written in terms of."""

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
Positions = NDArray[np.float64]
SignalFunction = Callable[[FloatArray], FloatArray]
Derivative = Callable[[FloatArray], FloatArray]
FINITE_DIFFERENCE_STEP = 1e-6


@dataclass(frozen=True, slots=True)
class Law:
    """A user function and, when it exists, its derivative."""

    value: SignalFunction
    derivative: Derivative | None = None

    @classmethod
    def of(cls, function: SignalFunction) -> Law:
        return cls(function)

    def slope(self, points: FloatArray) -> FloatArray:
        """The derivative at `points`, exact or by central difference."""
        if self.derivative is not None:
            return self.derivative(points)
        step = FINITE_DIFFERENCE_STEP * (1.0 + np.abs(points))
        return (self.value(points + step) - self.value(points - step)) / (2.0 * step)
