import time

import jax
import numpy as np

from emitter_optimizer.kernel import (
    Coverage,
    Descender,
    DescentSettings,
    Extent,
    GridShape,
    HardOcclusion,
    Physics,
)
from emitter_optimizer.paths import DEFAULT_EMITTER_FUNCTION, DEFAULT_SENSOR_FUNCTION
from emitter_optimizer.service.evaluated_law import EvaluatedLaw
from scripts.densities import collision_map, crop_rows, density_map, peaks, rooms
from scripts.result import Result
from scripts.situation import Situation

ITERATIONS = 60
EMITTERS = 15
SEED = 0
STEP_SIZE = 0.01

PHYSICS = Physics(
    emitter=EvaluatedLaw.from_file(DEFAULT_EMITTER_FUNCTION),
    sensor=EvaluatedLaw.from_file(DEFAULT_SENSOR_FUNCTION),
)


def measure(
    situation: Situation,
    *,
    iterations: int = ITERATIONS,
    emitters: int = EMITTERS,
    seed: int = SEED,
) -> Result:
    scene = situation.scene
    coverage = Coverage(scene, HardOcclusion(), PHYSICS)
    start = scene.sample(jax.random.key(seed), 1, emitters)[0]
    initial = float(coverage.gain(start))
    settings = DescentSettings(
        emitters=emitters,
        steps=iterations,
        step_size=STEP_SIZE,
        seed=seed,
    )
    started = time.perf_counter()
    result = Descender(scene, PHYSICS, settings).run()
    seconds = time.perf_counter() - started
    return Result(
        situation,
        np.asarray(result.positions),
        initial,
        float(result.gain),
        result.history,
        seconds,
    )


def situations() -> tuple[Situation, ...]:
    return (
        Situation(
            "uniform",
            "No density, no walls: the emitters spread out.",
            None,
            None,
            Extent(100.0, 100.0),
            GridShape(32, 32),
        ),
        Situation(
            "farm",
            "Rows of crops, a hedge with a gate.",
            density_map(crop_rows((32, 64))),
            collision_map(((0.5, 0.0), (0.5, 0.4)), ((0.5, 0.6), (0.5, 1.0))),
            Extent(100.0, 50.0),
            GridShape(32, 64),
        ),
        Situation(
            "building",
            "Two rooms and a corridor, walls between.",
            density_map(rooms((32, 32))),
            collision_map(
                ((0.5, 0.0), (0.5, 0.45)),
                ((0.5, 0.55), (0.5, 1.0)),
                ((0.0, 0.5), (0.35, 0.5)),
            ),
            Extent(60.0, 40.0),
            GridShape(32, 32),
        ),
        Situation(
            "shop",
            "Three demand peaks in a town centre.",
            density_map(peaks((32, 32), ((0.3, 0.3), (0.7, 0.6), (0.5, 0.82)))),
            None,
            Extent(100.0, 100.0),
            GridShape(32, 32),
        ),
        Situation(
            "wide",
            "A map twice as wide as tall.",
            density_map(peaks((32, 64), ((0.25, 0.5), (0.75, 0.5)), width=0.2)),
            None,
            Extent(100.0, 50.0),
            GridShape(32, 64),
        ),
    )
