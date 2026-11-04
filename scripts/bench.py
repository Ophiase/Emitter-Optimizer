import time
from dataclasses import dataclass

import jax
import numpy as np
from jax import Array

from emitter_optimizer.kernel import (
    Coverage,
    Descender,
    DescentResult,
    DescentSettings,
    Greedy,
    HardOcclusion,
    Relocation,
)
from emitter_optimizer.maps.cases import Situation
from emitter_optimizer.render import MapImage, MethodImage, MethodRow, StartsImage
from emitter_optimizer.service.paths import PROJECT_ROOT
from scripts.situations import situations

OUTPUT = PROJECT_ROOT / "docs" / "benchmark" / "results.md"
FIGURES = PROJECT_ROOT / "docs" / "benchmark"
RANDOM_DRAWS = 32
STARTS = 4
STEPS = 300
FREE_STEP = 0.01
POLISH_STEP = 0.003
REPORT_EVERY = 20
HEADER = (
    "| case | emitters | random | greedy | descent | relocation "
    "| spread alone | spread relocated | seconds |"
)


def _random(situation: Situation) -> float:
    coverage = Coverage(situation.scene, HardOcclusion(), situation.physics)
    draws = situation.scene.sample(jax.random.key(1), RANDOM_DRAWS, situation.emitters)
    return float(np.mean([coverage.gain(draw) for draw in draws]))


@dataclass(frozen=True, slots=True)
class Search:
    """Every start's end, alone and relocated; the placement of the best of all."""

    free: tuple[float, ...]
    relocated: tuple[float, ...]
    descent: float
    relocation: float
    positions: Array


def _descend(situation: Situation, start: Array, polish: bool) -> DescentResult:
    settings = DescentSettings(
        situation.emitters,
        STEPS,
        step_size=POLISH_STEP if polish else FREE_STEP,
        report_every=REPORT_EVERY,
    )
    return Descender(
        situation.scene, situation.physics, settings, start=start[None]
    ).run()


def _relocate(situation: Situation, positions: Array) -> DescentResult:
    moved = Relocation(situation.scene, situation.physics).improve(positions)
    return _descend(situation, moved, polish=True)


def _search(situation: Situation, greedy: Array) -> Search:
    """The same starts alone and relocated, and the same two steps from greedy."""
    starts = situation.scene.sample(jax.random.key(0), STARTS, situation.emitters)
    free = [_descend(situation, start, polish=False) for start in starts]
    relocated = [_relocate(situation, result.positions) for result in free]
    polished = _descend(situation, greedy, polish=True)
    from_greedy = _relocate(situation, greedy)
    descent = max(*free, polished, key=lambda result: result.gain)
    best = max(*relocated, from_greedy, key=lambda result: result.gain)
    return Search(
        tuple(result.gain for result in free),
        tuple(result.gain for result in relocated),
        descent.gain,
        best.gain,
        best.positions,
    )


def _spread(gains: tuple[float, ...]) -> float:
    return 100.0 * (max(gains) - min(gains)) / max(gains)


def _page(table: list[str]) -> str:
    return f"""# Benchmark

Every gain comes from the same scene, with sharp walls.

- **Random**: the mean of {RANDOM_DRAWS} placements drawn from the demand.
- **Greedy**: emitters added one by one on the grid.
- **Descent**: the better of {STARTS} free starts and of a polish of greedy.
- **Relocation**: the same starts and greedy, each followed by
  [jumps](../local-minima.md) and a polish.
- **Spread**: how far the worst start ends below the best one.

What it says:

- **Greedy reaches most of the gain**; a relocation adds the rest.
- **A relocation makes the answer depend far less on the start.**
- A dot hides another when they tie.

`just bench` writes this page.

![The gain of each method above a random placement](methods.png)

![Each start, alone and relocated](starts.png)

{HEADER}
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(table)}
"""


def main() -> None:
    table = []
    rows = []
    for situation in situations():
        started = time.perf_counter()
        scene, physics = situation.scene, situation.physics
        greedy_positions = Greedy(scene, physics).place(situation.emitters)
        coverage = Coverage(scene, HardOcclusion(), physics)
        greedy = float(coverage.gain(greedy_positions))
        found = _search(situation, greedy_positions)
        seconds = time.perf_counter() - started
        row = MethodRow(
            situation.name,
            situation.emitters,
            _random(situation),
            greedy,
            found.descent,
            found.free,
            found.relocated,
        )
        rows.append(row)
        table.append(
            f"| {row.case} | {row.emitters} | {row.random:.4f} | {row.greedy:.4f} | "
            f"{row.descent:.4f} | {found.relocation:.4f} | "
            f"{_spread(found.free):.1f}% | {_spread(found.relocated):.1f}% | "
            f"{seconds:.0f} |"
        )
        image = MapImage(scene, coverage, width=640).png(found.positions)
        (FIGURES / f"{situation.name}.png").write_bytes(image)
        print(table[-1], flush=True)
    OUTPUT.write_text(_page(table), encoding="utf-8")
    (FIGURES / "methods.png").write_bytes(MethodImage(rows).png())
    (FIGURES / "starts.png").write_bytes(StartsImage(rows).png())


if __name__ == "__main__":
    main()
