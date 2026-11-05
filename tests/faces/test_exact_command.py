import json
from pathlib import Path

import pytest

import emitter_optimizer.__main__ as cli

POINTS = "49,50,3\n51,50,2\n90,90,1\n"
WALLS = "50,20,50,80\n"
PLAN = "20,20\n"


def _arguments(folder: Path, *extra: str) -> list[str]:
    (folder / "points.csv").write_text(POINTS, encoding="utf-8")
    (folder / "walls.csv").write_text(WALLS, encoding="utf-8")
    return [
        "exact",
        "--points",
        str(folder / "points.csv"),
        "--walls",
        str(folder / "walls.csv"),
        "--radius",
        "10",
        "--emitters",
        "1",
        "--map-scale",
        "100",
        "100",
        "--out",
        str(folder / "out"),
        *extra,
    ]


def test_the_certificate_reports_a_proved_optimum(tmp_path: Path) -> None:
    assert cli.main(_arguments(tmp_path)) == 0

    summary = json.loads((tmp_path / "out" / "certificate.json").read_text("utf-8"))
    assert summary["covered_weight"] == summary["upper_bound"] == 3
    assert summary["proved_optimal"] is True
    assert (tmp_path / "out" / "positions.csv").is_file()


def test_a_plan_is_judged_against_the_bound(tmp_path: Path) -> None:
    (tmp_path / "plan.csv").write_text(PLAN, encoding="utf-8")

    cli.main(_arguments(tmp_path, "--plan", str(tmp_path / "plan.csv")))

    summary = json.loads((tmp_path / "out" / "certificate.json").read_text("utf-8"))
    assert summary["your_plan"]["covered_weight"] == 0
    assert summary["your_plan"]["percent_below_the_bound"] == pytest.approx(100.0)


def test_a_fractional_weight_is_a_message(tmp_path: Path) -> None:
    arguments = _arguments(tmp_path)
    (tmp_path / "points.csv").write_text("49,50,0.5\n", encoding="utf-8")

    with pytest.raises(SystemExit) as stopped:
        cli.run_exact(cli.build_parser().parse_args(arguments))
    assert stopped.value.code == 2
