from dataclasses import dataclass

import jax.numpy as jnp
from jax import Array


@dataclass(frozen=True, slots=True)
class Extent:
    width: float
    height: float

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            message = f"an extent is positive, not {self.width} x {self.height}"
            raise ValueError(message)

    def as_array(self) -> Array:
        return jnp.array([self.width, self.height])
