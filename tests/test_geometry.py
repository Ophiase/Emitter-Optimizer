import numpy as np
import tensorflow as tf

from emitter_optimizer.engine.geometry import (
    generate_points,
    grid_to_world,
    make_grid,
    point_to_grid,
)

GRID_SIZE = (2, 4)
WORLD_SHAPE = (8.0, 4.0)


def test_the_grid_follows_the_width_and_the_height() -> None:
    grid = make_grid(GRID_SIZE, WORLD_SHAPE)

    np.testing.assert_allclose(grid[1, 3], [6.0, 2.0])


def test_a_world_point_maps_back_to_its_cell() -> None:
    row, column = point_to_grid(
        tf.constant([6.0, 2.0]),
        WORLD_SHAPE,
        GRID_SIZE,
    )

    np.testing.assert_array_equal(tf.stack([row, column]), [1, 3])


def test_world_coordinates_are_the_cells_scaled() -> None:
    cells = tf.constant([[1.0, 1.0]])

    world = grid_to_world(cells, WORLD_SHAPE, GRID_SIZE)

    np.testing.assert_allclose(world, [[2.0, 2.0]])


def test_generated_points_stay_on_the_map() -> None:
    density = np.zeros((4, 4))
    density[:, 0] = 1.0

    points = generate_points(density, WORLD_SHAPE, 32)

    assert points.shape == (32, 2)
    assert float(tf.reduce_min(points[:, 0])) >= 0.0
    assert float(tf.reduce_max(points[:, 0])) < WORLD_SHAPE[0] / 2.0
