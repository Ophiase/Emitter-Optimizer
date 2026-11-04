import argparse
import json
from pathlib import Path

import numpy as np
import pytest

import emitter_optimizer.__main__ as cli
from emitter_optimizer.maps.cases import CASE_NAMES, situation_named
from emitter_optimizer.service import Session
from scripts.situations import situations


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


def test_the_window_takes_the_same_map_options() -> None:
    arguments = cli.build_parser().parse_args([
        "window",
        "--emitters",
        "3",
        "--iterations",
        "2",
    ])

    assert arguments.emitters == 3
    assert arguments.iterations == 2


def _parse(*arguments: str) -> argparse.Namespace:
    return cli.build_parser().parse_args(list(arguments))


def _refusal(capsys: pytest.CaptureFixture[str], *arguments: str) -> str:
    """Run the command, require a non-zero exit, and return its single stderr line."""
    with pytest.raises(SystemExit) as exit_information:
        cli.main(list(arguments))
    assert exit_information.value.code not in {0, None}
    lines = capsys.readouterr().err.splitlines()
    assert len(lines) == 1
    return lines[0]


def _lawless_file(folder: Path) -> Path:
    law = folder / "lawless.py"
    law.write_text("THROW = 6.0\n", encoding="utf-8")
    return law


def test_a_case_gives_the_extent_the_grid_the_count_and_the_laws() -> None:
    garden = situation_named("garden")

    options = cli.map_options(_parse("run", "--case", "garden"))

    assert options.extent == garden.extent
    assert options.grid == garden.grid
    assert options.emitters == garden.emitters
    assert options.emitter_law == garden.folder / "emitter.py"
    assert options.sensor_law == garden.folder / "sensor.py"
    assert options.walls_on_grid


def test_a_flag_overrides_the_case_even_at_the_standard_value() -> None:
    options = cli.map_options(
        _parse("run", "--case", "garden", "--emitters", "15", "--grid-size", "8", "9")
    )

    assert options.emitters == 15
    assert (options.grid.rows, options.grid.columns) == (8, 9)
    assert options.extent == situation_named("garden").extent


def test_run_a_case_by_name(tmp_path: Path) -> None:
    garden = situation_named("garden")

    status = cli.main([
        "run",
        "--case",
        "garden",
        "--iterations",
        "1",
        "--grid-size",
        "8",
        "8",
        "--out",
        str(tmp_path),
    ])

    summary = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    assert status == 0
    assert summary["emitters"] == garden.emitters
    assert summary["map_scale"] == pytest.approx([
        garden.extent.width,
        garden.extent.height,
    ])
    assert summary["grid_size"] == [8, 8]


def test_serve_a_case_by_name(monkeypatch: pytest.MonkeyPatch) -> None:
    served: list[Session] = []
    monkeypatch.setattr(cli, "serve", lambda session, _settings: served.append(session))
    harbor = situation_named("harbor")

    assert cli.main(["serve", "--case", "harbor", "--grid-size", "8", "8"]) == 0

    assert served[0].emitters == harbor.emitters
    assert float(served[0].scene.bounds[0]) == pytest.approx(harbor.extent.width)


def test_the_window_takes_a_case_and_edits_its_laws() -> None:
    garden = situation_named("garden")

    config = cli.window_config(
        _parse("window", "--case", "garden", "--iterations", "1", "--emitters", "2")
    )

    assert config.map_scale == (garden.extent.width, garden.extent.height)
    assert config.grid_size == (garden.grid.rows, garden.grid.columns)
    assert config.emitter_count == 2
    assert config.emitter_source == garden.folder / "emitter.py"
    assert config.sensor_source == garden.folder / "sensor.py"
    assert config.solver.scene.grid == garden.grid


def test_the_scripts_read_the_package_catalogue() -> None:
    assert tuple(situation.name for situation in situations()) == CASE_NAMES


def test_an_unknown_case_lists_the_valid_ones(
    capsys: pytest.CaptureFixture[str],
) -> None:
    line = _refusal(capsys, "run", "--case", "atlantis")

    assert "atlantis" in line
    assert all(name in line for name in CASE_NAMES)


@pytest.mark.parametrize("flag", ["--density", "--collisions"])
def test_a_missing_map_is_a_message(
    capsys: pytest.CaptureFixture[str], flag: str
) -> None:
    assert "no-such.png" in _refusal(capsys, "run", flag, "no-such.png")


@pytest.mark.parametrize("flag", ["--emitter-law", "--sensor-law"])
def test_a_missing_law_is_a_message(
    capsys: pytest.CaptureFixture[str], flag: str
) -> None:
    assert "no-such.py" in _refusal(capsys, "run", flag, "no-such.py")


@pytest.mark.parametrize("value", ["0", "-3"])
def test_no_emitter_is_a_message(
    capsys: pytest.CaptureFixture[str], value: str
) -> None:
    assert "--emitters" in _refusal(capsys, "run", "--emitters", value)


@pytest.mark.parametrize("value", ["0", "-3"])
def test_no_iteration_is_a_message(
    capsys: pytest.CaptureFixture[str], value: str
) -> None:
    assert "--iterations" in _refusal(capsys, "run", "--iterations", value)


@pytest.mark.parametrize("size", [("0", "8"), ("8", "-1")])
def test_a_grid_without_cells_is_a_message(
    capsys: pytest.CaptureFixture[str], size: tuple[str, str]
) -> None:
    assert "--grid-size" in _refusal(capsys, "run", "--grid-size", *size)


@pytest.mark.parametrize("scale", [("0", "10"), ("10", "-1"), ("nan", "10")])
def test_a_map_without_area_is_a_message(
    capsys: pytest.CaptureFixture[str], scale: tuple[str, str]
) -> None:
    assert "--map-scale" in _refusal(capsys, "run", "--map-scale", *scale)


def test_a_law_without_eval_is_a_message(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    law = _lawless_file(tmp_path)

    assert "eval" in _refusal(capsys, "run", "--emitter-law", str(law))


def test_a_law_that_fails_to_load_is_a_message(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    law = tmp_path / "broken.py"
    law.write_text("raise RuntimeError('broken on import')\n", encoding="utf-8")

    assert "broken on import" in _refusal(capsys, "run", "--sensor-law", str(law))


def test_a_map_that_is_no_image_is_a_message(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    density = tmp_path / "density.png"
    density.write_text("not an image", encoding="utf-8")

    assert "density.png" in _refusal(capsys, "run", "--density", str(density))


def test_the_window_refuses_a_law_without_eval(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    law = _lawless_file(tmp_path)

    assert "eval" in _refusal(capsys, "window", "--emitter-law", str(law))
