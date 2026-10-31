import argparse
from dataclasses import dataclass
from pathlib import Path

import jax.numpy as jnp

from emitter_optimizer.kernel import Extent, GridShape, Physics, Scene
from emitter_optimizer.maps import Density, Walls
from emitter_optimizer.service.evaluated_law import EvaluatedLaw
from emitter_optimizer.service.session import Session

DEFAULT_MAP_SCALE = (100.0, 100.0)
DEFAULT_GRID_SIZE = (32, 32)
DEFAULT_EMITTERS = 15
DEFAULT_RUN_ITERATIONS = 200
DEFAULT_STEP_SIZE = 0.01
DEFAULT_SEED = 0


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

    @classmethod
    def from_arguments(cls, arguments: argparse.Namespace) -> MapOptions:
        return cls(
            extent=Extent(float(arguments.map_scale[0]), float(arguments.map_scale[1])),
            grid=GridShape(int(arguments.grid_size[0]), int(arguments.grid_size[1])),
            emitters=int(arguments.emitters),
            step_size=float(arguments.step_size),
            seed=int(arguments.seed),
            density_path=arguments.density,
            collisions_path=arguments.collisions,
            emitter_law=arguments.emitter_law,
            sensor_law=arguments.sensor_law,
        )

    def scene(self) -> Scene:
        density = (
            None
            if self.density_path is None
            else Density.load(self.density_path).resized(self.grid).values
        )
        walls = (
            None
            if self.collisions_path is None
            else Walls.load(self.collisions_path).to_world(self.extent)
        )
        return Scene.of(
            self.extent,
            self.grid,
            None if density is None else jnp.asarray(density),
            None if walls is None else jnp.asarray(walls),
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
