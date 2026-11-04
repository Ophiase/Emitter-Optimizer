from dataclasses import dataclass, field
from itertools import product
from typing import Self

import jax
import jax.numpy as jnp
from jax import Array

from emitter_optimizer.kernel.domain.domain import Domain
from emitter_optimizer.kernel.laws import Law

LENGTH_FLOOR = 1e-12


@jax.tree_util.register_dataclass
@dataclass(frozen=True)
class Torus(Domain):
    """A periodic cell: an emitter also acts through its images in the lattice.

    `reach` counts the shells of images summed around the nearest one.
    """

    lengths: Array
    grid: tuple[int, ...] = field(metadata={"static": True})
    reach: int = field(default=0, metadata={"static": True})

    @classmethod
    def of(
        cls,
        lengths: tuple[float, ...],
        grid: tuple[int, ...],
        density: Array | None = None,
        reach: int = 0,
    ) -> Self:
        size = jnp.asarray(lengths)
        axes = [(jnp.arange(count) + 0.5) for count in grid]
        centres = jnp.stack(jnp.meshgrid(*axes, indexing="ij"), axis=-1).reshape(
            -1, len(grid)
        )
        weights = jnp.ones(grid) if density is None else density
        points = centres * size / jnp.asarray(grid)
        return cls(points, weights.reshape(-1), size, grid, reach)

    @property
    def shape(self) -> tuple[int, ...]:
        return self.grid

    @property
    def scale(self) -> Array:
        return jnp.max(self.lengths)

    @property
    def cell(self) -> Array:
        return self.lengths / jnp.asarray(self.grid)

    def project(self, positions: Array) -> Array:
        return jnp.mod(positions, self.lengths)

    def signal(self, law: Law, positions: Array) -> Array:
        offsets = self.points[:, None, :] - positions[None, :, :]
        nearest = offsets - self.lengths * jnp.round(offsets / self.lengths)
        shells = range(-self.reach, self.reach + 1)
        images = jnp.asarray(list(product(shells, repeat=len(self.grid))))
        shifted = nearest[:, :, None, :] + images * self.lengths
        distances = jnp.sqrt(jnp.sum(shifted**2, axis=-1) + LENGTH_FLOOR)
        return jnp.sum(law(distances), axis=-1)
