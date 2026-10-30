from dataclasses import dataclass

import cv2
import numpy as np

from emitter_optimizer.engine.map_type import MapType

CANNY_THRESHOLD = 300
CANNY_APERTURE = 3


@dataclass(eq=False)
class CollisionMap:
    """The segments that block a signal, as (start, end) points of the unit square."""

    data: np.ndarray
    storage_type: MapType = MapType.SEGMENTS

    @classmethod
    def from_data(
        cls,
        data: np.ndarray,
        data_format: MapType,
        storage_type: MapType,
    ) -> CollisionMap:
        match data_format, storage_type:
            case MapType.GRID, MapType.SEGMENTS:
                return cls(_segments_from_grid(data), storage_type)
            case MapType.SEGMENTS, MapType.SEGMENTS:
                return cls(data, storage_type)
            case _:
                message = f"cannot read a {data_format} map as {storage_type}"
                raise NotImplementedError(message)

    def to_world(self, world_shape: tuple[float, float]) -> CollisionMap:
        return CollisionMap(self.data * np.array(world_shape), self.storage_type)


def _segments_from_grid(image: np.ndarray) -> np.ndarray:
    gray = image if image.ndim == 2 else np.mean(image, axis=2)
    if np.issubdtype(gray.dtype, np.floating):
        gray = np.clip(gray, 0.0, 1.0) * 255.0
    edges = cv2.Canny(
        np.asarray(gray, dtype=np.uint8),
        CANNY_THRESHOLD,
        CANNY_THRESHOLD,
        apertureSize=CANNY_APERTURE,
    )
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    height, width = gray.shape
    if not contours:
        return np.empty((0, 2, 2), dtype=np.float32)
    return np.concatenate([
        _contour_to_segments(contour, width, height) for contour in contours
    ])


def _contour_to_segments(
    contour: np.ndarray,
    width: int,
    height: int,
) -> np.ndarray:
    points = contour.reshape(-1, 2) / np.array([width, height])
    following = np.roll(points, -1, axis=0)
    return np.stack([points, following], axis=1)
