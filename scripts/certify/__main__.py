import json
import multiprocessing
from collections.abc import Iterator, Sequence
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from emitter_optimizer.kernel.placement.exact import Instance
from emitter_optimizer.service.paths import PROJECT_ROOT, RESOURCES_DIRECTORY
from scripts.certify.family import Family
from scripts.certify.measure import measure, measure_scale
from scripts.certify.report.figure import ComparisonFigure
from scripts.certify.report.page import page
from scripts.certify.runs.cases import RADII, case_instance
from scripts.certify.scores import Scores

REFERENCE = RESOURCES_DIRECTORY / "reference" / "coverage-with-walls.json"
PAGE = PROJECT_ROOT / "docs" / "benchmark" / "certified.md"
FIGURE = PROJECT_ROOT / "docs" / "benchmark" / "certified.png"
FIGURED = Family(400, 5, 12)
SCALE = (Family(800, 10, 12), Family(1600, 20, 12))
SIZES = (100, 200, 400)
EMITTERS = (3, 5, 10, 20)
WALLS = (0, 4, 12)
SEEDS = range(5)
WORKERS = 4


def _reference_instances() -> Iterator[Instance]:
    for points in SIZES:
        for emitters in EMITTERS:
            for walls in WALLS:
                for seed in SEEDS:
                    yield Family(points, emitters, walls).instance(seed)


def _measure_all(
    instances: Sequence[Instance],
) -> list[tuple[Scores, dict[str, object]]]:
    context = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(WORKERS, mp_context=context) as pool:
        return list(pool.map(measure, instances))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    reference = _measure_all(list(_reference_instances()))
    cases = _measure_all([case_instance(name) for name in RADII])
    records = [record for _, record in reference]
    _write(REFERENCE, json.dumps(records, separators=(",", ":")) + "\n")
    reference_scores = [scores for scores, _ in reference]
    case_scores = [scores for scores, _ in cases]
    scale = [measure_scale(family.instance(0)) for family in SCALE]
    _write(PAGE, page(reference_scores, case_scores, scale))
    ComparisonFigure(FIGURED.instance(0)).image().save(FIGURE)


if __name__ == "__main__":
    main()
