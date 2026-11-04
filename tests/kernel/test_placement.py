import jax.numpy as jnp

from emitter_optimizer.kernel import (
    Coverage,
    Extent,
    Greedy,
    GridShape,
    HardOcclusion,
    Physics,
    Scene,
)

PHYSICS = Physics(
    emitter=lambda distance: jnp.exp(-distance / 5.0),
    sensor=lambda signal: 1.0 - jnp.exp(-signal),
)


def test_the_first_emitter_goes_to_the_only_demand() -> None:
    density = jnp.zeros((8, 8)).at[2, 5].set(1.0)
    scene = Scene.of(Extent(80.0, 80.0), GridShape(8, 8), density)

    positions = Greedy(scene, PHYSICS).place(1)

    assert jnp.allclose(positions[0], jnp.array([55.0, 25.0]))


def test_a_wall_sends_the_second_emitter_behind_it() -> None:
    wall = jnp.array([[[40.0, 0.0], [40.0, 80.0]]])
    scene = Scene.of(Extent(80.0, 80.0), GridShape(8, 8), walls=wall)
    coverage = Coverage(scene, HardOcclusion(), PHYSICS)

    positions = Greedy(scene, PHYSICS).place(2)

    assert positions.shape == (2, 2)
    assert (positions[0, 0] - 40.0) * (positions[1, 0] - 40.0) < 0.0
    assert float(coverage.gain(positions)) > 0.0
