"""Reading a map from a file: an image or a CSV of segments."""

from pathlib import Path

import cv2
import numpy as np

from emitter_optimizer.engine.maps.collision_map import CollisionMap
from emitter_optimizer.engine.maps.density_map import DensityMap
from emitter_optimizer.engine.maps.map_type import MapType

OPAQUE = 255.0


def load_density(path: Path) -> DensityMap:
    """A grayscale image, one weight in [0, 1] per cell."""
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        message = f"cannot read the density map: {path}"
        raise ValueError(message)
    return DensityMap.from_data(
        image.astype(np.float64) / OPAQUE,
        MapType.GRID,
        MapType.GRID,
    )


def load_collisions(path: Path) -> CollisionMap:
    """A mask turned into segments, or a CSV of normalized segments."""
    if path.suffix == ".csv":
        segments = np.loadtxt(path, delimiter=",", dtype=np.float64).reshape(-1, 2, 2)
        return CollisionMap.from_data(segments, MapType.SEGMENTS, MapType.SEGMENTS)

    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        message = f"cannot read the collision map: {path}"
        raise ValueError(message)
    return CollisionMap.from_data(image, MapType.GRID, MapType.SEGMENTS)
