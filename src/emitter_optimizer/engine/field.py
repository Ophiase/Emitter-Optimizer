"""The gain over a map: density, obstacles and the two functions the user edits."""

from collections.abc import Callable
from dataclasses import dataclass

import tensorflow as tf

from emitter_optimizer.engine.geometry import (
    SIGNAL_DTYPE,
    is_blocked,
    point_to_grid,
)

SignalFunction = Callable[[tf.Tensor], tf.Tensor]


@dataclass(eq=False)
class Field:
    grid: tf.Tensor
    map_scale: tuple[float, float]
    grid_size: tuple[int, int]
    density: tf.Tensor | None
    obstacles: tf.Tensor | None
    emitter_function: SignalFunction
    sensor_function: SignalFunction

    @tf.function
    def path_is_blocked(self, start: tf.Tensor, end: tf.Tensor) -> tf.Tensor:
        if self.obstacles is None:
            return tf.constant(False)
        return is_blocked(start, end, tf.unstack(self.obstacles))

    @tf.function
    def sum_signals(
        self,
        position: tf.Tensor,
        emitter_positions: tf.Tensor,
    ) -> tf.Tensor:
        total = tf.constant(0.0, dtype=SIGNAL_DTYPE)
        for emitter in tf.unstack(emitter_positions):
            distance = tf.norm(emitter - position)
            signal = self.emitter_function(distance)
            blocked = self.path_is_blocked(emitter, position)
            total = tf.where(blocked, total, total + signal)
        return total

    @tf.function
    def density_at(self, position: tf.Tensor) -> tf.Tensor:
        if self.density is None:
            return tf.constant(1.0, dtype=SIGNAL_DTYPE)
        row, column = point_to_grid(position, self.map_scale, self.grid_size)
        return tf.gather_nd(self.density, tf.stack([row, column]))

    @tf.function
    def value_at(
        self,
        position: tf.Tensor,
        emitter_positions: tf.Tensor,
    ) -> tf.Tensor:
        signal = self.sum_signals(position, emitter_positions)
        return self.sensor_function(signal) * self.density_at(position)

    @tf.function
    def value_map(self, emitter_positions: tf.Tensor) -> tf.Tensor:
        """The value of every cell, for the preview."""
        positions = tf.reshape(self.grid, (-1, 2))
        values = tf.vectorized_map(
            lambda position: self.value_at(position, emitter_positions),
            positions,
        )
        return tf.reshape(values, tf.shape(self.grid)[:-1])

    @tf.function
    def gain(self, emitter_positions: tf.Tensor) -> tf.Tensor:
        return tf.reduce_mean(self.value_map(emitter_positions))
