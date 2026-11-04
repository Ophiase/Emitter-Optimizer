import jax
import jax.numpy as jnp
import numpy as np
import pytest

from emitter_optimizer.kernel import (
    Coverage,
    Descender,
    DescentSettings,
    Greedy,
    HardOcclusion,
    Physics,
    Sphere,
    Torus,
)

CONCENTRATION = 6.0
THOMSON = Physics(
    emitter=lambda angle: jnp.exp(CONCENTRATION * (jnp.cos(angle) - 1.0)),
    sensor=lambda signal: 1.0 - (1.0 - signal) ** 2,
)


def smallest_angle(positions: jax.Array) -> float:
    units = np.asarray(positions)
    units = units / np.linalg.norm(units, axis=1, keepdims=True)
    cosines = units @ units.T
    np.fill_diagonal(cosines, -1.0)
    return float(np.degrees(np.arccos(np.clip(cosines.max(), -1.0, 1.0))))


@pytest.mark.parametrize(
    ("emitters", "expected"),
    [(4, 109.47), (6, 90.0), (12, 63.43)],
    ids=["tetrahedron", "octahedron", "icosahedron"],
)
def test_the_sphere_finds_the_regular_polyhedron(
    emitters: int, expected: float
) -> None:
    sphere = Sphere.of(32, 64)
    settings = DescentSettings(
        emitters=emitters, steps=400, starts=6, step_size=0.02, report_every=50
    )

    result = Descender(sphere, THOMSON, settings).run()

    assert smallest_angle(result.positions) == pytest.approx(expected, abs=2.5)


def test_a_rotation_of_the_sphere_keeps_the_distance() -> None:
    sphere = Sphere.of(8, 16)
    north = jnp.array([[0.0, 0.0, 1.0]])

    angles = sphere.signal(lambda angle: angle, north)

    expected = jnp.arccos(sphere.points[:, 2])
    assert jnp.allclose(angles[:, 0], expected, atol=1e-2)


def test_the_torus_wraps_the_distance() -> None:
    torus = Torus.of((10.0, 10.0), (10, 10))
    across = jnp.array([[9.9, 0.5]])

    distances = torus.signal(lambda distance: distance, across)

    assert float(distances[0, 0]) == pytest.approx(0.6, abs=1e-2)


def test_the_lattice_sum_converges_as_the_reach_grows() -> None:
    def law(distance: jax.Array) -> jax.Array:
        return jnp.exp(-distance / 3.0)

    def signal(reach: int) -> jax.Array:
        torus = Torus.of((10.0, 10.0), (8, 8), reach=reach)
        return torus.signal(law, jnp.array([[2.0, 3.0]]))

    errors = [float(jnp.max(jnp.abs(signal(r) - signal(6)))) for r in (0, 1, 2, 4)]

    assert errors == sorted(errors, reverse=True)
    assert errors[-1] < 1e-2 * errors[0]


def test_two_emitters_on_a_torus_sit_half_a_cell_apart() -> None:
    torus = Torus.of((10.0, 10.0), (24, 24))
    physics = Physics(
        emitter=lambda distance: jnp.exp(-((distance / 2.0) ** 2)),
        sensor=lambda signal: 1.0 - (1.0 - signal) ** 2,
    )
    settings = DescentSettings(emitters=2, steps=300, starts=4, report_every=50)

    positions = Descender(torus, physics, settings).run().positions

    offset = jnp.abs(positions[0] - positions[1])
    wrapped = jnp.minimum(offset, 10.0 - offset)
    assert float(jnp.linalg.norm(wrapped)) == pytest.approx(50.0**0.5, abs=0.6)


def test_greedy_works_on_any_domain() -> None:
    sphere = Sphere.of(12, 24)
    coverage = Coverage(sphere, HardOcclusion(), THOMSON)

    positions = Greedy(sphere, THOMSON).place(4)

    assert positions.shape == (4, 3)
    assert float(coverage.gain(positions)) > 0.0
