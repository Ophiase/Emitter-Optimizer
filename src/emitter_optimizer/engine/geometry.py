"""Conversions between the grid and the world, and the path a signal takes."""

from collections.abc import Sequence

import cv2
import numpy as np
import tensorflow as tf

SIGNAL_DTYPE = tf.float32
HALF_CELL = 0.5


def resize_map(image: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    return cv2.resize(image, size)


def point_to_grid(
    point: tf.Tensor,
    world_shape: tuple[float, float],
    grid_shape: tuple[int, int],
) -> tuple[tf.Tensor, tf.Tensor]:
    """The (row, column) cell of the grid that holds a world position."""
    rows, columns = grid_shape
    width, height = world_shape
    column = tf.cast(tf.floor(columns * point[0] / width), tf.int32)
    row = tf.cast(tf.floor(rows * point[1] / height), tf.int32)
    return row, column


def grid_to_world(
    cells: tf.Tensor,
    world_shape: tuple[float, float],
    grid_shape: tuple[int, int],
) -> tf.Tensor:
    """The world coordinates of grid cells written as (column, row)."""
    rows, columns = grid_shape
    width, height = world_shape
    scale = tf.constant([width / columns, height / rows], dtype=SIGNAL_DTYPE)
    return cells * scale


def make_grid(
    grid_shape: tuple[int, int],
    world_shape: tuple[float, float],
) -> tf.Tensor:
    """World coordinates of every cell, shaped (rows, columns, 2)."""
    rows, columns = grid_shape
    row_indices, column_indices = np.meshgrid(
        np.arange(rows),
        np.arange(columns),
        indexing="ij",
    )
    cells = np.stack([column_indices, row_indices], axis=-1).astype(np.float32)
    return grid_to_world(tf.constant(cells), world_shape, grid_shape)


def turn_is_clockwise(
    origin: tf.Tensor,
    first: tf.Tensor,
    second: tf.Tensor,
) -> tf.Tensor:
    return (second[1] - origin[1]) * (first[0] - origin[0]) > (first[1] - origin[1]) * (
        second[0] - origin[0]
    )


def segments_intersect(
    start: tf.Tensor,
    end: tf.Tensor,
    obstacle: tf.Tensor,
) -> tf.Tensor:
    """Whether the segment [start, end] crosses the segment obstacle."""
    obstacle_start, obstacle_end = obstacle[0], obstacle[1]
    return tf.logical_and(
        turn_is_clockwise(start, obstacle_start, obstacle_end)
        != turn_is_clockwise(end, obstacle_start, obstacle_end),
        turn_is_clockwise(start, end, obstacle_start)
        != turn_is_clockwise(start, end, obstacle_end),
    )


def is_blocked(
    start: tf.Tensor,
    end: tf.Tensor,
    obstacles: Sequence[tf.Tensor],
) -> tf.Tensor:
    blocked = tf.constant(False)
    for obstacle in obstacles:
        blocked = tf.logical_or(blocked, segments_intersect(start, end, obstacle))
    return blocked


def generate_points(
    density: np.ndarray | None,
    world_shape: tuple[float, float],
    count: int,
) -> tf.Tensor:
    """`count` points drawn from a density, or uniformly when it has none."""
    width, height = world_shape
    if density is None or not np.any(density):
        return tf.constant(
            np.random.uniform(size=(count, 2)) * np.array([width, height]),
            dtype=SIGNAL_DTYPE,
        )

    rows, columns = density.shape
    weights = (density / density.sum()).ravel()
    row_indices, column_indices = np.unravel_index(
        np.random.choice(weights.size, size=count, p=weights), density.shape
    )
    points = np.column_stack([
        (column_indices + HALF_CELL) * width / columns,
        (row_indices + HALF_CELL) * height / rows,
    ])
    return tf.constant(points, dtype=SIGNAL_DTYPE)
