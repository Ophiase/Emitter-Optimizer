import argparse
import json
from pathlib import Path

import numpy as np

from emitter_optimizer.engine.laws import load_law_file
from emitter_optimizer.engine.solver import Solver
from emitter_optimizer.gui.configuration import GuiConfig
from emitter_optimizer.paths import DEFAULT_EMITTER_FUNCTION, DEFAULT_SENSOR_FUNCTION
from emitter_optimizer.service import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    MapOptions,
    ServiceSettings,
    serve,
)
from emitter_optimizer.service.options import (
    DEFAULT_EMITTERS,
    DEFAULT_GRID_SIZE,
    DEFAULT_LEARNING_RATE,
    DEFAULT_MAP_SCALE,
    DEFAULT_RUN_ITERATIONS,
    DEFAULT_SEED,
)


def _add_map_arguments(command: argparse.ArgumentParser) -> None:
    command.add_argument("--density", type=Path, help="grayscale image")
    command.add_argument("--collisions", type=Path, help="mask or CSV of segments")
    command.add_argument(
        "--map-scale",
        nargs=2,
        type=float,
        default=DEFAULT_MAP_SCALE,
        metavar=("WIDTH", "HEIGHT"),
    )
    command.add_argument(
        "--grid-size",
        nargs=2,
        type=int,
        default=DEFAULT_GRID_SIZE,
        metavar=("ROWS", "COLUMNS"),
    )
    command.add_argument("--emitters", type=int, default=DEFAULT_EMITTERS)
    command.add_argument("--learning-rate", type=float, default=DEFAULT_LEARNING_RATE)
    command.add_argument("--seed", type=int, default=DEFAULT_SEED)
    command.add_argument("--emitter-law", type=Path, default=DEFAULT_EMITTER_FUNCTION)
    command.add_argument("--sensor-law", type=Path, default=DEFAULT_SENSOR_FUNCTION)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="emitter-optimizer",
        description="Place emitters so the map they cover is maximized.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    optimize = commands.add_parser("run", help="optimize a map and write the result")
    _add_map_arguments(optimize)
    optimize.add_argument("--iterations", type=int, default=DEFAULT_RUN_ITERATIONS)
    optimize.add_argument("--out", type=Path, default=Path("out"))

    service = commands.add_parser(
        "serve",
        help="serve the engine on 127.0.0.1 for an agent",
    )
    _add_map_arguments(service)
    service.add_argument("--host", default=str(DEFAULT_HOST))
    service.add_argument("--port", type=int, default=DEFAULT_PORT)

    window = commands.add_parser(
        "window",
        help="open the window, on an optimized map if asked",
    )
    _add_map_arguments(window)
    window.add_argument("--iterations", type=int, default=DEFAULT_RUN_ITERATIONS)
    window.add_argument(
        "--solve",
        action="store_true",
        help="optimize before opening the window",
    )
    return parser


def run_optimization(arguments: argparse.Namespace) -> int:
    solver = MapOptions.from_arguments(arguments).solver(int(arguments.iterations))
    solver.solve()

    summary = write_result(arguments.out, solver)
    print(json.dumps(summary, indent=2))
    return 0


def run_service(arguments: argparse.Namespace) -> int:
    settings = ServiceSettings(host=arguments.host, port=arguments.port)
    serve(MapOptions.from_arguments(arguments).session(), settings)
    return 0


def write_result(directory: Path, solver: Solver) -> dict[str, object]:
    """Write the four files of a run, and return the summary they describe."""
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
        "iterations": solver.settings.iteration_count,
        "learning_rate": solver.settings.learning_rate,
        "seed": solver.seed,
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
    if parsed.command == "serve":
        return run_service(parsed)
    if parsed.command == "window":
        return open_window(parsed)
    return run_optimization(parsed)


def window_configuration(arguments: argparse.Namespace) -> GuiConfig:
    options = MapOptions.from_arguments(arguments)
    return GuiConfig(
        iteration_count=int(arguments.iterations),
        learning_rate=options.learning_rate,
        emitter_count=options.emitters,
        map_scale=options.map_scale,
        grid_size=options.grid_size,
        density_map=options.density,
        collision_map=options.collisions,
        emitter_law=load_law_file(options.emitter_law),
        sensor_law=load_law_file(options.sensor_law),
    )


def prepare_window(arguments: argparse.Namespace) -> GuiConfig:
    config = window_configuration(arguments)
    if arguments.solve:
        config.solver.solve()
    return config


def open_window(arguments: argparse.Namespace) -> int:
    from emitter_optimizer.gui.application import Application

    Application(prepare_window(arguments))()
    return 0
