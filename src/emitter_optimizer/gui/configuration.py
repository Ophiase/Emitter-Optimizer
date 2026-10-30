"""The parameters the window edits, and the solver built from them."""

from pathlib import Path
from typing import ClassVar

from emitter_optimizer.engine.laws import load_law
from emitter_optimizer.engine.maps import CollisionMap, DensityMap
from emitter_optimizer.engine.solver import Solver, UpdateCallback
from emitter_optimizer.engine.types import Law
from emitter_optimizer.paths import (
    DEFAULT_EMITTER_FUNCTION,
    DEFAULT_SAVE_PATH,
    DEFAULT_SENSOR_FUNCTION,
)

DEFAULT_ITERATIONS = 200
DEFAULT_LEARNING_STEP = 1.0
DEFAULT_EMITTERS = 15
DEFAULT_MAP_SCALE = (100.0, 100.0)
DEFAULT_GRID_SIZE = (32, 32)
DEFAULT_UPDATE_RATE = 5


class GuiConfig:
    DEFAULT_EMITTER_FUNCTION: ClassVar[Path] = DEFAULT_EMITTER_FUNCTION
    DEFAULT_SENSOR_FUNCTION: ClassVar[Path] = DEFAULT_SENSOR_FUNCTION
    DEFAULT_SAVE_PATH: ClassVar[Path] = DEFAULT_SAVE_PATH

    ITEMS_TO_HIDE: ClassVar[tuple[str, ...]] = (
        "user_defined_density",
        "user_defined_collisions",
        "user_defined_emitter",
        "user_defined_sensor",
        "loss",
    )

    def __init__(self, update_callback: UpdateCallback | None = None) -> None:
        self.n_iteration = DEFAULT_ITERATIONS
        self.learning_step = DEFAULT_LEARNING_STEP

        self.n_emitters = DEFAULT_EMITTERS
        self.density_map: DensityMap | None = None
        self.collision_map: CollisionMap | None = None

        self.map_scale = DEFAULT_MAP_SCALE
        self.grid_size = DEFAULT_GRID_SIZE

        self.emitter_function = self.load_function(
            self.load_file(self.DEFAULT_EMITTER_FUNCTION)
        )
        self.sensor_function = self.load_function(
            self.load_file(self.DEFAULT_SENSOR_FUNCTION)
        )

        self.update_callback = update_callback
        self.update_rate = DEFAULT_UPDATE_RATE

        self.update_solver()

    @staticmethod
    def load_file(path: Path) -> str:
        return path.read_text(encoding="utf-8")

    @staticmethod
    def load_function(source: str) -> Law:
        return load_law(source)

    def update_solver(self) -> None:
        self.solver = self.to_solver()

    def to_solver(self) -> Solver:
        return Solver(
            n_emitters=self.n_emitters,
            density_map=self.density_map,
            collision_map=self.collision_map,
            map_scale=self.map_scale,
            grid_size=self.grid_size,
            emitter_law=self.emitter_function,
            sensor_law=self.sensor_function,
            n_iteration=self.n_iteration,
            epsilon=self.learning_step,
            update_callback=self.update_callback,
            update_rate=self.update_rate,
        )
