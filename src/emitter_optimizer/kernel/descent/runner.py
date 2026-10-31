import threading
from functools import partial

import jax
import jax.numpy as jnp
import optax
from jax import Array

from emitter_optimizer.kernel.coverage import Coverage
from emitter_optimizer.kernel.descent.progress import Progress
from emitter_optimizer.kernel.descent.result import DescentResult
from emitter_optimizer.kernel.descent.settings import DescentSettings
from emitter_optimizer.kernel.descent.step import Step
from emitter_optimizer.kernel.descent.step_callback import StepCallback
from emitter_optimizer.kernel.laws import Physics
from emitter_optimizer.kernel.occlusion import Occlusion, SoftOcclusion
from emitter_optimizer.kernel.scene import Scene


def _negative_gain(
    positions: Array,
    scene: Scene,
    occlusion: Occlusion,
    physics: Physics,
) -> Array:
    return -Coverage(scene, occlusion, physics).gain(positions)


def _transform(optimizer: str, rate: float) -> optax.GradientTransformation:
    match optimizer:
        case "adam":
            return optax.adam(rate)
        case "adamw":
            return optax.adamw(rate)
        case "nadam":
            return optax.nadam(rate)
        case "lion":
            return optax.lion(rate)
        case "sgd":
            return optax.sgd(rate, momentum=0.9, nesterov=True)
        case _:
            message = f"unknown optimizer: {optimizer}"
            raise ValueError(message)


def _sharpness(scene: Scene, settings: DescentSettings) -> Array:
    side = jnp.max(scene.bounds)
    first, last = 0.05, 0.001
    widths = side * first * (last / first) ** jnp.linspace(0.0, 1.0, settings.steps)
    return 1.0 / widths


def _sharp(scene: Scene) -> Occlusion:
    side = jnp.max(scene.bounds)
    return SoftOcclusion(1.0 / (side * 0.001))


def _settle(
    progress: Progress, scene: Scene, physics: Physics, history: list[float]
) -> DescentResult:
    def objective(positions: Array) -> Array:
        return Coverage(scene, _sharp(scene), physics).gain(positions)

    gains = jax.vmap(objective)(progress.positions)
    best = int(jnp.argmax(gains))
    return DescentResult(
        progress.positions[best],
        float(gains[best]),
        tuple(history),
        tuple(gains.tolist()),
    )


class Descender:
    """Run `settings.starts` descents side by side; keep the best, sharp walls."""

    def __init__(
        self,
        scene: Scene,
        physics: Physics,
        settings: DescentSettings,
        on_step: StepCallback | None = None,
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
        rate = self.settings.step_size * float(jnp.max(self.scene.bounds))
        transform = _transform(self.settings.optimizer, rate)
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
        sharpness = _sharpness(self.scene, self.settings)
        history: list[float] = []
        for first in range(0, self.settings.steps, self.settings.report_every):
            progress, gains = chunk(
                progress,
                sharpness[first : first + self.settings.report_every],
                self.scene,
            )
            history.extend(jnp.max(gains, axis=1).tolist())
            if self.on_step is not None:
                best = int(jnp.argmax(gains[-1]))
                self.on_step(Step(len(history), history[-1], progress.positions[best]))
            if self._stop.is_set():
                break
        return _settle(progress, self.scene, self.physics, history)
