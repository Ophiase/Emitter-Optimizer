from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

from emitter_optimizer.kernel import GridShape

OPAQUE = 255.0


@dataclass(frozen=True, slots=True)
class Density:
    """One weight in [0, 1] per map cell, rows first."""

    values: np.ndarray

    def __post_init__(self) -> None:
        if self.values.ndim != 2:
            message = f"a density is a grid, not {self.values.shape}"
            raise ValueError(message)

    @classmethod
    def load(cls, path: Path) -> Density:
        image = Image.open(path).convert("L")
        return cls(np.asarray(image, dtype=np.float64) / OPAQUE)

    @classmethod
    def of(cls, values: np.ndarray) -> Density:
        return cls(np.asarray(values, dtype=np.float64))

    def resized(self, grid: GridShape) -> Density:
        image = Image.fromarray(
            np.clip(self.values * OPAQUE, 0, OPAQUE).astype(np.uint8), mode="L"
        )
        resized = image.resize((grid.columns, grid.rows), Image.Resampling.BOX)
        return Density(np.asarray(resized, dtype=np.float64) / OPAQUE)
