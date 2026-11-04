import jax
import jax.numpy as jnp

from emitter_optimizer.kernel import (
    Coverage,
    Extent,
    Greedy,
    GridShape,
    HardOcclusion,
    Physics,
    Relocation,
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


def _two_peaks() -> Scene:
    density = jnp.zeros((16, 16)).at[3, 3].set(1.0).at[12, 12].set(1.0)
    return Scene.of(Extent(160.0, 160.0), GridShape(16, 16), density)


def test_a_relocation_leaves_the_hill_a_gradient_cannot() -> None:
    scene = _two_peaks()
    both_on_one_peak = jnp.array([[35.0, 35.0], [36.0, 36.0]])

    moved = Relocation(scene, PHYSICS).improve(both_on_one_peak)

    served = jnp.linalg.norm(moved - jnp.array([125.0, 125.0]), axis=1)
    assert float(jnp.min(served)) < 1.0


def test_a_relocation_never_lowers_the_gain() -> None:
    scene = _two_peaks()
    coverage = Coverage(scene, HardOcclusion(), PHYSICS)
    start = scene.sample(jax.random.key(0), 1, 4)[0]

    moved = Relocation(scene, PHYSICS).improve(start)

    assert float(coverage.gain(moved)) >= float(coverage.gain(start))


def test_a_relocation_keeps_a_placement_nothing_improves() -> None:
    scene = _two_peaks()
    optimum = jnp.array([[35.0, 35.0], [125.0, 125.0]])

    assert jnp.array_equal(Relocation(scene, PHYSICS).improve(optimum), optimum)
