from __future__ import annotations

import threading
from functools import partial
from typing import Protocol

import jax
import jax.numpy as jnp
import optax
from jax import Array

from emitter_optimizer.kernel.coverage import Coverage
from emitter_optimizer.kernel.descent.progress import Progress
from emitter_optimizer.kernel.descent.result import DescentResult
from emitter_optimizer.kernel.descent.settings import DescentSettings
from emitter_optimizer.kernel.descent.step import Step
from emitter_optimizer.kernel.laws import Physics
from emitter_optimizer.kernel.occlusion import HardOcclusion, Occlusion, SoftOcclusion
from emitter_optimizer.kernel.domain.scene import Scene


FINAL_RATE_SHARE = 0.02


def _negative_gain(
    positions: Array,
    scene: Scene,
    occlusion: Occlusion,
    physics: Physics,
) -> Array:
    return -Coverage(scene, occlusion, physics).gain(positions)


def _sharpness(scene: Scene, settings: DescentSettings) -> Array:
    side = jnp.max(scene.bounds)
    first, last = 0.05, 0.001
    widths = side * first * (last / first) ** jnp.linspace(0.0, 1.0, settings.steps)
    return 1.0 / widths


def _rate(scene: Scene, settings: DescentSettings) -> optax.Schedule:
    """Wide early steps to travel, then small ones so the end settles."""
    rate = settings.step_size * float(jnp.max(scene.bounds))
    return optax.cosine_decay_schedule(rate, settings.steps, alpha=FINAL_RATE_SHARE)


class Descender:
    """Run `settings.starts` descents side by side; keep the best seen, sharp walls."""

    class StepCallback(Protocol):
        def __call__(self, step: Step, /) -> None: ...

    def __init__(
        self,
        scene: Scene,
        physics: Physics,
        settings: DescentSettings,
        on_step: Descender.StepCallback | None = None,
        start: Array | None = None,
    ) -> None:
        self.scene = scene
        self.physics = physics
        self.settings = settings
        self.on_step = on_step
        self.start = start
        self._stop = threading.Event()

    def stop(self) -> None:
        self._stop.set()

    def run(self) -> DescentResult:
        transform = self.settings.optimizer.to_optax(_rate(self.scene, self.settings))
        objective = jax.vmap(
            jax.value_and_grad(partial(_negative_gain, physics=self.physics)),
            in_axes=(0, None, None),
        )

        def one(
            progress: Progress, sharpness: Array, scene: Scene
        ) -> tuple[Progress, Array]:
            loss, gradient = objective(
                progress.positions, scene, SoftOcclusion(sharpness)
            )
            updates, state = transform.update(
                gradient, progress.state, progress.positions
            )
            moved = jnp.clip(
                jnp.asarray(optax.apply_updates(progress.positions, updates)),
                0.0,
                scene.bounds,
            )
            return Progress(moved, state), -loss

        @jax.jit
        def chunk(
            progress: Progress, sharpness: Array, scene: Scene
        ) -> tuple[Progress, Array]:
            return jax.lax.scan(partial(one, scene=scene), progress, sharpness)

        if self.start is None:
            key = jax.random.key(self.settings.seed)
            start = self.scene.sample(key, self.settings.starts, self.settings.emitters)
        else:
            start = jnp.asarray(self.start)
        progress = Progress(start, transform.init(start))
        physics = self.physics

        @jax.jit
        def sharp_gains(positions: Array, scene: Scene) -> Array:
            return jax.vmap(Coverage(scene, HardOcclusion(), physics).gain)(positions)

        best_positions = start
        best_gains = sharp_gains(start, self.scene)
        sharpness = _sharpness(self.scene, self.settings)
        history: list[float] = []
        for first in range(0, self.settings.steps, self.settings.report_every):
            progress, gains = chunk(
                progress,
                sharpness[first : first + self.settings.report_every],
                self.scene,
            )
            history.extend(jnp.max(gains, axis=1).tolist())
            reached = sharp_gains(progress.positions, self.scene)
            improved = reached > best_gains
            best_gains = jnp.where(improved, reached, best_gains)
            best_positions = jnp.where(
                improved[:, None, None], progress.positions, best_positions
            )
            if self.on_step is not None:
                best = int(jnp.argmax(gains[-1]))
                self.on_step(Step(len(history), history[-1], progress.positions[best]))
            if self._stop.is_set():
                break
        best = int(jnp.argmax(best_gains))
        return DescentResult(
            best_positions[best],
            float(best_gains[best]),
            tuple(history),
            tuple(best_gains.tolist()),
        )
