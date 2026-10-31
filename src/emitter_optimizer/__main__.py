import argparse
import json
from pathlib import Path

import numpy as np

from emitter_optimizer.gui.application import Application
from emitter_optimizer.gui.configuration import GuiConfig
from emitter_optimizer.maps import Density, Walls
from emitter_optimizer.service import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    MapOptions,
    ServiceSettings,
    Session,
    serve,
)
from emitter_optimizer.service.evaluated_law import EvaluatedLaw
from emitter_optimizer.service.models import RunRequest, State
from emitter_optimizer.service.options import (
    DEFAULT_EMITTERS,
    DEFAULT_GRID_SIZE,
    DEFAULT_MAP_SCALE,
    DEFAULT_RUN_ITERATIONS,
    DEFAULT_SEED,
    DEFAULT_STEP_SIZE,
)
from emitter_optimizer.service.paths import (
    DEFAULT_EMITTER_FUNCTION,
    DEFAULT_SENSOR_FUNCTION,
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
    command.add_argument("--step-size", type=float, default=DEFAULT_STEP_SIZE)
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
        "serve", help="serve the engine on 127.0.0.1 for an agent"
    )
    _add_map_arguments(service)
    service.add_argument("--host", default=str(DEFAULT_HOST))
    service.add_argument("--port", type=int, default=DEFAULT_PORT)

    window = commands.add_parser("window", help="open the desktop window on a map")
    _add_map_arguments(window)
    window.add_argument("--iterations", type=int, default=DEFAULT_RUN_ITERATIONS)
    window.add_argument(
        "--solve",
        action="store_true",
        help="optimize before opening the window",
    )
    return parser


def run_optimization(arguments: argparse.Namespace) -> int:
    session = MapOptions.from_arguments(arguments).session()
    state = session.run(RunRequest(iterations=int(arguments.iterations)))
    summary = write_result(arguments.out, session, state)
    print(json.dumps(summary, indent=2))
    return 0


def run_service(arguments: argparse.Namespace) -> int:
    settings = ServiceSettings(host=arguments.host, port=arguments.port)
    serve(MapOptions.from_arguments(arguments).session(), settings)
    return 0


def write_result(directory: Path, session: Session, state: State) -> dict[str, object]:
    """Write the four files of a run, and return the summary they describe."""
    directory.mkdir(parents=True, exist_ok=True)
    np.savetxt(
        directory / "positions.csv",
        np.asarray(state.positions),
        delimiter=",",
        header="x,y",
        comments="",
    )
    np.savetxt(
        directory / "history.csv",
        np.asarray(session.history),
        header="gain",
        comments="",
    )
    (directory / "figure.png").write_bytes(session.figure())
    summary: dict[str, object] = {
        "gain": state.gain,
        "emitters": state.emitters,
        "iterations": len(session.history),
        "step_size": session.step_size,
        "seed": session.seed,
        "map_scale": list(state.map_scale),
        "grid_size": list(state.grid_size),
    }
    (directory / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def open_window(arguments: argparse.Namespace) -> int:
    config = GuiConfig(
        iteration_count=int(arguments.iterations),
        learning_rate=float(arguments.step_size),
        emitter_count=int(arguments.emitters),
        map_scale=(float(arguments.map_scale[0]), float(arguments.map_scale[1])),
        grid_size=(int(arguments.grid_size[0]), int(arguments.grid_size[1])),
        density=(
            None if arguments.density is None else Density.load(arguments.density)
        ),
        walls=(
            None if arguments.collisions is None else Walls.load(arguments.collisions)
        ),
        emitter_law=EvaluatedLaw.from_file(arguments.emitter_law),
        sensor_law=EvaluatedLaw.from_file(arguments.sensor_law),
    )
    if arguments.solve:
        config.solver.solve()
    Application(config)()
    return 0


def main(arguments: list[str] | None = None) -> int:
    parsed = build_parser().parse_args(arguments)
    if parsed.command == "serve":
        return run_service(parsed)
    if parsed.command == "window":
        return open_window(parsed)
    return run_optimization(parsed)


if __name__ == "__main__":
    raise SystemExit(main())
