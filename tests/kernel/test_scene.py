import jax
import jax.numpy as jnp

from emitter_optimizer.kernel import (
    Extent,
    GridShape,
    Physics,
    Scene,
)

jax.config.update("jax_enable_x64", True)

PHYSICS = Physics(
    emitter=lambda distance: jnp.exp(-distance / 5.0),
    sensor=lambda signal: jnp.tanh(signal),
)
EXTENT = Extent(100.0, 100.0)
WALL = jnp.array([[[50.0, 0.0], [50.0, 100.0]]])


def test_a_wide_density_keeps_its_rows() -> None:
    grid = GridShape(rows=16, columns=48)
    density = jnp.zeros((16, 48)).at[:4].set(1.0)
    scene = Scene.of(Extent(300.0, 100.0), grid, density)
    positions = scene.sample(jax.random.key(0), 4, 20)
    assert float(jnp.max(positions[..., 1])) <= 100.0 * 4 / 16
