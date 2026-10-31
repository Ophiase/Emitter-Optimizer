import threading
from collections.abc import Callable, Mapping
from functools import cache, partial

import jax
import jax.numpy as jnp
import optax
from jax import Array

from emitter_optimizer.kernel.coverage import coverage, gain
from emitter_optimizer.kernel.descent.progress import Progress
from emitter_optimizer.kernel.descent.result import Descent
from emitter_optimizer.kernel.descent.settings import DescentSettings
from emitter_optimizer.kernel.descent.step import Step
from emitter_optimizer.kernel.laws import Physics
from emitter_optimizer.kernel.occlusion import Occlusion, SoftOcclusion
from emitter_optimizer.kernel.scene import Scene

OPTIMIZERS: Mapping[str, Callable[[float], optax.GradientTransformation]] = {
    "adam": optax.adam,
    "adamw": optax.adamw,
    "nadam": optax.nadam,
    "lion": optax.lion,
    "sgd": partial(optax.sgd, momentum=0.9, nesterov=True),
}


def _negative_gain(
    positions: Array,
    scene: Scene,
    occlusion: Occlusion,
    physics: Physics,
) -> Array:
    return -jnp.mean(coverage(positions, scene, occlusion, physics))


@cache
def _chunk_runner(
    physics: Physics, optimizer: str, rate: float
) -> Callable[..., tuple[Progress, Array]]:
    transform = _transform(optimizer, rate)
    objective = jax.vmap(
        jax.value_and_grad(partial(_negative_gain, physics=physics)),
        in_axes=(0, None, None),
    )

    def one(
        progress: Progress,
        sharpness: Array,
        scene: Scene,
    ) -> tuple[Progress, Array]:
        loss, gradient = objective(progress.positions, scene, SoftOcclusion(sharpness))
        updates, state = transform.update(gradient, progress.state, progress.positions)
        moved = jnp.clip(
            jnp.asarray(optax.apply_updates(progress.positions, updates)),
            0.0,
            scene.bounds,
        )
        return Progress(moved, state), -loss

    @jax.jit
    def run(
        progress: Progress, sharpness: Array, scene: Scene
    ) -> tuple[Progress, Array]:
        return jax.lax.scan(partial(one, scene=scene), progress, sharpness)

    return run


@cache
def _transform(optimizer: str, rate: float) -> optax.GradientTransformation:
    return OPTIMIZERS[optimizer](rate)


def _sharpness(scene: Scene, settings: DescentSettings) -> Array:
    side = jnp.max(scene.bounds)
    first, last = 0.05, 0.001
    widths = side * first * (last / first) ** jnp.linspace(0.0, 1.0, settings.steps)
    return 1.0 / widths


def _settle(
    progress: Progress, scene: Scene, physics: Physics, history: list[float]
) -> Descent:
    gains = jax.vmap(gain, in_axes=(0, None, None, None))(
        progress.positions, scene, _sharp(scene), physics
    )
    best = int(jnp.argmax(gains))
    return Descent(
        progress.positions[best],
        float(gains[best]),
        tuple(history),
        tuple(gains.tolist()),
    )


def _sharp(scene: Scene) -> Occlusion:
    side = jnp.max(scene.bounds)
    return SoftOcclusion(1.0 / (side * 0.001))


def descend(
    scene: Scene,
    physics: Physics,
    settings: DescentSettings,
    stop: threading.Event | None = None,
    on_step: Callable[[Step], None] | None = None,
) -> Descent:
    """Run `settings.starts` descents side by side; keep the best, sharp walls."""
    rate = settings.step_size * float(jnp.max(scene.bounds))
    transform = _transform(settings.optimizer, rate)
    run = _chunk_runner(physics, settings.optimizer, rate)
    key = jax.random.key(settings.seed)
    start = scene.sample(key, settings.starts, settings.emitters)
    progress = Progress(start, transform.init(start))
    sharpness = _sharpness(scene, settings)
    history: list[float] = []
    for first in range(0, settings.steps, settings.report_every):
        progress, gains = run(
            progress, sharpness[first : first + settings.report_every], scene
        )
        history.extend(jnp.max(gains, axis=1).tolist())
        if on_step is not None:
            best = int(jnp.argmax(gains[-1]))
            on_step(Step(len(history), history[-1], progress.positions[best]))
        if stop is not None and stop.is_set():
            break
    return _settle(progress, scene, physics, history)
