import jax
import jax.numpy as jnp
from jax.test_util import check_grads

from emitter_optimizer.kernel import (
    Coverage,
    Extent,
    GridShape,
    HardOcclusion,
    Physics,
    Scene,
    SoftOcclusion,
)

jax.config.update("jax_enable_x64", True)

PHYSICS = Physics(
    emitter=lambda distance: jnp.exp(-distance / 5.0),
    sensor=lambda signal: jnp.tanh(signal),
)
EXTENT = Extent(100.0, 100.0)
WALL = jnp.array([[[50.0, 0.0], [50.0, 100.0]]])


def test_a_hard_wall_blocks_the_sight_line() -> None:
    scene = Scene.of(EXTENT, GridShape(4, 4), walls=WALL)
    emitter = jnp.array([[90.0, 50.0]])
    visible = scene.visibility(HardOcclusion(), emitter)
    assert not bool(visible[0, 0])
    assert bool(visible[-1, 0])


def test_the_soft_gradient_sees_the_wall_the_hard_one_ignores() -> None:
    density = jnp.zeros((4, 4)).at[1, 0].set(1.0)
    wall = jnp.array([[[50.0, 0.0], [50.0, 60.0]]])
    scene = Scene.of(EXTENT, GridShape(4, 4), density, wall)
    hidden = jnp.array([[75.0, 40.0]])

    def hard_gain(p: jax.Array) -> jax.Array:
        return Coverage(scene, HardOcclusion(), PHYSICS).gain(p)

    def soft_gain(p: jax.Array) -> jax.Array:
        return Coverage(scene, SoftOcclusion(jnp.asarray(0.2)), PHYSICS).gain(p)

    hard = jax.grad(hard_gain)(hidden)
    soft = jax.grad(soft_gain)(hidden)
    assert not bool(jnp.any(hard))
    assert float(soft[0, 1]) > 0.0


def test_the_gain_ignores_the_order_of_emitters() -> None:
    scene = Scene.of(EXTENT, GridShape(8, 8), walls=WALL)
    emitters = jnp.array([[10.0, 20.0], [70.0, 80.0], [40.0, 55.0]])
    occlusion = SoftOcclusion(jnp.asarray(1.0))
    forward = Coverage(scene, occlusion, PHYSICS).gain(emitters)
    backward = Coverage(scene, occlusion, PHYSICS).gain(emitters[::-1])
    assert jnp.allclose(forward, backward)


def test_the_soft_gain_has_the_gradient_it_reports() -> None:
    scene = Scene.of(EXTENT, GridShape(6, 6), walls=WALL)
    emitters = jnp.array([[30.0, 20.0], [65.0, 70.0]])

    def objective(positions: jax.Array) -> jax.Array:
        return Coverage(scene, SoftOcclusion(jnp.asarray(0.3)), PHYSICS).gain(positions)

    check_grads(objective, (emitters,), order=1, modes=("rev",))
