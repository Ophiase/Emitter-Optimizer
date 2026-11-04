from dataclasses import dataclass, field
from typing import Self

import jax
import jax.numpy as jnp
from jax import Array

from emitter_optimizer.kernel.domain.domain import Domain
from emitter_optimizer.kernel.laws import Law

LENGTH_FLOOR = 1e-12


@jax.tree_util.register_dataclass
@dataclass(frozen=True)
class Sphere(Domain):
    """The unit sphere on a latitude-longitude grid; the distance is an angle."""

    rows: int = field(metadata={"static": True})
    columns: int = field(metadata={"static": True})

    @classmethod
    def of(cls, rows: int, columns: int, density: Array | None = None) -> Self:
        """`density` is `(rows, columns)`, north first; the cell area is built in."""
        latitude = jnp.pi / 2 - (jnp.arange(rows) + 0.5) * jnp.pi / rows
        longitude = (jnp.arange(columns) + 0.5) * 2 * jnp.pi / columns - jnp.pi
        lat, lon = jnp.meshgrid(latitude, longitude, indexing="ij")
        points = jnp.stack(
            [jnp.cos(lat) * jnp.cos(lon), jnp.cos(lat) * jnp.sin(lon), jnp.sin(lat)],
            axis=-1,
        ).reshape(-1, 3)
        area = jnp.cos(lat) / jnp.mean(jnp.cos(lat))
        weights = area if density is None else area * density
        return cls(points, weights.reshape(-1), rows, columns)

    @property
    def shape(self) -> tuple[int, ...]:
        return (self.rows, self.columns)

    @property
    def scale(self) -> Array:
        return jnp.asarray(jnp.pi)

    @property
    def cell(self) -> Array:
        return jnp.full(3, jnp.pi / self.rows)

    def project(self, positions: Array) -> Array:
        norm = jnp.sqrt(jnp.sum(positions**2, axis=-1, keepdims=True) + LENGTH_FLOOR)
        return positions / norm

    def signal(self, law: Law, positions: Array) -> Array:
        """Projecting first keeps the gradient tangent to the sphere."""
        on_sphere = self.project(positions)
        cosine = self.points @ on_sphere.T
        cross = jnp.cross(self.points[:, None, :], on_sphere[None, :, :])
        sine = jnp.sqrt(jnp.sum(cross**2, axis=-1) + LENGTH_FLOOR)
        return law(jnp.arctan2(sine, cosine))
