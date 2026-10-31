from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image
from skimage.measure import find_contours

from emitter_optimizer.kernel import Extent, GridShape

WALL_LEVEL = 128
WALL_SHARE = 0.25


@dataclass(frozen=True, slots=True)
class Walls:
    """Wall segments in normalized map coordinates, `(segments, 2, 2)`."""

    segments: np.ndarray

    def __post_init__(self) -> None:
        if self.segments.ndim != 3 or self.segments.shape[1:] != (2, 2):
            message = f"walls are (segments, 2, 2), not {self.segments.shape}"
            raise ValueError(message)

    @classmethod
    def load(cls, path: Path, grid: GridShape | None = None) -> Walls:
        """Read a CSV of segments or a mask; a grid traces the mask cell by cell."""
        if path.suffix == ".csv":
            data = np.loadtxt(path, delimiter=",", ndmin=2)
            return cls(np.asarray(data, dtype=np.float64).reshape(-1, 2, 2))
        image = Image.open(path).convert("L")
        mask = np.asarray(image) < WALL_LEVEL
        if grid is not None:
            shares = Image.fromarray(mask.astype(np.float32)).resize(
                (grid.columns, grid.rows), Image.Resampling.BOX
            )
            mask = np.asarray(shares) >= WALL_SHARE
        height, width = mask.shape
        contours = find_contours(mask.astype(np.float64), 0.5)
        parts = [
            cls._segments(contour, width, height)
            for contour in contours
            if len(contour) > 1
        ]
        if not parts:
            return cls(np.empty((0, 2, 2), dtype=np.float64))
        return cls(np.concatenate(parts))

    @classmethod
    def of(cls, *segments: tuple[tuple[float, float], tuple[float, float]]) -> Walls:
        return cls(np.asarray(segments, dtype=np.float64))

    def to_world(self, extent: Extent) -> np.ndarray:
        return self.segments * np.array([extent.width, extent.height])

    @classmethod
    def _segments(cls, contour: np.ndarray, width: int, height: int) -> np.ndarray:
        points = np.stack(
            [(contour[:, 1] + 0.5) / width, (contour[:, 0] + 0.5) / height], axis=1
        )
        following = np.roll(points, -1, axis=0)
        return np.stack([points, following], axis=1)
