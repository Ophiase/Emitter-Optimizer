from abc import ABC, abstractmethod
from dataclasses import dataclass

import jax
import jax.numpy as jnp
from jax import Array

from emitter_optimizer.kernel.laws import Law
from emitter_optimizer.kernel.occlusion import Occlusion


@dataclass(frozen=True)
class Domain(ABC):
    """Where the gain is integrated: the gain and the descent see nothing else.

    `points` is `(points, dimension)` and `measure` is `(points,)`.
    """

    points: Array
    measure: Array

    @property
    @abstractmethod
    def shape(self) -> tuple[int, ...]:
        """The grid `points` unravels to, to draw a value map."""
        raise NotImplementedError

    @property
    @abstractmethod
    def scale(self) -> Array:
        """The length a step and a blur are expressed against."""
        raise NotImplementedError

    @property
    @abstractmethod
    def cell(self) -> Array:
        """The size of one cell, along each axis."""
        raise NotImplementedError

    @abstractmethod
    def signal(self, law: Law, positions: Array) -> Array:
        """`(points, emitters)`: what each emitter sends each point, walls aside."""
        raise NotImplementedError

    @abstractmethod
    def project(self, positions: Array) -> Array:
        """Bring positions back onto the domain."""
        raise NotImplementedError

    def visibility(self, occlusion: Occlusion, emitters: Array) -> Array:
        """`(points, emitters)`: nothing blocks unless a domain says so."""
        del occlusion
        return jnp.ones((self.points.shape[0], emitters.shape[0]))

    def sample(self, key: Array, starts: int, emitters: int) -> Array:
        """`(starts, emitters, dimension)` positions drawn from the measure."""
        choice_key, jitter_key = jax.random.split(key)
        total = jnp.sum(self.measure)
        weights = jnp.where(total > 0, self.measure / total, 1.0 / self.measure.size)
        indices = jax.random.choice(
            choice_key, self.measure.size, (starts, emitters), p=weights
        )
        jitter = jax.random.uniform(
            jitter_key,
            (starts, emitters, self.points.shape[1]),
            minval=-0.5,
            maxval=0.5,
        )
        return self.project(self.points[indices] + jitter * self.cell)
