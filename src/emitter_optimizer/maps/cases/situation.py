from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from emitter_optimizer.kernel import Extent, GridShape, Physics, Scene
from emitter_optimizer.service.options import (
    DEFAULT_SEED,
    DEFAULT_STEP_SIZE,
    MapOptions,
)


@dataclass(frozen=True, slots=True)
class Situation:
    """A photograph, its painted layers and its laws, read from one folder."""

    folder: Path
    description: str
    width: float
    columns: int
    emitters: int

    @property
    def name(self) -> str:
        return self.folder.name

    @property
    def source(self) -> Path:
        return self.folder / "source.jpg"

    @property
    def extent(self) -> Extent:
        columns, rows = Image.open(self.source).size
        return Extent(self.width, self.width * rows / columns)

    @property
    def grid(self) -> GridShape:
        extent = self.extent
        return GridShape(
            round(self.columns * extent.height / extent.width), self.columns
        )

    @property
    def options(self) -> MapOptions:
        return MapOptions(
            extent=self.extent,
            grid=self.grid,
            emitters=self.emitters,
            step_size=DEFAULT_STEP_SIZE,
            seed=DEFAULT_SEED,
            density_path=self.folder / "attraction.png",
            collisions_path=self.folder / "collision.png",
            emitter_law=self.folder / "emitter.py",
            sensor_law=self.folder / "sensor.py",
            walls_on_grid=True,
        )

    @property
    def physics(self) -> Physics:
        return self.options.physics()

    @property
    def scene(self) -> Scene:
        return self.options.scene()
