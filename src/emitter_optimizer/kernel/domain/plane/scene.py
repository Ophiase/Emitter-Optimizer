from dataclasses import dataclass, field
from typing import Self

import jax
import jax.numpy as jnp
from jax import Array

from emitter_optimizer.kernel.domain.domain import Domain
from emitter_optimizer.kernel.domain.plane.extent import Extent
from emitter_optimizer.kernel.domain.plane.grid_shape import GridShape
from emitter_optimizer.kernel.laws import Law
from emitter_optimizer.kernel.occlusion import Occlusion


@jax.tree_util.register_dataclass
@dataclass(frozen=True)
class Scene(Domain):
    """Cell centres `(points, 2)`, weights `(cells,)`, walls `(walls, 2, 2)`.

    Every length is in world units.
    """

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
            points=cell_centres(extent, grid),
            measure=measure,
            walls=jnp.zeros((0, 2, 2)) if walls is None else jnp.asarray(walls),
            bounds=extent.as_array(),
            grid=grid,
        )

    @property
    def shape(self) -> tuple[int, ...]:
        return (self.grid.rows, self.grid.columns)

    @property
    def scale(self) -> Array:
        return jnp.max(self.bounds)

    @property
    def cell(self) -> Array:
        return self.bounds / jnp.array([self.grid.columns, self.grid.rows])

    def project(self, positions: Array) -> Array:
        return jnp.clip(positions, 0.0, self.bounds)

    def signal(self, law: Law, positions: Array) -> Array:
        offsets = self.points[:, None, :] - positions[None, :, :]
        return law(self._length(offsets))

    def visibility(self, occlusion: Occlusion, emitters: Array) -> Array:
        """`(cells, emitters)`: the share of each sight line no wall blocks."""

        def block(visible: Array, wall: Array) -> tuple[Array, None]:
            return visible * (1.0 - self._crossing(occlusion, emitters, wall)), None

        clear = jnp.ones((self.points.shape[0], emitters.shape[0]))
        visible, _ = jax.lax.scan(block, clear, self.walls)
        return visible

    def _crossing(self, occlusion: Occlusion, emitters: Array, wall: Array) -> Array:
        start, end = wall[0], wall[1]
        along = end - start
        wall_length = self._length(along)
        sight = emitters[None, :, :] - self.points[:, None, :]
        sight_length = self._length(sight)
        start_side = self._cross(sight, start - self.points[:, None, :]) / sight_length
        end_side = self._cross(sight, end - self.points[:, None, :]) / sight_length
        cell_side = self._cross(along, self.points - start) / wall_length
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


def cell_centres(extent: Extent, grid: GridShape) -> Array:
    """World coordinates `(x, y)` of each cell centre, in row-major order."""
    rows, columns = jnp.meshgrid(
        jnp.arange(grid.rows), jnp.arange(grid.columns), indexing="ij"
    )
    centres = jnp.stack([columns, rows], axis=-1).reshape(-1, 2) + 0.5
    return centres * jnp.array([extent.width / grid.columns, extent.height / grid.rows])
