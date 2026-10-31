from dataclasses import dataclass

import jax.numpy as jnp
from jax import Array

from emitter_optimizer.kernel.laws import Physics
from emitter_optimizer.kernel.occlusion import Occlusion
from emitter_optimizer.kernel.scene import Scene

LENGTH_FLOOR = 1e-12


@dataclass(frozen=True, slots=True)
class Coverage:
    """The score of a placement over a scene, under one occlusion model."""

    scene: Scene
    occlusion: Occlusion
    physics: Physics

    def __call__(self, positions: Array) -> Array:
        offsets = self.scene.cells[:, None, :] - positions[None, :, :]
        distances = jnp.sqrt(jnp.sum(offsets**2, axis=-1) + LENGTH_FLOOR)
        visible = self.scene.visibility(self.occlusion, positions)
        received = jnp.sum(self.physics.emitter(distances) * visible, axis=1)
        return self.physics.sensor(received) * self.scene.measure

    def gain(self, positions: Array) -> Array:
        return jnp.mean(self(positions))

    def value_map(self, positions: Array) -> Array:
        return self(positions).reshape(self.scene.grid.rows, self.scene.grid.columns)
