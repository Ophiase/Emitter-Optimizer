from dataclasses import dataclass, field
from typing import Self

import jax
import jax.numpy as jnp
from jax import Array
from jax.scipy.ndimage import map_coordinates

from emitter_optimizer.kernel.domain.domain import Domain
from emitter_optimizer.kernel.laws import Law
from emitter_optimizer.kernel.occlusion import Occlusion

LENGTH_FLOOR = 1e-12
DEFAULT_SAMPLES = 32


@jax.tree_util.register_dataclass
@dataclass(frozen=True)
class Volume(Domain):
    """A voxel grid in world units: an absorption field stands where walls would.

    `density` and `absorption` are indexed `(x, y, z)`; absorption is per length.
    """

    absorption: Array
    lengths: Array
    grid: tuple[int, int, int] = field(metadata={"static": True})
    samples: int = field(default=DEFAULT_SAMPLES, metadata={"static": True})

    @classmethod
    def of(
        cls,
        lengths: tuple[float, float, float],
        grid: tuple[int, int, int],
        density: Array | None = None,
        absorption: Array | None = None,
        samples: int = DEFAULT_SAMPLES,
    ) -> Self:
        size = jnp.asarray(lengths)
        weights = jnp.ones(grid) if density is None else jnp.asarray(density)
        opacity = jnp.zeros(grid) if absorption is None else jnp.asarray(absorption)
        if weights.shape != grid or opacity.shape != grid:
            message = (
                f"a density of shape {weights.shape} and an absorption of shape "
                f"{opacity.shape} do not fit {grid}"
            )
            raise ValueError(message)
        axes = [jnp.arange(count) + 0.5 for count in grid]
        centres = jnp.stack(jnp.meshgrid(*axes, indexing="ij"), axis=-1).reshape(-1, 3)
        points = centres * size / jnp.asarray(grid)
        return cls(points, weights.reshape(-1), opacity, size, grid, samples)

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
        return jnp.clip(positions, 0.0, self.lengths)

    def signal(self, law: Law, positions: Array) -> Array:
        offsets = self.points[:, None, :] - positions[None, :, :]
        return law(jnp.sqrt(jnp.sum(offsets**2, axis=-1) + LENGTH_FLOOR))

    def visibility(self, occlusion: Occlusion, emitters: Array) -> Array:
        """`(points, emitters)`: the transmission along each sight line.

        One emitter at a time, replayed on the way back: the memory then grows with
        points times samples, not with their product by the emitters.
        """
        del occlusion
        return jax.lax.map(jax.checkpoint(self._transmission), emitters).T

    def lattice(self, stride: tuple[int, int, int]) -> Array:
        """`(candidates, 3)`: every `stride`-th voxel centre along each axis."""
        centres = self.points.reshape(*self.grid, 3)
        for axis, step in enumerate(stride):
            kept = jnp.arange(step // 2, self.grid[axis], step)
            centres = jnp.take(centres, kept, axis=axis)
        return centres.reshape(-1, 3)

    def _transmission(self, emitter: Array) -> Array:
        """Beer-Lambert: exp(-integral of absorption), by the midpoint rule."""
        sight = emitter - self.points
        fractions = (jnp.arange(self.samples) + 0.5) / self.samples
        along = self.points[:, None, :] + fractions[None, :, None] * sight[:, None, :]
        voxel = jnp.moveaxis(along / self.cell - 0.5, -1, 0)
        sampled = map_coordinates(self.absorption, list(voxel), order=1, mode="nearest")
        length = jnp.sqrt(jnp.sum(sight**2, axis=-1) + LENGTH_FLOOR)
        return jnp.exp(-length * jnp.mean(sampled, axis=1))
