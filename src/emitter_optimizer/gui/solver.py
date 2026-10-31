from collections.abc import Callable
from dataclasses import replace

import jax
import jax.numpy as jnp
import numpy as np

from emitter_optimizer.kernel import (
    Coverage,
    Descender,
    DescentSettings,
    HardOcclusion,
    Physics,
    Scene,
    Step,
)
from emitter_optimizer.render import MapImage

UpdateCallback = Callable[[np.ndarray | None, list[float] | None], None]
IMAGE_WIDTH = 600


def _ignore_update(*_: object) -> None:
    return None


class Solver:
    """Drive the JAX descender from the window, one reported step at a time."""

    def __init__(
        self,
        scene: Scene,
        physics: Physics,
        settings: DescentSettings,
        update_callback: UpdateCallback | None = None,
    ) -> None:
        self.scene = scene
        self.physics = physics
        self.settings = settings
        self.update_callback = update_callback or _ignore_update
        self.positions = self._sample()
        self.history: list[float] = []
        self.is_working = False
        self._descender: Descender | None = None

    def solve(self) -> None:
        if self.is_working:
            return
        self.is_working = True
        descender = Descender(
            self.scene,
            self.physics,
            self.settings,
            on_step=self._on_step,
            start=jnp.asarray(self.positions)[None],
        )
        self._descender = descender
        try:
            result = descender.run()
        finally:
            self.is_working = False
            self._descender = None
        self.positions = np.asarray(result.positions, dtype=np.float64)
        self.history = list(result.history)
        self.update_callback(self.positions, self.history)

    def abort(self) -> None:
        descender = self._descender
        if descender is not None:
            descender.stop()

    def figure(self) -> bytes:
        coverage = Coverage(self.scene, HardOcclusion(), self.physics)
        return MapImage(self.scene, coverage, width=IMAGE_WIDTH).png(self.positions)

    def set_iteration_count(self, count: int) -> None:
        self.settings = replace(self.settings, steps=count)

    def set_learning_rate(self, value: float) -> None:
        self.settings = replace(self.settings, step_size=value)

    def set_report_every(self, value: int) -> None:
        self.settings = replace(self.settings, report_every=value)

    def set_emitter_count(self, count: int) -> None:
        self.settings = replace(self.settings, emitters=count)
        self.positions = self._sample()

    def _sample(self) -> np.ndarray:
        key = jax.random.key(self.settings.seed)
        start = self.scene.sample(key, 1, self.settings.emitters)
        return np.asarray(start[0], dtype=np.float64)

    def _on_step(self, step: Step) -> None:
        self.positions = np.asarray(step.positions, dtype=np.float64)
        self.history.append(step.gain)
        self.update_callback(self.positions, self.history)
