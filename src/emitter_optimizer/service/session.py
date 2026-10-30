"""The mutable state of one map: what the service answers about."""

import io
import threading
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from emitter_optimizer.engine.geometry import generate_points
from emitter_optimizer.engine.laws import load_law_file
from emitter_optimizer.engine.maps import CollisionMap, DensityMap
from emitter_optimizer.engine.solver import Solver
from emitter_optimizer.paths import (
    DEFAULT_EMITTER_FUNCTION,
    DEFAULT_SENSOR_FUNCTION,
)
from emitter_optimizer.service.models import (
    DEFAULT_ITERATIONS,
    PlaceRequest,
    RunRequest,
    State,
    StopResult,
)


@dataclass
class Session:
    """One map, its solver, and the emitters currently placed on it."""

    map_scale: tuple[float, float] = (100.0, 100.0)
    grid_size: tuple[int, int] = (32, 32)
    density: DensityMap | None = None
    collisions: CollisionMap | None = None
    emitters: int = 15
    epsilon: float = 1.0
    seed: int = 0
    emitter_law: Path = DEFAULT_EMITTER_FUNCTION
    sensor_law: Path = DEFAULT_SENSOR_FUNCTION
    positions: np.ndarray | None = None
    history: list[float] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    _solver: Solver | None = field(default=None, repr=False)

    def solver(self) -> Solver:
        if self._solver is None:
            self._solver = self._build()
        return self._solver

    def state(self) -> State:
        solver = self.solver()
        positions = (
            solver.emitters_positions if self.positions is None else self.positions
        )
        return State(
            map_scale=self.map_scale,
            grid_size=self.grid_size,
            emitters=self.emitters,
            positions=tuple(
                (float(point[0]), float(point[1]))
                for point in np.asarray(positions).tolist()
            ),
            gain=float(solver.field.gain(positions)),
            history=tuple(self.history),
            seed=self.seed,
            running=solver.is_working,
        )

    def place(self, request: PlaceRequest) -> State:
        with self._lock:
            if request.seed is not None:
                self.seed = request.seed
            if request.positions is not None:
                positions = np.asarray(request.positions, dtype=np.float64)
                self.emitters = int(positions.shape[0])
            elif request.emitters is not None:
                self.emitters = request.emitters

            self._solver = self._build()
            if request.positions is not None:
                self._solver.emitters_positions = positions
            self.positions = np.array(self._solver.emitters_positions, copy=True)
            self.history = []
            return self.state()

    def run(self, request: RunRequest) -> State:
        with self._lock:
            solver = self.solver()
            solver.n_iteration = request.iterations
            if request.seed is not None:
                self.seed = request.seed
                solver.emitters_positions = generate_points(
                    solver.density,
                    solver.map_scale,
                    solver.n_emitters,
                    np.random.default_rng(self.seed),
                )
            solver.solve()
            self.positions = np.array(solver.emitters_positions, copy=True)
            self.history = list(solver.history)
            return self.state()

    def stop(self) -> StopResult:
        solver = self._solver
        if solver is None or not solver.is_working:
            return StopResult(aborted=False)
        solver.abort()
        return StopResult(aborted=True)

    def figure(self) -> bytes:
        figure = self.solver().make_fig(self.positions)
        buffer = io.BytesIO()
        figure.savefig(buffer, format="png")
        return buffer.getvalue()

    def _build(self) -> Solver:
        return Solver(
            n_emitters=self.emitters,
            density_map=self.density,
            collision_map=self.collisions,
            map_scale=self.map_scale,
            grid_size=self.grid_size,
            emitter_law=load_law_file(self.emitter_law),
            sensor_law=load_law_file(self.sensor_law),
            n_iteration=DEFAULT_ITERATIONS,
            epsilon=self.epsilon,
            seed=self.seed,
        )
