import threading
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from functools import cache, partial

import jax
import jax.numpy as jnp
import optax
from jax import Array

from emitter_optimizer.kernel.gain import coverage, gain
from emitter_optimizer.kernel.laws import Physics
from emitter_optimizer.kernel.occlusion import HardOcclusion, Occlusion, SoftOcclusion
from emitter_optimizer.kernel.scene import Scene

OPTIMIZERS: Mapping[str, Callable[[float], optax.GradientTransformation]] = {
    "adam": optax.adam,
    "adamw": optax.adamw,
    "nadam": optax.nadam,
    "lion": optax.lion,
    "sgd": partial(optax.sgd, momentum=0.9, nesterov=True),
}


@dataclass(frozen=True, slots=True)
class DescentSettings:
    """`step_size` and `blur` are shares of the scene's larger side.

    `blur` anneals from its first value to its second.
    """

    emitters: int
    steps: int
    starts: int = 1
    optimizer: str = "adam"
    step_size: float = 0.01
    blur: tuple[float, float] = (0.05, 0.001)
    report_every: int = 50
    seed: int = 0


@dataclass(frozen=True, slots=True)
class Step:
    index: int
    gain: float
    positions: Array


@dataclass(frozen=True, slots=True)
class Descent:
    """`gain` is measured with hard walls.

    `history` holds the blurred objective of the best start at each step.
    """

    positions: Array
    gain: float
    history: tuple[float, ...]
    start_gains: tuple[float, ...]


@jax.tree_util.register_dataclass
@dataclass(frozen=True)
class Progress:
    positions: Array
    state: optax.OptState


def _negative_gain(
    positions: Array, scene: Scene, occlusion: Occlusion, physics: Physics
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
        progress: Progress, sharpness: Array, scene: Scene
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
    first, last = settings.blur
    widths = side * first * (last / first) ** jnp.linspace(0.0, 1.0, settings.steps)
    return 1.0 / widths


def _settle(
    progress: Progress, scene: Scene, physics: Physics, history: list[float]
) -> Descent:
    gains = jax.vmap(gain, in_axes=(0, None, None, None))(
        progress.positions, scene, HardOcclusion(), physics
    )
    best = int(jnp.argmax(gains))
    return Descent(
        progress.positions[best],
        float(gains[best]),
        tuple(history),
        tuple(gains.tolist()),
    )


def descend(
    scene: Scene,
    physics: Physics,
    settings: DescentSettings,
    stop: threading.Event | None = None,
    on_step: Callable[[Step], None] | None = None,
) -> Descent:
    """Run `settings.starts` descents side by side; keep the best, hard walls."""
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
