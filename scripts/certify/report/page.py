from collections.abc import Callable, Sequence
from statistics import mean, median

import numpy as np

from scripts.certify.scores import Scores

INTRODUCTION = """\
# How far from the proved optimum

`just certify` writes this page and
[the reference set](../../resources/reference/coverage-with-walls.json).
[The method and its limits](certified-method.md) are on their own page.
"""
FIGURE = """\
![The best placement on the demand points, and the proved optimum](certified.png)

*Left, the best placement if emitters must stand on a demand point; right, the
proved optimum. Green points are covered, red are not, black lines are walls.*"""
READING = """\
- **Discrete solvers** are exact over their sites, as spopt's formulation is.
- **The grid of 64 by 64** is the one the engine jumps on.
- **The seconds** depend on the machine; the optima do not."""
CASES_NOTE = """\
Each case of the [benchmark](results.md), with its law reduced to the disk one
emitter serves alone. These are not the laws of that benchmark, so the two tables
do not compare."""
METHODS: tuple[tuple[str, Callable[[Scores], float]], ...] = (
    ("Random, 32 draws", lambda scores: scores.random),
    ("Exact on the demand points", lambda scores: scores.demand_sites),
    ("Exact on a 16 by 16 grid", lambda scores: scores.grid_16),
    ("Exact on a 32 by 32 grid", lambda scores: scores.grid_32),
    ("Exact on a 64 by 64 grid", lambda scores: scores.grid_64),
    ("Greedy on the 64 by 64 grid", lambda scores: scores.greedy),
    ("Engine: descent", lambda scores: scores.descent),
    ("Engine: relocation and polish", lambda scores: scores.relocation),
)


def _gap(scores: Scores, reach: Callable[[Scores], float]) -> float:
    return 100.0 * (scores.upper - reach(scores)) / scores.upper


def method_table(rows: Sequence[Scores]) -> str:
    lines = [
        "| Method | mean gap | median | 95th percentile | worst | optimum reached |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, reach in METHODS:
        gaps = [_gap(row, reach) for row in rows]
        hits = sum(gap <= 0.0 for gap in gaps)
        lines.append(
            f"| {name} | {mean(gaps):.2f}% | {median(gaps):.2f}% | "
            f"{float(np.percentile(gaps, 95)):.2f}% | {max(gaps):.2f}% | "
            f"{hits} of {len(gaps)} |"
        )
    return "\n".join(lines)


def split_table(rows: Sequence[Scores], label: str, key: str) -> str:
    lines = [
        f"| {label} | instances | 32 by 32 grid | 64 by 64 grid | descent | relocation "
        "| exact, median seconds |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for value in sorted({getattr(row, key) for row in rows}):
        group = [row for row in rows if getattr(row, key) == value]
        cells = " | ".join(
            f"{mean(_gap(row, reach) for row in group):.2f}%"
            for reach in (
                lambda scores: scores.grid_32,
                lambda scores: scores.grid_64,
                lambda scores: scores.descent,
                lambda scores: scores.relocation,
            )
        )
        seconds = median(row.exact_seconds for row in group)
        lines.append(f"| {value} | {len(group)} | {cells} | {seconds:.1f} |")
    return "\n".join(lines)


def case_table(rows: Sequence[Scores]) -> str:
    lines = [
        "| map | points | walls | emitters | covered | proved | exact seconds "
        "| 64 by 64 grid | descent | relocation |",
        "| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        total = row.lower / row.upper if row.upper else 0.0
        state = (
            "yes" if row.lower == row.upper else f"no, {100 * (1 - total):.2f}% open"
        )
        lines.append(
            f"| {row.name} | {row.points} | {row.walls} | {row.emitters} | {row.upper} "
            f"| {state} | {row.exact_seconds:.0f} "
            f"| {_gap(row, lambda scores: scores.grid_64):.2f}% "
            f"| {_gap(row, lambda scores: scores.descent):.2f}% "
            f"| {_gap(row, lambda scores: scores.relocation):.2f}% |"
        )
    return "\n".join(lines)


def scale_table(rows: Sequence[str]) -> str:
    header = (
        "| points | emitters | walls | candidates | kept | proved | seconds |\n"
        "| ---: | ---: | ---: | ---: | ---: | --- | ---: |\n"
    )
    return header + "\n".join(rows)


def _sections(
    reference: Sequence[Scores], cases: Sequence[Scores], scale: Sequence[str]
) -> str:
    sections = (
        ("The reference set", method_table(reference)),
        ("By number of walls", split_table(reference, "walls", "walls")),
        ("By number of emitters", split_table(reference, "emitters", "emitters")),
        ("By number of points", split_table(reference, "points", "points")),
        ("The published maps, as disks", f"{CASES_NOTE}\n\n{case_table(cases)}"),
        ("How far it scales", scale_table(scale)),
    )
    return "\n\n".join(f"## {title}\n\n{body}" for title, body in sections)


def page(
    reference: Sequence[Scores], cases: Sequence[Scores], scale: Sequence[str]
) -> str:
    proved = sum(row.lower == row.upper for row in reference)
    summary = (
        f"**{proved} of {len(reference)} reference instances are solved to a proved\n"
        "optimum.** Every gap below is measured against it: "
        "`(optimum - covered) / optimum`."
    )
    return f"{INTRODUCTION}\n{summary}\n\n{FIGURE}\n\n{READING}\n\n" + (
        _sections(reference, cases, scale) + "\n"
    )
