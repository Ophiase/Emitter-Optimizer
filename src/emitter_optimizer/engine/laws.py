from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
Positions = NDArray[np.float64]
SignalFunction = Callable[[FloatArray], FloatArray]
Derivative = Callable[[FloatArray], FloatArray]
FINITE_DIFFERENCE_STEP = 1e-6
ENTRY = "eval"
DERIVATIVE = "derivative"


@dataclass(frozen=True, slots=True)
class Law:
    value: SignalFunction
    derivative: Derivative | None = None

    @classmethod
    def of(cls, function: SignalFunction) -> Law:
        return cls(function)

    def slope(self, points: FloatArray) -> FloatArray:
        if self.derivative is not None:
            return self.derivative(points)
        step = FINITE_DIFFERENCE_STEP * (1.0 + np.abs(points))
        return (self.value(points + step) - self.value(points - step)) / (2.0 * step)


def load_law(source: str) -> Law:
    namespace: dict[str, Any] = {}
    exec(source, namespace)
    value = cast(SignalFunction, namespace[ENTRY])
    derivative = cast(Derivative | None, namespace.get(DERIVATIVE))
    return Law(value, derivative)


def load_law_file(path: Path) -> Law:
    return load_law(path.read_text(encoding="utf-8"))
