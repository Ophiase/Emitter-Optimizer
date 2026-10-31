from functools import partial

import jax
import jax.numpy as jnp
from jax import Array

from emitter_optimizer.kernel.laws import Physics
from emitter_optimizer.kernel.occlusion import Occlusion
from emitter_optimizer.kernel.scene import Scene

LENGTH_FLOOR = 1e-12


def coverage(
    positions: Array,
    scene: Scene,
    occlusion: Occlusion,
    physics: Physics,
) -> Array:
    offsets = scene.cells[:, None, :] - positions[None, :, :]
    distances = jnp.sqrt(jnp.sum(offsets**2, axis=-1) + LENGTH_FLOOR)
    visible = scene.visibility(occlusion, positions)
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
