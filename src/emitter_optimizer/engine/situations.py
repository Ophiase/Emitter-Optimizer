import time
from dataclasses import dataclass

import numpy as np

from emitter_optimizer.engine.laws import load_law_file
from emitter_optimizer.engine.maps import CollisionMap, DensityMap, MapType
from emitter_optimizer.engine.solver import Solver
from emitter_optimizer.paths import (
    DEFAULT_EMITTER_FUNCTION,
    DEFAULT_SENSOR_FUNCTION,
)

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
        n_emitters=emitters,
        density_map=situation.density,
        collision_map=situation.collisions,
        map_scale=situation.map_scale,
        grid_size=situation.grid_size,
        emitter_law=load_law_file(DEFAULT_EMITTER_FUNCTION),
        sensor_law=load_law_file(DEFAULT_SENSOR_FUNCTION),
        n_iteration=iterations,
        epsilon=LEARNING_RATE,
        seed=seed,
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
            _density(_crop_rows((32, 64))),
            _walls(
                ((0.5, 0.0), (0.5, 0.4)),
                ((0.5, 0.6), (0.5, 1.0)),
            ),
            (100.0, 50.0),
            (32, 64),
        ),
        Situation(
            "building",
            "Two rooms and a corridor, walls between.",
            _density(_rooms((32, 32))),
            _walls(
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
            _density(
                _peaks(
                    (32, 32),
                    ((0.3, 0.3), (0.7, 0.6), (0.5, 0.82)),
                )
            ),
            None,
            (100.0, 100.0),
            (32, 32),
        ),
        Situation(
            "wide",
            "A map twice as wide as tall.",
            _density(_peaks((32, 64), ((0.25, 0.5), (0.75, 0.5)), width=0.2)),
            None,
            (100.0, 50.0),
            (32, 64),
        ),
    )


def _density(data: np.ndarray) -> DensityMap:
    return DensityMap.from_data(
        np.asarray(data, dtype=np.float64),
        MapType.GRID,
        MapType.GRID,
    )


def _walls(
    *segments: tuple[tuple[float, float], tuple[float, float]],
) -> CollisionMap:
    return CollisionMap.from_data(
        np.array(segments, dtype=np.float64),
        MapType.SEGMENTS,
        MapType.SEGMENTS,
    )


def _crop_rows(grid_size: tuple[int, int]) -> np.ndarray:
    density = np.zeros(grid_size)
    density[::4, :] = 1.0
    density[1::4, :] = 0.7
    return density


def _rooms(grid_size: tuple[int, int]) -> np.ndarray:
    rows, columns = grid_size
    density = np.ones(grid_size)
    density[rows // 2 - 1 : rows // 2 + 1, :] = 0.15
    density[:, columns // 2 - 1 : columns // 2 + 1] = 0.35
    return density


def _peaks(
    grid_size: tuple[int, int],
    centres: tuple[tuple[float, float], ...],
    width: float = 0.12,
) -> np.ndarray:
    rows, columns = grid_size
    row_indices, column_indices = np.meshgrid(
        np.arange(rows),
        np.arange(columns),
        indexing="ij",
    )
    density = np.zeros(grid_size)
    for column, row in centres:
        density += np.exp(
            -(
                (column_indices / columns - column) ** 2
                + (row_indices / rows - row) ** 2
            )
            / (2.0 * width**2)
        )
    return density / density.max()
