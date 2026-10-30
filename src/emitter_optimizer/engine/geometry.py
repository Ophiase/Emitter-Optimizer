import cv2
import numpy as np

from emitter_optimizer.engine.laws import FloatArray, Positions

HALF_CELL = 0.5


def resize_map(image: FloatArray, size: tuple[int, int]) -> FloatArray:
    return np.asarray(cv2.resize(image, size), dtype=np.float64)


def grid_to_world(
    cells: FloatArray,
    world_shape: tuple[float, float],
    grid_shape: tuple[int, int],
) -> FloatArray:
    """The world coordinates of grid cells written as (column, row)."""
    rows, columns = grid_shape
    width, height = world_shape
    return cells * np.array([width / columns, height / rows])


def make_grid(
    grid_shape: tuple[int, int],
    world_shape: tuple[float, float],
) -> FloatArray:
    """World coordinates of every cell, shaped (rows, columns, 2)."""
    rows, columns = grid_shape
    row_indices, column_indices = np.meshgrid(
        np.arange(rows),
        np.arange(columns),
        indexing="ij",
    )
    cells = np.stack([column_indices, row_indices], axis=-1).astype(np.float64)
    return grid_to_world(cells, world_shape, grid_shape)


def turn(origin: FloatArray, first: FloatArray, second: FloatArray) -> FloatArray:
    return (second[..., 1] - origin[..., 1]) * (first[..., 0] - origin[..., 0]) - (
        first[..., 1] - origin[..., 1]
    ) * (second[..., 0] - origin[..., 0])


def crosses(start: FloatArray, end: FloatArray, obstacle: FloatArray) -> FloatArray:
    """Whether the segment [start, end] crosses the segment `obstacle`."""
    obstacle_start, obstacle_end = obstacle[0], obstacle[1]
    return (
        (turn(start, obstacle_start, obstacle_end) > 0)
        != (turn(end, obstacle_start, obstacle_end) > 0)
    ) & ((turn(start, end, obstacle_start) > 0) != (turn(start, end, obstacle_end) > 0))


def visibility(
    cells: FloatArray,
    emitters: Positions,
    obstacles: FloatArray | None,
) -> FloatArray:
    """True where the segment from a cell to an emitter crosses no obstacle."""
    start = cells[:, None, :]
    end = emitters[None, :, :]
    shape = (len(cells), len(emitters))
    if obstacles is None or len(obstacles) == 0:
        return np.ones(shape, dtype=bool)
    blocked = np.zeros(shape, dtype=bool)
    for obstacle in obstacles:
        blocked |= crosses(start, end, obstacle)
    return ~blocked


def generate_points(
    density: FloatArray | None,
    world_shape: tuple[float, float],
    count: int,
    generator: np.random.Generator,
) -> Positions:
    """`count` points drawn from a density, or uniformly when it has none."""
    width, height = world_shape
    if density is None or not np.any(density):
        return generator.uniform(size=(count, 2)) * np.array([width, height])

    rows, columns = density.shape
    weights = (density / density.sum()).ravel()
    row_indices, column_indices = np.unravel_index(
        generator.choice(weights.size, size=count, p=weights),
        density.shape,
    )
    return np.column_stack([
        (column_indices + HALF_CELL) * width / columns,
        (row_indices + HALF_CELL) * height / rows,
    ])
