from dataclasses import dataclass

from jax import Array


@dataclass(frozen=True, slots=True)
class Step:
    index: int
    gain: float
    positions: Array
