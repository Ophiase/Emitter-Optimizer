import time

import jax
import numpy as np
from jax import Array

from emitter_optimizer.kernel import (
    Coverage,
    Descender,
    DescentSettings,
    Greedy,
    HardOcclusion,
)
from emitter_optimizer.maps.cases import Situation
from emitter_optimizer.render import MapImage, MethodImage, MethodRow
from emitter_optimizer.service.paths import PROJECT_ROOT
from scripts.situations import situations

OUTPUT = PROJECT_ROOT / "docs" / "benchmark" / "results.md"
FIGURES = PROJECT_ROOT / "docs" / "benchmark"
RANDOM_DRAWS = 32
STARTS = 4
STEPS = 300
POLISH_STEP = 0.003
REPORT_EVERY = 20


def _random(situation: Situation) -> float:
    coverage = Coverage(situation.scene, HardOcclusion(), situation.physics)
    draws = situation.scene.sample(jax.random.key(1), RANDOM_DRAWS, situation.emitters)
    return float(np.mean([coverage.gain(draw) for draw in draws]))


def _descent(situation: Situation, greedy: Array) -> tuple[float, Array]:
    """The better of free starts and of a descent polishing the greedy answer."""
    free = Descender(
        situation.scene,
        situation.physics,
        DescentSettings(
            situation.emitters, STEPS, starts=STARTS, report_every=REPORT_EVERY
        ),
    ).run()
    polished = Descender(
        situation.scene,
        situation.physics,
        DescentSettings(
            situation.emitters,
            STEPS,
            step_size=POLISH_STEP,
            report_every=REPORT_EVERY,
        ),
        start=greedy[None],
    ).run()
    best = max(free, polished, key=lambda result: result.gain)
    return best.gain, best.positions


def main() -> None:
    lines = [
        "# Benchmark",
        "",
        "Every gain comes from the same scene, with sharp walls. *Random* is the",
        f"mean of {RANDOM_DRAWS} placements drawn from the demand; *greedy* adds",
        "emitters one by one on the grid; *descent* is the better of"
        f" {STARTS} free starts",
        "and of a polish of the greedy answer. `just bench` writes this page.",
        "",
        "![The gain of each method above a random placement](methods.png)",
        "",
        "| case | emitters | random | greedy | descent | above random | seconds |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    rows = []
    for situation in situations():
        started = time.perf_counter()
        scene, physics = situation.scene, situation.physics
        greedy_positions = Greedy(scene, physics).place(situation.emitters)
        coverage = Coverage(scene, HardOcclusion(), physics)
        greedy = float(coverage.gain(greedy_positions))
        descent, positions = _descent(situation, greedy_positions)
        seconds = time.perf_counter() - started
        row = MethodRow(
            situation.name, situation.emitters, _random(situation), greedy, descent
        )
        rows.append(row)
        lines.append(
            f"| {row.case} | {row.emitters} | {row.random:.4f} | {row.greedy:.4f} | "
            f"{row.descent:.4f} | {row.above_random(row.descent):+.1f}% | "
            f"{seconds:.1f} |"
        )
        image = MapImage(scene, coverage, width=640).png(positions)
        (FIGURES / f"{situation.name}.png").write_bytes(image)
        print(lines[-1], flush=True)
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (FIGURES / "methods.png").write_bytes(MethodImage(rows).png())


if __name__ == "__main__":
    main()
