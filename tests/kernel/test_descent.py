import jax
import jax.numpy as jnp

from emitter_optimizer.kernel import (
    Coverage,
    Descender,
    DescentSettings,
    Extent,
    GridShape,
    HardOcclusion,
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


def test_a_descent_improves_on_its_start() -> None:
    scene = Scene.of(EXTENT, GridShape(16, 16), walls=WALL)
    settings = DescentSettings(emitters=4, steps=60, starts=8, report_every=20)
    start = scene.sample(jax.random.key(settings.seed), 8, 4)
    before = max(
        float(Coverage(scene, HardOcclusion(), PHYSICS).gain(positions))
        for positions in start
    )
    result = Descender(scene, PHYSICS, settings).run()
    assert result.gain > before
    assert len(result.history) == settings.steps


def test_a_long_descent_never_ends_below_its_start() -> None:
    scene = Scene.of(EXTENT, GridShape(16, 16), walls=WALL)
    start = scene.sample(jax.random.key(0), 1, 4)
    coverage = Coverage(scene, HardOcclusion(), PHYSICS)
    settings = DescentSettings(emitters=4, steps=40, step_size=0.2, report_every=10)

    result = Descender(scene, PHYSICS, settings, start=start).run()

    assert result.gain >= float(coverage.gain(start[0]))
    assert abs(result.gain - float(coverage.gain(result.positions))) < 1e-6
