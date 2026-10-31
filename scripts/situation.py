from dataclasses import dataclass
from pathlib import Path

import jax.numpy as jnp
from PIL import Image

from emitter_optimizer.kernel import Extent, GridShape, Physics, Scene
from emitter_optimizer.maps import Density, Walls
from emitter_optimizer.service.evaluated_law import EvaluatedLaw


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
    def physics(self) -> Physics:
        return Physics(
            emitter=EvaluatedLaw.from_file(self.folder / "emitter.py"),
            sensor=EvaluatedLaw.from_file(self.folder / "sensor.py"),
        )

    @property
    def scene(self) -> Scene:
        density = Density.load(self.folder / "attraction.png").resized(self.grid)
        walls = Walls.load(self.folder / "collision.png", self.grid)
        return Scene.of(
            self.extent,
            self.grid,
            jnp.asarray(density.values),
            jnp.asarray(walls.to_world(self.extent)),
        )
