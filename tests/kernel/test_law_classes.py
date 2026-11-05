import itertools

import jax.numpy as jnp
import numpy as np
import pytest
from jax import Array
from scipy.special import logsumexp

from emitter_optimizer.kernel import (
    Coverage,
    Extent,
    Greedy,
    GridShape,
    HardOcclusion,
    Physics,
    Scene,
)
from emitter_optimizer.kernel.laws import ConcaveEnvelope, Law
from emitter_optimizer.kernel.placement.online_bound import OnlineBound

SIDE = 16
WALL = jnp.array([[[40.0, 10.0], [40.0, 60.0]]])
SCENE = Scene.of(Extent(80.0, 80.0), GridShape(SIDE, SIDE), walls=WALL)
FREE = Scene.of(Extent(80.0, 80.0), GridShape(SIDE, SIDE))


def _gaussian(distance: Array) -> Array:
    return jnp.exp(-((distance / 15.0) ** 2))


SATURATING = Physics(_gaussian, lambda signal: 1.0 - jnp.exp(-signal))
DOME = Physics(_gaussian, lambda signal: 1.0 - (1.0 - signal) ** 2)
THRESHOLD = Physics(
    _gaussian, lambda signal: 1.0 / (1.0 + jnp.exp((0.8 - signal) / 0.02))
)
LINEAR = Physics(_gaussian, lambda signal: signal)


def _gain(scene: Scene, physics: Physics, positions: Array | np.ndarray) -> float:
    coverage = Coverage(scene, HardOcclusion(), physics)
    return float(coverage.gain(jnp.asarray(positions, dtype=jnp.float32)))


def _positions(seed: int, count: int) -> np.ndarray:
    return np.random.default_rng(seed).uniform(0.0, 80.0, (count, 2))


def _largest_loss_of_returns(physics: Physics, seed: int) -> float:
    """How far a new emitter helps a larger set more than a part of it; 0 if never."""
    small, large = _positions(seed + 1, 1), _positions(seed + 1, 3)
    large[0] = small[0]
    new = _positions(seed + 2, 1)
    gain_small = _gain(SCENE, physics, np.vstack((small, new))) - _gain(
        SCENE, physics, small
    )
    gain_large = _gain(SCENE, physics, np.vstack((large, new))) - _gain(
        SCENE, physics, large
    )
    return gain_large - gain_small


def test_a_linear_sensor_sends_every_emitter_to_the_same_place() -> None:
    best = FREE.points[
        int(
            jnp.argmax(
                Coverage(FREE, HardOcclusion(), LINEAR).sent(FREE.points).mean(axis=0)
            )
        )
    ]
    stacked = _gain(FREE, LINEAR, np.tile(np.asarray(best), (4, 1)))

    assert all(
        _gain(FREE, LINEAR, _positions(seed, 4)) <= stacked for seed in range(30)
    )


@pytest.mark.parametrize("physics", [SATURATING, DOME])
def test_a_concave_sensor_has_diminishing_returns_even_behind_a_wall(
    physics: Physics,
) -> None:
    worst = max(_largest_loss_of_returns(physics, seed) for seed in range(40))

    assert worst < 1e-5


def test_a_threshold_sensor_rewards_a_second_emitter_more_than_the_first() -> None:
    worst = max(_largest_loss_of_returns(THRESHOLD, seed) for seed in range(40))

    assert worst > 1e-3


def test_a_dome_can_lose_from_one_more_emitter() -> None:
    near = np.array([[40.0, 70.0], [42.0, 70.0], [38.0, 70.0]])

    assert _gain(FREE, DOME, near) < _gain(FREE, DOME, near[:2])


def test_the_online_bound_and_greedy_hold_against_every_subset() -> None:
    candidates = jnp.asarray(_positions(7, 10), dtype=jnp.float32)
    subsets = itertools.combinations(range(10), 3)
    optimum = max(
        _gain(SCENE, SATURATING, candidates[np.array(chosen)]) for chosen in subsets
    )
    greedy = Greedy(SCENE, SATURATING, candidates).place(3)
    bound = OnlineBound(SCENE, SATURATING, candidates)

    assert _gain(SCENE, SATURATING, greedy) >= (1.0 - 1.0 / np.e) * optimum
    assert bound.of(greedy) >= optimum - 1e-6
    assert bound.of(jnp.asarray(_positions(9, 3), dtype=jnp.float32)) >= optimum - 1e-6


def test_a_quadratic_sensor_is_a_field_minus_a_pair_energy() -> None:
    positions = jnp.asarray(_positions(3, 4), dtype=jnp.float32)
    sent = Coverage(FREE, HardOcclusion(), DOME).sent(positions)
    measure = FREE.measure[:, None]

    field = 2.0 * jnp.mean(jnp.sum(sent, axis=1) * FREE.measure)
    pairs = jnp.mean(
        jnp.sum((sent * measure)[:, :, None] * sent[:, None, :], axis=(1, 2))
    )

    assert float(field - pairs) == pytest.approx(_gain(FREE, DOME, positions), abs=1e-5)


def test_a_logarithm_tends_to_k_means_as_the_gaussian_narrows() -> None:
    points = np.asarray(FREE.points, dtype=np.float64)
    squared = np.sum((points[:, None] - _positions(3, 5)[None]) ** 2, axis=-1)
    nearest = float(np.mean(np.min(squared, axis=1)))
    errors = [
        abs(
            float(np.mean(logsumexp(-sharpness * squared, axis=1))) / sharpness
            + nearest
        )
        for sharpness in (0.05, 0.5, 5.0)
    ]

    assert errors[2] < errors[1] < errors[0]
    assert errors[2] < 0.05 * nearest


def test_the_grid_and_the_slope_bound_the_continuous_optimum_without_walls() -> None:
    lipschitz_signal = np.sqrt(2.0 / np.e) / 15.0
    coarse = np.linspace(0.0, 80.0, 9)
    grid = jnp.asarray(
        np.stack(np.meshgrid(coarse, coarse), axis=-1).reshape(-1, 2), dtype=jnp.float32
    )
    half_diagonal = (coarse[1] - coarse[0]) / np.sqrt(2.0)
    greedy = Greedy(FREE, SATURATING, grid).place(3)
    bound = OnlineBound(FREE, SATURATING, grid).of(greedy)
    margin = 3 * lipschitz_signal * half_diagonal

    fine = np.linspace(0.0, 80.0, 33)
    finer = np.stack(np.meshgrid(fine, fine), axis=-1).reshape(-1, 2)
    denser = Greedy(FREE, SATURATING, jnp.asarray(finer, dtype=jnp.float32)).place(3)

    assert _gain(FREE, SATURATING, denser) <= bound + margin


def test_convex_harm_is_worst_inside_and_least_at_a_corner() -> None:
    harm = Physics(lambda distance: 200.0 - distance, lambda signal: -signal)
    axis = np.linspace(0.0, 80.0, 41)
    grid = np.stack(np.meshgrid(axis, axis), axis=-1).reshape(-1, 2)
    gains = [_gain(FREE, harm, position[None]) for position in grid]
    best = grid[int(np.argmax(gains))]

    assert all(value in {0.0, 80.0} for value in best)


def test_only_ratios_of_lengths_matter() -> None:
    stretch = 7.0
    wide = Scene.of(Extent(560.0, 560.0), GridShape(SIDE, SIDE), walls=WALL * stretch)
    stretched = Physics(
        lambda distance: _gaussian(distance / stretch), SATURATING.sensor
    )
    positions = _positions(4, 5)

    assert _gain(wide, stretched, positions * stretch) == pytest.approx(
        _gain(SCENE, SATURATING, positions), abs=1e-5
    )


def test_two_rooms_that_cannot_see_each_other_add_up() -> None:
    partition = jnp.array([[[40.0, -1.0], [40.0, 81.0]]])
    rooms = Scene.of(Extent(80.0, 80.0), GridShape(SIDE, SIDE), walls=partition)
    left = np.array([[10.0, 20.0], [25.0, 60.0]])
    right = np.array([[60.0, 30.0]])
    origin = _gain(rooms, SATURATING, np.empty((0, 2)))

    together = _gain(rooms, SATURATING, np.vstack((left, right)))
    apart = _gain(rooms, SATURATING, left) + _gain(rooms, SATURATING, right) - origin

    assert together == pytest.approx(apart, abs=1e-5)


def _stairs(signal: Array) -> Array:
    return jnp.floor(jnp.minimum(signal, 1.2) * 5.0) / 5.0


@pytest.mark.parametrize(
    "sensor", [_stairs, THRESHOLD.sensor, DOME.sensor], ids=["stairs", "s", "dome"]
)
def test_the_envelope_bounds_a_sensor_that_is_not_concave(sensor: Law) -> None:
    emitters = 3
    physics = Physics(_gaussian, sensor)
    envelope = ConcaveEnvelope.of(sensor, float(emitters))
    signal = jnp.linspace(0.0, float(emitters), 2001)
    curved = jnp.diff(envelope(signal), n=2)
    candidates = jnp.asarray(_positions(7, 10), dtype=jnp.float32)
    optimum = max(
        _gain(SCENE, physics, candidates[np.array(chosen)])
        for chosen in itertools.combinations(range(10), emitters)
    )
    start = jnp.asarray(_positions(9, emitters), dtype=jnp.float32)

    bound = OnlineBound(SCENE, Physics(_gaussian, envelope), candidates).of(start)

    assert jnp.all(envelope(signal) >= sensor(signal) - 1e-5)
    assert jnp.all(jnp.diff(envelope(signal)) >= -1e-5)
    assert float(jnp.max(curved)) < 1e-4
    assert bound >= optimum - 1e-5


def test_a_finite_reach_cuts_all_interaction_past_twice_the_reach() -> None:
    reach = 10.0
    compact = Physics(
        lambda distance: jnp.maximum(1.0 - (distance / reach) ** 2, 0.0) ** 2,
        SATURATING.sensor,
    )
    first, second = np.array([[10.0, 10.0]]), np.array([[70.0, 70.0]])
    together = _gain(FREE, compact, np.vstack((first, second)))
    apart = _gain(FREE, compact, first) + _gain(FREE, compact, second)

    tail = Physics(
        lambda distance: 1.0 / (1.0 + (distance / reach) ** 2), SATURATING.sensor
    )
    tail_together = _gain(FREE, tail, np.vstack((first, second)))
    tail_apart = _gain(FREE, tail, first) + _gain(FREE, tail, second)

    assert together == pytest.approx(apart, abs=1e-6)
    assert tail_apart - tail_together > 1e-3


def test_a_fading_emitter_is_better_inside_the_hull_of_the_demand() -> None:
    density = jnp.zeros((SIDE, SIDE)).at[6:10, 6:10].set(1.0)
    scene = Scene.of(Extent(80.0, 80.0), GridShape(SIDE, SIDE), density)
    outside = np.array([[75.0, 40.0]])
    inside = np.array([[47.5, 40.0]])

    assert _gain(scene, SATURATING, inside) > _gain(scene, SATURATING, outside)


def test_a_ring_emitter_can_prefer_to_stand_outside_the_hull() -> None:
    density = jnp.zeros((SIDE, SIDE)).at[6:10, 6:10].set(1.0)
    scene = Scene.of(Extent(80.0, 80.0), GridShape(SIDE, SIDE), density)
    ring = Physics(
        lambda distance: jnp.exp(-(((distance - 30.0) / 4.0) ** 2)), SATURATING.sensor
    )
    outside = np.array([[70.0, 40.0]])
    inside = np.array([[40.0, 40.0]])

    assert _gain(scene, ring, outside) > _gain(scene, ring, inside)


def test_a_fading_law_is_a_positive_mixture_of_disks() -> None:
    radii = np.linspace(0.0, 200.0, 4001)
    distance = np.array([0.0, 3.0, 11.0, 40.0])
    law = np.exp(-((radii / 15.0) ** 2))
    weights = -np.diff(law)
    disks = distance[:, None] <= radii[1:][None, :]

    assert np.all(weights >= 0.0)
    assert disks @ weights == pytest.approx(np.exp(-((distance / 15.0) ** 2)), abs=3e-3)
