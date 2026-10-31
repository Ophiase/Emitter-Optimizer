import json
from pathlib import Path

import numpy as np

import emitter_optimizer.__main__ as cli


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
