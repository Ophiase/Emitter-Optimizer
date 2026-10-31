import time

import jax
import numpy as np

from emitter_optimizer.kernel import (
    Coverage,
    Descender,
    DescentSettings,
    HardOcclusion,
)
from emitter_optimizer.service.paths import PROJECT_ROOT
from scripts.result import Result
from scripts.situation import Situation

ITERATIONS = 60
SEED = 0
STEP_SIZE = 0.01

CASES = PROJECT_ROOT / "resources" / "cases"


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
    return (
        Situation(CASES / "garden", "Sprinklers over allotment beds.", 120.0, 32, 24),
        Situation(CASES / "beach", "Lifeguards over the bathing strip.", 150.0, 32, 5),
        Situation(
            CASES / "marina", "Wi-Fi over a marina and its old town.", 300.0, 32, 8
        ),
        Situation(
            CASES / "harbor", "Lamps along the quays of a ferry port.", 400.0, 32, 14
        ),
        Situation(CASES / "ramparts", "Sirens inside a walled old town.", 350.0, 32, 4),
    )
