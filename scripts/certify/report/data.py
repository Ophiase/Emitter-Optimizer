from collections.abc import Sequence
from statistics import mean

from scripts.certify.report.page import (
    case_table,
    method_table,
    scale_table,
    split_table,
)
from scripts.certify.scores import Scores


def _block(table: str) -> dict[str, object]:
    lines = table.splitlines()
    rows = [[cell.strip() for cell in line.strip("|").split("|")] for line in lines]
    return {"header": rows[0], "rows": rows[2:]}


def _percent(value: float) -> str:
    return f"{value:.2f}%"


def _gaps(rows: Sequence[Scores], field: str) -> list[float]:
    return [100.0 * (row.upper - getattr(row, field)) / row.upper for row in rows]


def report_data(
    reference: Sequence[Scores], cases: Sequence[Scores], scale: Sequence[str]
) -> dict[str, object]:
    """Every number the Typst report prints, so that it holds none of its own."""
    return {
        "proved": str(sum(row.lower == row.upper for row in reference)),
        "total": str(len(reference)),
        "demand_mean": _percent(mean(_gaps(reference, "demand_sites"))),
        "demand_worst": _percent(max(_gaps(reference, "demand_sites"))),
        "engine_mean": _percent(mean(_gaps(reference, "relocation"))),
        "methods": _block(method_table(reference)),
        "walls": _block(split_table(reference, "walls", "walls")),
        "cases": _block(case_table(cases)),
        "scale": _block(scale_table(scale)),
    }
