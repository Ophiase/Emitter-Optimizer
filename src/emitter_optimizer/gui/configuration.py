from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

import jax.numpy as jnp
from jax import Array

from emitter_optimizer.gui.solver import Solver, UpdateCallback
from emitter_optimizer.kernel import (
    DescentSettings,
    Extent,
    GridShape,
    Law,
    Physics,
    Scene,
)
from emitter_optimizer.maps import Density, Walls
from emitter_optimizer.service.evaluated_law import EvaluatedLaw
from emitter_optimizer.service.paths import (
    DEFAULT_EMITTER_FUNCTION,
    DEFAULT_SAVE_PATH,
    DEFAULT_SENSOR_FUNCTION,
)

DEFAULT_ITERATIONS = 200
DEFAULT_LEARNING_RATE = 0.01
DEFAULT_EMITTERS = 15
DEFAULT_MAP_SCALE = (100.0, 100.0)
DEFAULT_GRID_SIZE = (32, 32)
DEFAULT_REPORT_EVERY = 5
ITEMS_TO_HIDE = (
    "user_defined_density",
    "user_defined_collisions",
    "user_defined_emitter",
    "user_defined_sensor",
    "loss",
)


def _default_emitter_law() -> Law:
    return EvaluatedLaw.from_file(DEFAULT_EMITTER_FUNCTION)


def _default_sensor_law() -> Law:
    return EvaluatedLaw.from_file(DEFAULT_SENSOR_FUNCTION)


@dataclass
class GuiConfig:
    iteration_count: int = DEFAULT_ITERATIONS
    learning_rate: float = DEFAULT_LEARNING_RATE
    emitter_count: int = DEFAULT_EMITTERS
    map_scale: tuple[float, float] = DEFAULT_MAP_SCALE
    grid_size: tuple[int, int] = DEFAULT_GRID_SIZE
    report_every: int = DEFAULT_REPORT_EVERY
    density: Density | None = None
    walls: Walls | None = None
    emitter_law: Law = field(default_factory=_default_emitter_law)
    sensor_law: Law = field(default_factory=_default_sensor_law)
    update_callback: UpdateCallback | None = None
    solver: Solver = field(init=False)

    DEFAULT_EMITTER_FUNCTION: ClassVar[Path] = DEFAULT_EMITTER_FUNCTION
    DEFAULT_SENSOR_FUNCTION: ClassVar[Path] = DEFAULT_SENSOR_FUNCTION
    SAVE_PATH: ClassVar[Path] = DEFAULT_SAVE_PATH
    ITEMS_TO_HIDE: ClassVar[tuple[str, ...]] = ITEMS_TO_HIDE

    def __post_init__(self) -> None:
        self.solver = self.to_solver()

    def scene(self) -> Scene:
        extent = Extent(*self.map_scale)
        grid = GridShape(*self.grid_size)
        density: Array | None = (
            None
            if self.density is None
            else jnp.asarray(self.density.resized(grid).values)
        )
        walls = None if self.walls is None else jnp.asarray(self.walls.to_world(extent))
        return Scene.of(extent, grid, density, walls)

    def physics(self) -> Physics:
        return Physics(emitter=self.emitter_law, sensor=self.sensor_law)

    def to_solver(self) -> Solver:
        return Solver(
            scene=self.scene(),
            physics=self.physics(),
            settings=DescentSettings(
                emitters=self.emitter_count,
                steps=self.iteration_count,
                step_size=self.learning_rate,
                report_every=self.report_every,
                seed=0,
            ),
            update_callback=self.update_callback,
        )

    def update_solver(self) -> None:
        self.solver = self.to_solver()
        if self.update_callback is not None:
            self.solver.update_callback = self.update_callback
