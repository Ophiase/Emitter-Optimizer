import jax
import jax.numpy as jnp
import pytest

from emitter_optimizer.kernel import (
    Coverage,
    Greedy,
    HardOcclusion,
    Physics,
    Volume,
)

ALPHA = 0.8
PHYSICS = Physics(
    emitter=lambda distance: jnp.exp(-distance / 4.0),
    sensor=lambda signal: 1.0 - jnp.exp(-signal),
)


def corridor(absorption: jax.Array | None = None) -> Volume:
    return Volume.of((20.0, 2.0, 2.0), (40, 2, 2), None, absorption, samples=128)


def slab(first: int, last: int) -> jax.Array:
    return jnp.zeros((40, 2, 2)).at[first:last].set(ALPHA)


def two_floors() -> Volume:
    absorption = jnp.zeros((8, 8, 8)).at[:, :, 4].set(4.0)
    density = jnp.zeros((8, 8, 8)).at[:, :, 2].set(1.0).at[:, :, 6].set(1.0)
    return Volume.of((8.0, 8.0, 8.0), (8, 8, 8), density, absorption)


def test_free_space_transmits_everything() -> None:
    visible = corridor().visibility(HardOcclusion(), jnp.array([[19.0, 1.0, 1.0]]))

    assert visible.shape == (160, 1)
    assert jnp.allclose(visible, 1.0)


@pytest.mark.parametrize(("first", "last", "thickness"), [(18, 22, 2.0), (16, 24, 4.0)])
def test_a_wall_attenuates_by_beer_lambert(
    first: int, last: int, thickness: float
) -> None:
    across_the_corridor = jnp.array([[19.75, 0.5, 0.5]])

    visible = corridor(slab(first, last)).visibility(
        HardOcclusion(), across_the_corridor
    )

    expected = float(jnp.exp(-ALPHA * thickness))
    assert float(visible[0, 0]) == pytest.approx(expected, rel=0.02)


def test_the_gain_has_a_gradient_through_a_wall() -> None:
    coverage = Coverage(corridor(slab(18, 22)), HardOcclusion(), PHYSICS)
    behind_the_wall = jnp.array([[16.0, 1.0, 1.0]])

    gradient = jax.grad(coverage.gain)(behind_the_wall)

    assert bool(jnp.all(jnp.isfinite(gradient)))
    assert float(jnp.abs(gradient[0, 0])) > 0.0


def test_a_floor_rewards_an_emitter_on_each_side() -> None:
    coverage = Coverage(two_floors(), HardOcclusion(), PHYSICS)
    one_each = jnp.array([[4.0, 4.0, 2.5], [4.0, 4.0, 6.5]])
    both_below = jnp.array([[2.0, 4.0, 2.5], [6.0, 4.0, 2.5]])

    assert float(coverage.gain(one_each)) > float(coverage.gain(both_below))


def test_greedy_on_a_lattice_uses_each_floor() -> None:
    volume = two_floors()

    positions = Greedy(volume, PHYSICS, volume.lattice((3, 3, 2))).place(2)

    heights = sorted(float(height) for height in positions[:, 2])
    assert heights[0] < 4.0 < heights[1]


def test_the_projection_clips_to_the_bounds() -> None:
    moved = corridor().project(jnp.array([[-1.0, 3.0, 1.0]]))

    assert moved.tolist() == [[0.0, 2.0, 1.0]]


def test_a_density_that_does_not_fit_is_refused() -> None:
    with pytest.raises(ValueError, match="do not fit"):
        Volume.of((1.0, 1.0, 1.0), (2, 2, 2), jnp.ones((2, 2)))
