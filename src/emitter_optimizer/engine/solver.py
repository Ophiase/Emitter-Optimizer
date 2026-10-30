"""Gradient descent on the emitter positions: Adam with a projection."""

from collections.abc import Callable

import numpy as np
from matplotlib.figure import Figure

from emitter_optimizer.engine.field import Field
from emitter_optimizer.engine.geometry import generate_points, make_grid, resize_map
from emitter_optimizer.engine.maps import CollisionMap, DensityMap
from emitter_optimizer.engine.types import Law, Positions

UpdateCallback = Callable[[Positions | None, list[float] | None], None]
FIGURE_SIZE = (6, 4)
ADAM_BETA1 = 0.9
ADAM_BETA2 = 0.999
ADAM_EPSILON = 1e-8


def _ignore_update(*_: object) -> None:
    return None


class Solver:
    """Maximize the gain of a set of emitters over a field."""

    def __init__(
        self,
        n_emitters: int,
        density_map: DensityMap | None,
        collision_map: CollisionMap | None,
        map_scale: tuple[float, float],
        grid_size: tuple[int, int],
        emitter_law: Law,
        sensor_law: Law,
        n_iteration: int,
        epsilon: float,
        update_callback: UpdateCallback | None = None,
        update_rate: int = 200,
        seed: int | None = None,
    ) -> None:
        self.n_emitters = n_emitters
        self.map_scale = map_scale
        self.grid_size = grid_size
        self.n_iteration = n_iteration
        self.epsilon = epsilon
        self.update_rate = update_rate
        self.update_callback = update_callback or _ignore_update
        self.generator = np.random.default_rng(seed)

        self.is_working = False
        self.is_aborting = False
        self.history: list[float] = []

        self.density = (
            None
            if density_map is None
            else resize_map(density_map.data, grid_size).astype(np.float64)
        )
        obstacles = (
            None
            if collision_map is None
            else collision_map.to_world(map_scale).data.astype(np.float64)
        )
        self.field = Field(
            grid=make_grid(grid_size, map_scale),
            map_scale=map_scale,
            grid_size=grid_size,
            density=None if self.density is None else self.density.ravel(),
            obstacles=obstacles,
            emitter_law=emitter_law,
            sensor_law=sensor_law,
        )
        self.emitters_positions = generate_points(
            self.density,
            map_scale,
            n_emitters,
            self.generator,
        )
        self.update_callback(None, None)

    def make_fig(
        self,
        emitters: Positions | None = None,
        figsize: tuple[float, float] = FIGURE_SIZE,
    ) -> Figure:
        import matplotlib.pyplot as plt

        positions = self.emitters_positions if emitters is None else emitters
        values = self.field.value_map(positions)
        figure, axes = plt.subplots(figsize=figsize)
        axes.scatter(positions[:, 0], positions[:, 1])
        axes.set_xlim(0, self.map_scale[0])
        axes.set_ylim(self.map_scale[1], 0)
        axes.imshow(
            values,
            aspect="auto",
            origin="upper",
            extent=(0, self.map_scale[0], self.map_scale[1], 0),
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
        positions, history = self.train()
        self.is_working = False
        self.emitters_positions = positions
        self.history = history
        self.update_callback(positions, history)

    def abort(self) -> None:
        if not self.is_working or self.is_aborting:
            return
        self.is_aborting = True

    def train(self) -> tuple[Positions, list[float]]:
        positions = np.array(self.emitters_positions, dtype=np.float64, copy=True)
        history = list(self.history)
        first = np.zeros_like(positions)
        second = np.zeros_like(positions)
        best = positions.copy()
        best_gain = self.field.gain(positions)

        for iteration in range(1, self.n_iteration + 1):
            if self.is_aborting:
                self.is_aborting = False
                break

            gain, gradient = self.field.gain_and_gradient(positions)
            if gain > best_gain:
                best_gain, best = gain, positions.copy()

            first = ADAM_BETA1 * first + (1.0 - ADAM_BETA1) * gradient
            second = ADAM_BETA2 * second + (1.0 - ADAM_BETA2) * gradient**2
            first_moment = first / (1.0 - ADAM_BETA1**iteration)
            second_moment = second / (1.0 - ADAM_BETA2**iteration)
            step = self.epsilon * first_moment / (np.sqrt(second_moment) + ADAM_EPSILON)
            positions = np.clip(positions + step, 0.0, np.array(self.map_scale))

            history.append(-best_gain)
            if iteration % self.update_rate == 0:
                self.update_callback(positions, history)

        return best, history
