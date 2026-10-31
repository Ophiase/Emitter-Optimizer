import json
from pathlib import Path

import numpy as np

from emitter_optimizer import cli


def test_the_command_writes_a_full_result(tmp_path: Path) -> None:
    arguments = cli.build_parser().parse_args([
        "run",
        "--emitters",
        "3",
        "--iterations",
        "2",
        "--seed",
        "0",
        "--out",
        str(tmp_path),
    ])

    assert cli.run_optimization(arguments) == 0

    positions = np.loadtxt(tmp_path / "positions.csv", delimiter=",", skiprows=1)
    summary = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    assert positions.shape == (3, 2)
    assert (tmp_path / "figure.png").stat().st_size > 0
    assert summary["emitters"] == 3


def test_the_window_can_be_prepared_without_opening_it() -> None:
    arguments = cli.build_parser().parse_args([
        "window",
        "--emitters",
        "2",
        "--grid-size",
        "4",
        "4",
        "--iterations",
        "2",
        "--seed",
        "0",
        "--solve",
    ])

    configuration = cli.prepare_window(arguments)

    assert configuration.emitter_count == 2
    assert configuration.solver.history
