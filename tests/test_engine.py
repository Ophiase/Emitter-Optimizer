import subprocess
import sys

import numpy as np

from emitter_optimizer.engine import CollisionMap, DensityMap, Law, MapType, Solver
from emitter_optimizer.engine.geometry import (
    generate_points,
    grid_to_world,
    make_grid,
    visibility,
)

GRID_SHAPE = (2, 4)
WORLD_SHAPE = (8.0, 4.0)
MAP_SCALE = (10.0, 10.0)
SOLVER_GRID = (8, 8)


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
        grid_size=SOLVER_GRID,
        emitter_law=EMITTER_LAW,
        sensor_law=SENSOR_LAW,
        n_iteration=n_iteration,
        epsilon=0.1,
        seed=0,
    )


def test_the_grid_follows_the_width_and_the_height() -> None:
    grid = make_grid(GRID_SHAPE, WORLD_SHAPE)

    np.testing.assert_allclose(grid[1, 3], [6.0, 2.0])


def test_world_coordinates_are_the_cells_scaled() -> None:
    cells = np.array([[1.0, 1.0]])

    world = grid_to_world(cells, WORLD_SHAPE, GRID_SHAPE)

    np.testing.assert_allclose(world, [[2.0, 2.0]])


def test_a_segment_hides_what_lies_behind_it() -> None:
    cells = np.array([[0.0, 0.0], [2.0, 0.0]])
    emitters = np.array([[0.0, 2.0], [3.0, 2.0]])
    obstacles = np.array([[[-1.0, 1.0], [0.5, 1.0]]])

    mask = visibility(cells, emitters, obstacles)

    assert not mask[0, 0]
    assert mask[1, 0]
    assert mask[0, 1]
    assert mask[1, 1]


def test_generated_points_stay_on_the_map() -> None:
    density = np.zeros((4, 4))
    density[:, 0] = 1.0

    points = generate_points(density, WORLD_SHAPE, 32, np.random.default_rng(0))

    assert points.shape == (32, 2)
    assert points[:, 0].min() >= 0.0
    assert points[:, 0].max() < WORLD_SHAPE[0] / 2.0


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

    assert values.shape == SOLVER_GRID
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
    program = (
        "import sys, emitter_optimizer.engine; "
        "print('tensorflow' in sys.modules, 'dearpygui' in sys.modules)"
    )

    result = subprocess.run(
        [sys.executable, "-c", program],
        capture_output=True,
        text=True,
        check=True,
    )

    assert result.stdout.strip() == "False False"
