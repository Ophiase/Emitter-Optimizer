from collections.abc import Callable
from dataclasses import dataclass

from jax import Array

Law = Callable[[Array], Array]


@dataclass(frozen=True, slots=True)
class Physics:
    """`emitter` maps a distance to a signal, `sensor` a received signal to a score."""

    emitter: Law
    sensor: Law
