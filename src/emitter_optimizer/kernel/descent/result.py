from dataclasses import dataclass

from jax import Array


@dataclass(frozen=True, slots=True)
class DescentResult:
    """`gain` and `start_gains` are the best seen with the sharp walls;
    `history` is the best blurred objective at each step."""

    positions: Array
    gain: float
    history: tuple[float, ...]
    start_gains: tuple[float, ...]
