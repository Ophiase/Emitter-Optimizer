import numpy as np

from emitter_optimizer.engine.geometry import (
    generate_points,
    grid_to_world,
    make_grid,
    visibility,
)

GRID_SIZE = (2, 4)
WORLD_SHAPE = (8.0, 4.0)


def test_the_grid_follows_the_width_and_the_height() -> None:
    grid = make_grid(GRID_SIZE, WORLD_SHAPE)

    np.testing.assert_allclose(grid[1, 3], [6.0, 2.0])


def test_world_coordinates_are_the_cells_scaled() -> None:
    cells = np.array([[1.0, 1.0]])

    world = grid_to_world(cells, WORLD_SHAPE, GRID_SIZE)

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
