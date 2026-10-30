"""Command line: optimize a map, or open the window."""

import argparse
import json
from pathlib import Path

import numpy as np

from emitter_optimizer.engine.laws import load_law_file
from emitter_optimizer.engine.maps import load_collisions, load_density
from emitter_optimizer.engine.solver import Solver
from emitter_optimizer.paths import DEFAULT_EMITTER_FUNCTION, DEFAULT_SENSOR_FUNCTION

DEFAULT_MAP_SCALE = (100.0, 100.0)
DEFAULT_GRID_SIZE = (32, 32)
DEFAULT_EMITTERS = 15
DEFAULT_ITERATIONS = 200
DEFAULT_LEARNING_RATE = 1.0
DEFAULT_SEED = 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="emitter-optimizer",
        description="Place emitters so the map they cover is maximized.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    optimize = commands.add_parser("run", help="optimize a map and write the result")
    optimize.add_argument("--density", type=Path, help="grayscale image")
    optimize.add_argument("--collisions", type=Path, help="mask or CSV of segments")
    optimize.add_argument(
        "--map-scale",
        nargs=2,
        type=float,
        default=DEFAULT_MAP_SCALE,
        metavar=("WIDTH", "HEIGHT"),
    )
    optimize.add_argument(
        "--grid-size",
        nargs=2,
        type=int,
        default=DEFAULT_GRID_SIZE,
        metavar=("ROWS", "COLUMNS"),
    )
    optimize.add_argument("--emitters", type=int, default=DEFAULT_EMITTERS)
    optimize.add_argument("--iterations", type=int, default=DEFAULT_ITERATIONS)
    optimize.add_argument("--learning-rate", type=float, default=DEFAULT_LEARNING_RATE)
    optimize.add_argument("--seed", type=int, default=DEFAULT_SEED)
    optimize.add_argument("--emitter-law", type=Path, default=DEFAULT_EMITTER_FUNCTION)
    optimize.add_argument("--sensor-law", type=Path, default=DEFAULT_SENSOR_FUNCTION)
    optimize.add_argument("--out", type=Path, default=Path("out"))

    commands.add_parser("window", help="open the window")
    return parser


def run_optimization(arguments: argparse.Namespace) -> int:
    density = None if arguments.density is None else load_density(arguments.density)
    collisions = (
        None if arguments.collisions is None else load_collisions(arguments.collisions)
    )
    solver = Solver(
        n_emitters=int(arguments.emitters),
        density_map=density,
        collision_map=collisions,
        map_scale=(float(arguments.map_scale[0]), float(arguments.map_scale[1])),
        grid_size=(int(arguments.grid_size[0]), int(arguments.grid_size[1])),
        emitter_law=load_law_file(arguments.emitter_law),
        sensor_law=load_law_file(arguments.sensor_law),
        n_iteration=int(arguments.iterations),
        epsilon=float(arguments.learning_rate),
        seed=int(arguments.seed),
    )
    solver.solve()

    summary = _write(arguments.out, solver, arguments)
    print(json.dumps(summary, indent=2))
    return 0


def _write(
    directory: Path, solver: Solver, arguments: argparse.Namespace
) -> dict[str, object]:
    directory.mkdir(parents=True, exist_ok=True)
    np.savetxt(
        directory / "positions.csv",
        solver.emitters_positions,
        delimiter=",",
        header="x,y",
        comments="",
    )
    np.savetxt(
        directory / "history.csv",
        np.asarray(solver.history),
        header="loss",
        comments="",
    )
    figure = solver.make_fig()
    figure.savefig(directory / "figure.png")
    summary: dict[str, object] = {
        "gain": float(solver.field.gain(solver.emitters_positions)),
        "emitters": int(solver.emitters_positions.shape[0]),
        "iterations": int(solver.n_iteration),
        "learning_rate": float(solver.epsilon),
        "seed": int(arguments.seed),
        "map_scale": list(solver.map_scale),
        "grid_size": list(solver.grid_size),
    }
    (directory / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary


def main(arguments: list[str] | None = None) -> int:
    parsed = build_parser().parse_args(arguments)
    if parsed.command == "window":
        from emitter_optimizer.main import main as open_window

        open_window()
        return 0
    return run_optimization(parsed)
