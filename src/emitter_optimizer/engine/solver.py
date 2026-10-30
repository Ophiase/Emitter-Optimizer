"""Gradient descent on the emitter positions."""

from collections.abc import Callable

import keras
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from matplotlib.figure import Figure

from emitter_optimizer.engine.collision_map import CollisionMap
from emitter_optimizer.engine.density_map import DensityMap
from emitter_optimizer.engine.field import Field, SignalFunction
from emitter_optimizer.engine.geometry import (
    SIGNAL_DTYPE,
    generate_points,
    make_grid,
    resize_map,
)

Positions = tf.Variable | tf.Tensor
UpdateCallback = Callable[[Positions | None, list[float] | None], None]
FIGURE_SIZE = (6, 4)


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
        emitter_function: SignalFunction,
        sensor_function: SignalFunction,
        n_iteration: int,
        epsilon: float,
        update_callback: UpdateCallback | None = None,
        update_rate: int = 200,
    ) -> None:
        self.n_emitters = n_emitters
        self.map_scale = map_scale
        self.grid_size = grid_size
        self.n_iteration = n_iteration
        self.epsilon = epsilon
        self.update_rate = update_rate
        self.update_callback = update_callback or _ignore_update

        self.is_working = False
        self.is_aborting = False
        self.history: list[float] = []

        self.density = (
            None if density_map is None else resize_map(density_map.data, grid_size)
        )
        obstacles = (
            None if collision_map is None else collision_map.to_world(map_scale).data
        )
        self.field = Field(
            grid=make_grid(grid_size, map_scale),
            map_scale=map_scale,
            grid_size=grid_size,
            density=_constant(self.density),
            obstacles=_constant(obstacles),
            emitter_function=emitter_function,
            sensor_function=sensor_function,
        )
        self.emitters_positions = generate_points(
            self.density,
            map_scale,
            n_emitters,
        )
        self.update_callback(None, None)

    def make_fig(
        self,
        emitters: Positions | None = None,
        figsize: tuple[float, float] = FIGURE_SIZE,
    ) -> Figure:
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

    def train(self) -> tuple[tf.Variable, list[float]]:
        positions = tf.Variable(tf.identity(self.emitters_positions), trainable=True)
        history = list(self.history)
        optimizer = keras.optimizers.Nadam(learning_rate=self.epsilon)

        for iteration in range(self.n_iteration):
            if self.is_aborting:
                self.is_aborting = False
                return positions, history

            with tf.GradientTape() as tape:
                loss = -self.field.gain(positions)
            gradients = tape.gradient(loss, positions)
            optimizer.apply_gradients([(gradients, positions)])
            history.append(float(loss))

            if iteration % self.update_rate == 0:
                self.update_callback(positions, history)

        return positions, history


def _constant(data: np.ndarray | None) -> tf.Tensor | None:
    if data is None:
        return None
    return tf.constant(data, dtype=SIGNAL_DTYPE)
