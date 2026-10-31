from functools import partial

import jax
import jax.numpy as jnp
from jax import Array

from emitter_optimizer.kernel.laws import Physics
from emitter_optimizer.kernel.occlusion import Occlusion, length, visibility
from emitter_optimizer.kernel.scene import Scene


def coverage(
    positions: Array,
    scene: Scene,
    occlusion: Occlusion,
    physics: Physics,
) -> Array:
    """`(cells,)`: the sensor's score at each cell, weighted by its measure."""
    distances = length(scene.cells[:, None, :] - positions[None, :, :])
    visible = visibility(occlusion, scene.cells, positions, scene.walls)
    received = jnp.sum(physics.emitter(distances) * visible, axis=1)
    return physics.sensor(received) * scene.measure


@partial(jax.jit, static_argnames="physics")
def gain(
    positions: Array,
    scene: Scene,
    occlusion: Occlusion,
    physics: Physics,
) -> Array:
    return jnp.mean(coverage(positions, scene, occlusion, physics))


@partial(jax.jit, static_argnames="physics")
def value_map(
    positions: Array,
    scene: Scene,
    occlusion: Occlusion,
    physics: Physics,
) -> Array:
    values = coverage(positions, scene, occlusion, physics)
    return values.reshape(scene.grid.rows, scene.grid.columns)
