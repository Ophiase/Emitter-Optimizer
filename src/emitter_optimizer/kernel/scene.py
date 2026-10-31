from dataclasses import dataclass, field
from typing import Self

import jax
import jax.numpy as jnp
from jax import Array

from emitter_optimizer.kernel.shapes import Extent, GridShape


@jax.tree_util.register_dataclass
@dataclass(frozen=True)
class Scene:
    """Cell centres `(cells, 2)`, weights `(cells,)`, walls `(walls, 2, 2)`.

    Every length is in world units.
    """

    cells: Array
    measure: Array
    walls: Array
    bounds: Array
    grid: GridShape = field(metadata={"static": True})

    @classmethod
    def of(
        cls,
        extent: Extent,
        grid: GridShape,
        density: Array | None = None,
        walls: Array | None = None,
    ) -> Self:
        measure = jnp.ones(grid.cells) if density is None else density.reshape(-1)
        if measure.shape != (grid.cells,):
            message = f"a density of shape {measure.shape} does not fit {grid}"
            raise ValueError(message)
        return cls(
            cells=cell_centres(extent, grid),
            measure=measure,
            walls=jnp.zeros((0, 2, 2)) if walls is None else jnp.asarray(walls),
            bounds=extent.as_array(),
            grid=grid,
        )

    def sample(self, key: Array, starts: int, emitters: int) -> Array:
        """`(starts, emitters, 2)` positions drawn from the measure, within a cell."""
        choice_key, jitter_key = jax.random.split(key)
        total = jnp.sum(self.measure)
        weights = jnp.where(total > 0, self.measure / total, 1.0 / self.measure.size)
        indices = jax.random.choice(
            choice_key, self.measure.size, (starts, emitters), p=weights
        )
        cell = self.bounds / jnp.array([self.grid.columns, self.grid.rows])
        jitter = jax.random.uniform(
            jitter_key, (starts, emitters, 2), minval=-0.5, maxval=0.5
        )
        return self.cells[indices] + jitter * cell


def cell_centres(extent: Extent, grid: GridShape) -> Array:
    """World coordinates `(x, y)` of each cell centre, in row-major order."""
    rows, columns = jnp.meshgrid(
        jnp.arange(grid.rows), jnp.arange(grid.columns), indexing="ij"
    )
    centres = jnp.stack([columns, rows], axis=-1).reshape(-1, 2) + 0.5
    return centres * jnp.array([extent.width / grid.columns, extent.height / grid.rows])
