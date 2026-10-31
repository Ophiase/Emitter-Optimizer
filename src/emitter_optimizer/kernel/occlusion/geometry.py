import jax
import jax.numpy as jnp
from jax import Array

from emitter_optimizer.kernel.occlusion.base import Occlusion

LENGTH_FLOOR = 1e-12


def length(vectors: Array) -> Array:
    return jnp.sqrt(jnp.sum(vectors**2, axis=-1) + LENGTH_FLOOR)


def cross(first: Array, second: Array) -> Array:
    return first[..., 0] * second[..., 1] - first[..., 1] * second[..., 0]


def apart(occlusion: Occlusion, first: Array, second: Array) -> Array:
    first_side, second_side = occlusion.side(first), occlusion.side(second)
    return first_side + second_side - 2.0 * first_side * second_side


def crossing(occlusion: Occlusion, cells: Array, emitters: Array, wall: Array) -> Array:
    start, end = wall[0], wall[1]
    along = end - start
    wall_length = length(along)
    cell_side = cross(along, cells - start) / wall_length
    emitter_side = cross(along, emitters - start) / wall_length
    sight = emitters[None, :, :] - cells[:, None, :]
    sight_length = length(sight)
    start_side = cross(sight, start - cells[:, None, :]) / sight_length
    end_side = cross(sight, end - cells[:, None, :]) / sight_length
    return apart(occlusion, cell_side[:, None], emitter_side[None, :]) * apart(
        occlusion, start_side, end_side
    )


def visibility(
    occlusion: Occlusion, cells: Array, emitters: Array, walls: Array
) -> Array:
    def block(visible: Array, wall: Array) -> tuple[Array, None]:
        return visible * (1.0 - crossing(occlusion, cells, emitters, wall)), None

    clear = jnp.ones((cells.shape[0], emitters.shape[0]))
    visible, _ = jax.lax.scan(block, clear, walls)
    return visible
