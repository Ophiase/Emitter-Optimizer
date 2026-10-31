from dataclasses import dataclass

import numpy as np

from scripts.situation import Situation


@dataclass(frozen=True, slots=True)
class Result:
    situation: Situation
    positions: np.ndarray
    initial_gain: float
    gain: float
    history: tuple[float, ...]
    seconds: float

    @property
    def improvement(self) -> float:
        return self.gain - self.initial_gain
