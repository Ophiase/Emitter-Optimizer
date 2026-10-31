from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

from emitter_optimizer.engine.laws import Law, load_law_file
from emitter_optimizer.engine.maps import CollisionMap, DensityMap
from emitter_optimizer.engine.solver import (
    Problem,
    Solver,
    SolverSettings,
    UpdateCallback,
)
from emitter_optimizer.paths import (
    DEFAULT_EMITTER_FUNCTION,
    DEFAULT_SAVE_PATH,
    DEFAULT_SENSOR_FUNCTION,
)

DEFAULT_ITERATIONS = 200
DEFAULT_LEARNING_RATE = 1.0
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
    return load_law_file(DEFAULT_EMITTER_FUNCTION)


def _default_sensor_law() -> Law:
    return load_law_file(DEFAULT_SENSOR_FUNCTION)


@dataclass
class GuiConfig:
    iteration_count: int = DEFAULT_ITERATIONS
    learning_rate: float = DEFAULT_LEARNING_RATE
    emitter_count: int = DEFAULT_EMITTERS
    map_scale: tuple[float, float] = DEFAULT_MAP_SCALE
    grid_size: tuple[int, int] = DEFAULT_GRID_SIZE
    report_every: int = DEFAULT_REPORT_EVERY
    density_map: DensityMap | None = None
    collision_map: CollisionMap | None = None
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

    def to_solver(self) -> Solver:
        return Solver(
            problem=Problem(
                density_map=self.density_map,
                collision_map=self.collision_map,
                map_scale=self.map_scale,
                grid_size=self.grid_size,
            ),
            settings=SolverSettings(
                emitter_count=self.emitter_count,
                iteration_count=self.iteration_count,
                learning_rate=self.learning_rate,
                report_every=self.report_every,
                seed=0,
            ),
            emitter_law=self.emitter_law,
            sensor_law=self.sensor_law,
            update_callback=self.update_callback,
        )

    def update_solver(self) -> None:
        self.solver = self.to_solver()
