import jax
import jax.numpy as jnp

from emitter_optimizer.kernel import (
    DescentSettings,
    Extent,
    GridShape,
    HardOcclusion,
    Physics,
    Scene,
    descend,
    gain,
)

jax.config.update("jax_enable_x64", True)

PHYSICS = Physics(
    emitter=lambda distance: jnp.exp(-distance / 5.0),
    sensor=lambda signal: jnp.tanh(signal),
)
EXTENT = Extent(100.0, 100.0)
WALL = jnp.array([[[50.0, 0.0], [50.0, 100.0]]])


def test_a_descent_improves_on_its_start() -> None:
    scene = Scene.of(EXTENT, GridShape(16, 16), walls=WALL)
    settings = DescentSettings(emitters=4, steps=60, starts=8, report_every=20)
    start = scene.sample(jax.random.key(settings.seed), 8, 4)
    before = max(
        float(gain(positions, scene, HardOcclusion(), PHYSICS)) for positions in start
    )
    result = descend(scene, PHYSICS, settings)
    assert result.gain > before
    assert len(result.history) == settings.steps
