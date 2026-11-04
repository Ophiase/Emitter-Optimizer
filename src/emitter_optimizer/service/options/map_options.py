import argparse
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Self

import jax.numpy as jnp

from emitter_optimizer.kernel import Extent, GridShape, Physics, Scene
from emitter_optimizer.maps import Density, Walls
from emitter_optimizer.service.evaluated_law import EvaluatedLaw
from emitter_optimizer.service.paths import (
    DEFAULT_EMITTER_FUNCTION,
    DEFAULT_SENSOR_FUNCTION,
)
from emitter_optimizer.service.session import Session

DEFAULT_MAP_SCALE = (100.0, 100.0)
DEFAULT_GRID_SIZE = (32, 32)
DEFAULT_EMITTERS = 15
DEFAULT_RUN_ITERATIONS = 200
DEFAULT_STEP_SIZE = 0.01
DEFAULT_SEED = 0
FIELD_OF_FLAG = {
    "emitters": "emitters",
    "step_size": "step_size",
    "seed": "seed",
    "density": "density_path",
    "collisions": "collisions_path",
    "emitter_law": "emitter_law",
    "sensor_law": "sensor_law",
}


@dataclass(frozen=True, slots=True)
class MapOptions:
    extent: Extent
    grid: GridShape
    emitters: int
    step_size: float
    seed: int
    density_path: Path | None
    collisions_path: Path | None
    emitter_law: Path
    sensor_law: Path
    walls_on_grid: bool = False

    @classmethod
    def standard(cls) -> Self:
        return cls(
            extent=Extent(*DEFAULT_MAP_SCALE),
            grid=GridShape(*DEFAULT_GRID_SIZE),
            emitters=DEFAULT_EMITTERS,
            step_size=DEFAULT_STEP_SIZE,
            seed=DEFAULT_SEED,
            density_path=None,
            collisions_path=None,
            emitter_law=DEFAULT_EMITTER_FUNCTION,
            sensor_law=DEFAULT_SENSOR_FUNCTION,
        )

    def overridden_by(self, arguments: argparse.Namespace) -> Self:
        """Keep these options except where a flag was given; an absent flag is None."""
        given = {
            field: getattr(arguments, flag)
            for flag, field in FIELD_OF_FLAG.items()
            if getattr(arguments, flag) is not None
        }
        if arguments.map_scale is not None:
            given["extent"] = Extent(*arguments.map_scale)
        if arguments.grid_size is not None:
            given["grid"] = GridShape(*arguments.grid_size)
        return replace(self, **given)

    def density(self) -> Density | None:
        return None if self.density_path is None else Density.load(self.density_path)

    def walls(self) -> Walls | None:
        if self.collisions_path is None:
            return None
        grid = self.grid if self.walls_on_grid else None
        return Walls.load(self.collisions_path, grid)

    def scene(self) -> Scene:
        density = self.density()
        walls = self.walls()
        return Scene.of(
            self.extent,
            self.grid,
            None if density is None else jnp.asarray(density.resized(self.grid).values),
            None if walls is None else jnp.asarray(walls.to_world(self.extent)),
        )

    def physics(self) -> Physics:
        return Physics(
            emitter=EvaluatedLaw.from_file(self.emitter_law),
            sensor=EvaluatedLaw.from_file(self.sensor_law),
        )

    def session(self) -> Session:
        return Session(
            scene=self.scene(),
            physics=self.physics(),
            emitters=self.emitters,
            step_size=self.step_size,
            seed=self.seed,
        )
