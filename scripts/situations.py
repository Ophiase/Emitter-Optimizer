import time
from dataclasses import dataclass

from emitter_optimizer.engine.laws import load_law_file
from emitter_optimizer.engine.maps import CollisionMap, DensityMap
from emitter_optimizer.engine.solver import Problem, Solver, SolverSettings
from emitter_optimizer.paths import (
    DEFAULT_EMITTER_FUNCTION,
    DEFAULT_SENSOR_FUNCTION,
)
from scripts.densities import collision_map, crop_rows, density_map, peaks, rooms

ITERATIONS = 60
EMITTERS = 15
SEED = 0
LEARNING_RATE = 1.0


@dataclass(frozen=True)
class Situation:
    name: str
    description: str
    density: DensityMap | None
    collisions: CollisionMap | None
    map_scale: tuple[float, float]
    grid_size: tuple[int, int]

    @property
    def cells(self) -> int:
        return self.grid_size[0] * self.grid_size[1]


@dataclass(frozen=True)
class Result:
    situation: Situation
    solver: Solver
    initial_gain: float
    gain: float
    seconds: float

    @property
    def improvement(self) -> float:
        return self.gain - self.initial_gain


def solver_for(
    situation: Situation,
    *,
    iterations: int = ITERATIONS,
    emitters: int = EMITTERS,
    seed: int = SEED,
) -> Solver:
    return Solver(
        problem=Problem(
            density_map=situation.density,
            collision_map=situation.collisions,
            map_scale=situation.map_scale,
            grid_size=situation.grid_size,
        ),
        settings=SolverSettings(
            emitter_count=emitters,
            iteration_count=iterations,
            learning_rate=LEARNING_RATE,
            seed=seed,
        ),
        emitter_law=load_law_file(DEFAULT_EMITTER_FUNCTION),
        sensor_law=load_law_file(DEFAULT_SENSOR_FUNCTION),
    )


def measure(
    situation: Situation,
    *,
    iterations: int = ITERATIONS,
    emitters: int = EMITTERS,
    seed: int = SEED,
) -> Result:
    solver = solver_for(
        situation,
        iterations=iterations,
        emitters=emitters,
        seed=seed,
    )
    initial_gain = solver.field.gain(solver.emitters_positions)
    started = time.perf_counter()
    solver.solve()
    seconds = time.perf_counter() - started
    gain = solver.field.gain(solver.emitters_positions)
    return Result(situation, solver, initial_gain, gain, seconds)


def situations() -> tuple[Situation, ...]:
    return (
        Situation(
            "uniform",
            "No density, no walls: the emitters spread out.",
            None,
            None,
            (100.0, 100.0),
            (32, 32),
        ),
        Situation(
            "farm",
            "Rows of crops, a hedge with a gate.",
            density_map(crop_rows((32, 64))),
            collision_map(((0.5, 0.0), (0.5, 0.4)), ((0.5, 0.6), (0.5, 1.0))),
            (100.0, 50.0),
            (32, 64),
        ),
        Situation(
            "building",
            "Two rooms and a corridor, walls between.",
            density_map(rooms((32, 32))),
            collision_map(
                ((0.5, 0.0), (0.5, 0.45)),
                ((0.5, 0.55), (0.5, 1.0)),
                ((0.0, 0.5), (0.35, 0.5)),
            ),
            (60.0, 40.0),
            (32, 32),
        ),
        Situation(
            "shop",
            "Three demand peaks in a town centre.",
            density_map(peaks((32, 32), ((0.3, 0.3), (0.7, 0.6), (0.5, 0.82)))),
            None,
            (100.0, 100.0),
            (32, 32),
        ),
        Situation(
            "wide",
            "A map twice as wide as tall.",
            density_map(peaks((32, 64), ((0.25, 0.5), (0.75, 0.5)), width=0.2)),
            None,
            (100.0, 50.0),
            (32, 64),
        ),
    )
