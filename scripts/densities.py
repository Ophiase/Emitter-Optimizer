import numpy as np

from emitter_optimizer.engine.maps import CollisionMap, DensityMap, MapType


def density_map(data: np.ndarray) -> DensityMap:
    return DensityMap.from_data(
        np.asarray(data, dtype=np.float64),
        MapType.GRID,
        MapType.GRID,
    )


def collision_map(
    *segments: tuple[tuple[float, float], tuple[float, float]],
) -> CollisionMap:
    return CollisionMap.from_data(
        np.array(segments, dtype=np.float64),
        MapType.SEGMENTS,
        MapType.SEGMENTS,
    )


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
