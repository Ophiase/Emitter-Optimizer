from dataclasses import dataclass, field
from typing import Self

import jax
import jax.numpy as jnp
from jax import Array

from emitter_optimizer.kernel.occlusion import Occlusion
from emitter_optimizer.kernel.domain.extent import Extent
from emitter_optimizer.kernel.domain.grid_shape import GridShape


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

    def visibility(self, occlusion: Occlusion, emitters: Array) -> Array:
        """`(cells, emitters)`: the share of each sight line no wall blocks."""

        def block(visible: Array, wall: Array) -> tuple[Array, None]:
            return visible * (1.0 - self._crossing(occlusion, emitters, wall)), None

        clear = jnp.ones((self.cells.shape[0], emitters.shape[0]))
        visible, _ = jax.lax.scan(block, clear, self.walls)
        return visible

    def _crossing(self, occlusion: Occlusion, emitters: Array, wall: Array) -> Array:
        start, end = wall[0], wall[1]
        along = end - start
        wall_length = self._length(along)
        sight = emitters[None, :, :] - self.cells[:, None, :]
        sight_length = self._length(sight)
        start_side = self._cross(sight, start - self.cells[:, None, :]) / sight_length
        end_side = self._cross(sight, end - self.cells[:, None, :]) / sight_length
        cell_side = self._cross(along, self.cells - start) / wall_length
        emitter_side = self._cross(along, emitters - start) / wall_length
        return self._apart(occlusion, cell_side[:, None], emitter_side[None, :]) * (
            self._apart(occlusion, start_side, end_side)
        )

    def _length(self, vectors: Array) -> Array:
        return jnp.sqrt(jnp.sum(vectors**2, axis=-1) + 1e-12)

    def _cross(self, first: Array, second: Array) -> Array:
        return first[..., 0] * second[..., 1] - first[..., 1] * second[..., 0]

    def _apart(self, occlusion: Occlusion, first: Array, second: Array) -> Array:
        first_side, second_side = occlusion.side(first), occlusion.side(second)
        return first_side + second_side - 2.0 * first_side * second_side

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
