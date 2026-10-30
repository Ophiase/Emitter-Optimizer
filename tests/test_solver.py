import importlib
import sys

import numpy as np

from emitter_optimizer.engine import CollisionMap, DensityMap, Law, MapType, Solver

MAP_SCALE = (10.0, 10.0)
GRID_SIZE = (8, 8)


def signal(distance: np.ndarray) -> np.ndarray:
    return np.exp(-distance)


def signal_slope(distance: np.ndarray) -> np.ndarray:
    return -np.exp(-distance)


def sensor(received: np.ndarray) -> np.ndarray:
    return received


def sensor_slope(received: np.ndarray) -> np.ndarray:
    return np.ones_like(received)


EMITTER_LAW = Law(signal, signal_slope)
SENSOR_LAW = Law(sensor, sensor_slope)


def make_solver(
    *,
    density_map: DensityMap | None = None,
    collision_map: CollisionMap | None = None,
    n_iteration: int = 15,
) -> Solver:
    return Solver(
        n_emitters=3,
        density_map=density_map,
        collision_map=collision_map,
        map_scale=MAP_SCALE,
        grid_size=GRID_SIZE,
        emitter_law=EMITTER_LAW,
        sensor_law=SENSOR_LAW,
        n_iteration=n_iteration,
        epsilon=0.1,
        seed=0,
    )


def test_the_gradient_matches_a_finite_difference() -> None:
    solver = make_solver()
    positions = solver.emitters_positions
    gradient = solver.field.gradient(positions)
    reference = np.zeros_like(positions)
    step = 1e-6
    for index in np.ndindex(positions.shape):
        forward = positions.copy()
        backward = positions.copy()
        forward[index] += step
        backward[index] -= step
        reference[index] = (
            solver.field.gain(forward) - solver.field.gain(backward)
        ) / (2.0 * step)

    np.testing.assert_allclose(gradient, reference, rtol=1e-5, atol=1e-7)


def test_training_maximizes_the_gain() -> None:
    solver = make_solver()
    before = solver.field.gain(solver.emitters_positions)

    positions, history = solver.train()

    assert solver.field.gain(positions) > before
    assert len(history) == solver.n_iteration


def test_a_density_map_weights_the_grid() -> None:
    density = np.ones((4, 4))
    density[0, :] = 0.0
    solver = make_solver(
        density_map=DensityMap.from_data(density, MapType.GRID, MapType.GRID)
    )

    values = solver.field.value_map(solver.emitters_positions)

    assert values.shape == GRID_SIZE
    assert values.min() >= 0.0
    np.testing.assert_allclose(values[0, :].max(), 0.0)


def test_a_wall_lowers_the_gain() -> None:
    wall = np.array([[[0.5, 0.0], [0.5, 1.0]]])
    clear = make_solver()
    walled = make_solver(
        collision_map=CollisionMap.from_data(
            wall,
            MapType.SEGMENTS,
            MapType.SEGMENTS,
        )
    )
    positions = np.array([[0.0, 5.0]])

    assert walled.field.gain(positions) < clear.field.gain(positions)


def test_solving_updates_the_positions_and_the_history() -> None:
    solver = make_solver(n_iteration=3)

    solver.solve()

    assert solver.history
    assert not solver.is_working


def test_the_engine_needs_neither_tensorflow_nor_a_window() -> None:
    importlib.import_module("emitter_optimizer.engine")

    assert "tensorflow" not in sys.modules
    assert "dearpygui" not in sys.modules
