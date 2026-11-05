import itertools

import jax.numpy as jnp
import numpy as np
import pytest

from emitter_optimizer.kernel import (
    Coverage,
    GridShape,
    HardOcclusion,
    Physics,
    Scene,
)
from emitter_optimizer.kernel.placement.exact import (
    CoverProgram,
    ExactPlacement,
    Instance,
)
from scripts.certify.family import Family

SMALL_FAMILIES = (
    Family(30, 1, 3),
    Family(30, 2, 3),
    Family(40, 2, 6),
    Family(40, 3, 0),
)


def _instance(points: list[list[float]], walls: list[list[list[float]]]) -> Instance:
    return Instance(
        name="by-hand",
        points=np.array(points),
        weights=np.ones(len(points), dtype=np.int64),
        walls=np.array(walls, dtype=np.float64).reshape(-1, 2, 2),
        radius=10.0,
        emitters=1,
        width=100.0,
        height=100.0,
    )


def test_three_points_on_a_circle_are_covered_from_its_centre_alone() -> None:
    instance = _instance([[60.0, 50.0], [40.0, 50.0], [50.0, 60.0], [90.0, 90.0]], [])

    certificate = ExactPlacement(instance).solve()

    assert certificate.lower == certificate.upper == 3
    assert certificate.positions[0] == pytest.approx([50.0, 50.0], abs=1e-5)


def test_a_wall_between_two_close_points_costs_one_of_them() -> None:
    points = [[49.0, 50.0], [51.0, 50.0]]

    free = ExactPlacement(_instance(points, [])).solve()
    walled = ExactPlacement(_instance(points, [[[50.0, 20.0], [50.0, 80.0]]])).solve()

    assert (free.lower, free.upper) == (2, 2)
    assert (walled.lower, walled.upper) == (1, 1)


def test_an_emitter_past_the_end_of_a_wall_sees_both_sides() -> None:
    points = [[49.0, 50.0], [51.0, 50.0]]
    walled = _instance(points, [[[50.0, 20.0], [50.0, 53.0]]])

    certificate = ExactPlacement(walled).solve()

    assert (certificate.lower, certificate.upper) == (2, 2)
    assert certificate.positions[0][1] > 53.0 - 1e-6


@pytest.mark.parametrize("family", SMALL_FAMILIES)
@pytest.mark.parametrize("seed", range(6))
def test_nothing_found_by_a_dense_search_passes_the_bound(
    family: Family, seed: int
) -> None:
    instance = family.instance(seed)
    certificate = ExactPlacement(instance).solve()

    assert certificate.proved
    assert certificate.lower == instance.covered_weight(certificate.positions)
    axis = np.linspace(0.0, 100.0, 301)
    grid = np.stack(np.meshgrid(axis, axis), axis=-1).reshape(-1, 2)
    coverage = instance.covers(grid)
    kept = CoverProgram.maximal_rows(coverage)
    searched = CoverProgram(coverage[kept], instance.weights, instance.emitters)
    assert searched.solve().weight <= certificate.upper


def test_the_program_agrees_with_every_subset_on_a_small_choice() -> None:
    generator = np.random.default_rng(0)
    coverage = generator.random((12, 20)) < 0.3
    weights = generator.integers(1, 50, 20)

    solved = CoverProgram(coverage, weights, 3).solve()

    best = max(
        int(weights[coverage[list(subset)].any(axis=0)].sum())
        for subset in itertools.combinations(range(12), 3)
    )
    assert solved.weight == solved.bound == best


def test_the_scored_coverage_agrees_with_the_kernel_with_sharp_walls() -> None:
    instance = Family(60, 3, 8).instance(1)
    radius = instance.radius
    scene = Scene(
        points=jnp.asarray(instance.points),
        measure=jnp.ones(60),
        walls=jnp.asarray(instance.walls),
        bounds=jnp.array([100.0, 100.0]),
        grid=GridShape(1, 60),
    )
    physics = Physics(
        emitter=lambda distance: (distance <= radius).astype(distance.dtype),
        sensor=lambda signal: signal,
    )
    positions = np.random.default_rng(3).uniform(0.0, 100.0, (200, 2))

    kernel = np.asarray(
        Coverage(scene, HardOcclusion(), physics).sent(jnp.asarray(positions))
    )

    disagreeing = np.mean(kernel.T.astype(bool) != instance.covers(positions))
    assert disagreeing < 1e-3
