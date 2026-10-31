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


@dataclass(frozen=True, slots=True)
class GridShape:
    rows: int
    columns: int

    def __post_init__(self) -> None:
        if self.rows <= 0 or self.columns <= 0:
            message = f"a grid has cells, not {self.rows} x {self.columns}"
            raise ValueError(message)

    @property
    def cells(self) -> int:
        return self.rows * self.columns
