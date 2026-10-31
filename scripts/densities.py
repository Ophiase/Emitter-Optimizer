import numpy as np

from emitter_optimizer.maps import Density, Walls


def density_map(data: np.ndarray) -> Density:
    return Density.of(data)


def collision_map(
    *segments: tuple[tuple[float, float], tuple[float, float]],
) -> Walls:
    return Walls.of(*segments)


def crop_rows(shape: tuple[int, int]) -> np.ndarray:
    density = np.zeros(shape)
    density[::4, :] = 1.0
    density[1::4, :] = 0.7
    return density


def rooms(shape: tuple[int, int]) -> np.ndarray:
    rows, columns = shape
    density = np.ones(shape)
    density[rows // 2 - 1 : rows // 2 + 1, :] = 0.15
    density[:, columns // 2 - 1 : columns // 2 + 1] = 0.35
    return density


def peaks(
    shape: tuple[int, int],
    centres: tuple[tuple[float, float], ...],
    width: float = 0.12,
) -> np.ndarray:
    rows, columns = shape
    row_indices, column_indices = np.meshgrid(
        np.arange(rows),
        np.arange(columns),
        indexing="ij",
    )
    density = np.zeros(shape)
    for column, row in centres:
        density += np.exp(
            -(
                (column_indices / columns - column) ** 2
                + (row_indices / rows - row) ** 2
            )
            / (2.0 * width**2)
        )
    return density / density.max()
