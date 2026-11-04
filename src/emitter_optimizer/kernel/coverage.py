from dataclasses import dataclass

import jax.numpy as jnp
from jax import Array

from emitter_optimizer.kernel.domain import Domain
from emitter_optimizer.kernel.laws import Physics
from emitter_optimizer.kernel.occlusion import Occlusion


@dataclass(frozen=True, slots=True)
class Coverage:
    """The score of a placement over a domain, under one occlusion model."""

    domain: Domain
    occlusion: Occlusion
    physics: Physics

    def __call__(self, positions: Array) -> Array:
        signal = self.domain.signal(self.physics.emitter, positions)
        visible = self.domain.visibility(self.occlusion, positions)
        received = jnp.sum(signal * visible, axis=1)
        return self.physics.sensor(received) * self.domain.measure

    def gain(self, positions: Array) -> Array:
        return jnp.mean(self(positions))

    def value_map(self, positions: Array) -> Array:
        return self(positions).reshape(self.domain.shape)
