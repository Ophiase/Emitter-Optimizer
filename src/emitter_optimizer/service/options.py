import argparse
from dataclasses import dataclass
from pathlib import Path

from emitter_optimizer.engine.laws import load_law_file
from emitter_optimizer.engine.maps import (
    CollisionMap,
    DensityMap,
    load_collisions,
    load_density,
)
from emitter_optimizer.engine.solver import Problem, Solver, SolverSettings
from emitter_optimizer.service.session import Session

DEFAULT_MAP_SCALE = (100.0, 100.0)
DEFAULT_GRID_SIZE = (32, 32)
DEFAULT_EMITTERS = 15
DEFAULT_RUN_ITERATIONS = 200
DEFAULT_LEARNING_RATE = 1.0
DEFAULT_SEED = 0


@dataclass(frozen=True)
class MapOptions:
    density: DensityMap | None
    collisions: CollisionMap | None
    map_scale: tuple[float, float]
    grid_size: tuple[int, int]
    emitters: int
    learning_rate: float
    seed: int
    emitter_law: Path
    sensor_law: Path

    @classmethod
    def from_arguments(cls, arguments: argparse.Namespace) -> MapOptions:
        return cls(
            density=None
            if arguments.density is None
            else load_density(arguments.density),
            collisions=(
                None
                if arguments.collisions is None
                else load_collisions(arguments.collisions)
            ),
            map_scale=(float(arguments.map_scale[0]), float(arguments.map_scale[1])),
            grid_size=(int(arguments.grid_size[0]), int(arguments.grid_size[1])),
            emitters=int(arguments.emitters),
            learning_rate=float(arguments.learning_rate),
            seed=int(arguments.seed),
            emitter_law=arguments.emitter_law,
            sensor_law=arguments.sensor_law,
        )

    def solver(self, iterations: int) -> Solver:
        return Solver(
            problem=Problem(
                density_map=self.density,
                collision_map=self.collisions,
                map_scale=self.map_scale,
                grid_size=self.grid_size,
            ),
            settings=SolverSettings(
                emitter_count=self.emitters,
                iteration_count=iterations,
                learning_rate=self.learning_rate,
                seed=self.seed,
            ),
            emitter_law=load_law_file(self.emitter_law),
            sensor_law=load_law_file(self.sensor_law),
        )

    def session(self) -> Session:
        return Session(
            map_scale=self.map_scale,
            grid_size=self.grid_size,
            density=self.density,
            collisions=self.collisions,
            emitters=self.emitters,
            learning_rate=self.learning_rate,
            seed=self.seed,
            emitter_law=self.emitter_law,
            sensor_law=self.sensor_law,
        )
