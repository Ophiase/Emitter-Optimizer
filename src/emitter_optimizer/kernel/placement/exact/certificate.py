from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class Certificate:
    """A placement of weight `lower`, and a bound `upper` no placement can pass."""

    positions: np.ndarray
    lower: int
    upper: int
    vertices: int
    columns: int
    seconds: float

    @property
    def proved(self) -> bool:
        return self.lower == self.upper
