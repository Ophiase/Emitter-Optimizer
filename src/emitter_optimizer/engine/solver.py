from collections.abc import Callable
from dataclasses import dataclass, replace

import numpy as np
from matplotlib.figure import Figure

from emitter_optimizer.engine.adam import Adam
from emitter_optimizer.engine.field import Field
from emitter_optimizer.engine.geometry import generate_points, make_grid, resize_map
from emitter_optimizer.engine.laws import Law, Positions
from emitter_optimizer.engine.maps import CollisionMap, DensityMap

UpdateCallback = Callable[[Positions | None, list[float] | None], None]
FIGURE_SIZE = (6, 4)


@dataclass(frozen=True)
class Problem:
    density_map: DensityMap | None
    collision_map: CollisionMap | None
    map_scale: tuple[float, float]
    grid_size: tuple[int, int]


@dataclass(frozen=True)
class SolverSettings:
    emitter_count: int
    iteration_count: int
    learning_rate: float
    report_every: int = 200
    seed: int = 0


@dataclass(frozen=True)
class TrainingResult:
    positions: Positions
    history: list[float]


def _ignore_update(*_: object) -> None:
    return None


class Solver:
    def __init__(
        self,
        problem: Problem,
        settings: SolverSettings,
        emitter_law: Law,
        sensor_law: Law,
        update_callback: UpdateCallback | None = None,
    ) -> None:
        self.problem = problem
        self.settings = settings
        self.update_callback = update_callback or _ignore_update
        self.seed = settings.seed
        self.generator = np.random.default_rng(settings.seed)
        self.is_working = False
        self.is_aborting = False
        self.history: list[float] = []

        self.density = (
            None
            if problem.density_map is None
            else resize_map(problem.density_map.data, problem.grid_size).astype(
                np.float64
            )
        )
        obstacles = (
            None
            if problem.collision_map is None
            else problem.collision_map.to_world(problem.map_scale).data.astype(
                np.float64
            )
        )
        self.field = Field(
            grid=make_grid(problem.grid_size, problem.map_scale),
            map_scale=problem.map_scale,
            grid_size=problem.grid_size,
            density=None if self.density is None else self.density.ravel(),
            obstacles=obstacles,
            emitter_law=emitter_law,
            sensor_law=sensor_law,
        )
        self.emitters_positions = generate_points(
            self.density,
            problem.map_scale,
            settings.emitter_count,
            self.generator,
        )
        self.update_callback(None, None)

    @property
    def map_scale(self) -> tuple[float, float]:
        return self.problem.map_scale

    @property
    def grid_size(self) -> tuple[int, int]:
        return self.problem.grid_size

    @property
    def emitter_count(self) -> int:
        return self.settings.emitter_count

    @property
    def iteration_count(self) -> int:
        return self.settings.iteration_count

    def set_iteration_count(self, count: int) -> None:
        self.settings = replace(self.settings, iteration_count=count)

    def set_learning_rate(self, value: float) -> None:
        self.settings = replace(self.settings, learning_rate=value)

    def set_report_every(self, value: int) -> None:
        self.settings = replace(self.settings, report_every=value)

    def make_fig(
        self,
        emitters: Positions | None = None,
        figure_size: tuple[float, float] = FIGURE_SIZE,
    ) -> Figure:
        positions = self.emitters_positions if emitters is None else emitters
        values = self.field.value_map(positions)
        figure = Figure(figsize=figure_size)
        axes = figure.add_subplot(1, 1, 1)
        axes.scatter(positions[:, 0], positions[:, 1])
        axes.set_xlim(0, self.problem.map_scale[0])
        axes.set_ylim(self.problem.map_scale[1], 0)
        axes.imshow(
            values,
            aspect="auto",
            origin="upper",
            extent=(
                0,
                self.problem.map_scale[0],
                self.problem.map_scale[1],
                0,
            ),
            cmap="plasma",
            vmin=-1,
            vmax=1,
        )
        axes.set_xlabel("X")
        axes.set_ylabel("Y")
        axes.set_title("Emitters positions")
        axes.grid(visible=True)
        return figure

    def solve(self) -> None:
        if self.is_working:
            return
        self.is_working = True
        result = self.train()
        self.is_working = False
        self.emitters_positions = result.positions
        self.history = result.history
        self.update_callback(result.positions, result.history)

    def abort(self) -> None:
        if not self.is_working or self.is_aborting:
            return
        self.is_aborting = True

    def train(self) -> TrainingResult:
        positions = np.array(self.emitters_positions, dtype=np.float64, copy=True)
        adam = Adam(
            self.settings.learning_rate,
            np.zeros_like(positions),
            np.zeros_like(positions),
        )
        best = positions.copy()
        best_gain = self.field.gain(positions)
        history = list(self.history)

        for iteration in range(1, self.settings.iteration_count + 1):
            if self.is_aborting:
                self.is_aborting = False
                break
            gain, gradient = self.field.gain_and_gradient(positions)
            if gain > best_gain:
                best, best_gain = positions.copy(), gain
            positions = np.clip(
                positions + adam.step(gradient),
                0.0,
                np.array(self.problem.map_scale),
            )
            history.append(-best_gain)
            if iteration % self.settings.report_every == 0:
                self.update_callback(positions, history)

        return TrainingResult(best, history)
