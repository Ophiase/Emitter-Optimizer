import time

import jax
import numpy as np

from emitter_optimizer.kernel import (
    Coverage,
    Descender,
    DescentSettings,
    HardOcclusion,
)
from emitter_optimizer.maps.cases import SITUATIONS, Situation
from scripts.result import Result

ITERATIONS = 60
SEED = 0
STEP_SIZE = 0.01


def measure(
    situation: Situation,
    *,
    iterations: int = ITERATIONS,
    emitters: int | None = None,
    seed: int = SEED,
    report_every: int = 50,
    on_step: Descender.StepCallback | None = None,
) -> Result:
    scene = situation.scene
    physics = situation.physics
    emitters = situation.emitters if emitters is None else emitters
    coverage = Coverage(scene, HardOcclusion(), physics)
    start = scene.sample(jax.random.key(seed), 1, emitters)[0]
    initial = float(coverage.gain(start))
    settings = DescentSettings(
        emitters=emitters,
        steps=iterations,
        step_size=STEP_SIZE,
        report_every=report_every,
        seed=seed,
    )
    started = time.perf_counter()
    result = Descender(scene, physics, settings, on_step=on_step).run()
    seconds = time.perf_counter() - started
    return Result(
        situation,
        np.asarray(result.positions),
        np.asarray(start),
        initial,
        float(result.gain),
        result.history,
        seconds,
    )


def situations() -> tuple[Situation, ...]:
    return SITUATIONS
