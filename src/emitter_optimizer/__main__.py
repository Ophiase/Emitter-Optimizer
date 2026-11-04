import argparse
import json
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

import numpy as np

from emitter_optimizer.gui.application import Application
from emitter_optimizer.gui.configuration import GuiConfig
from emitter_optimizer.maps.cases import CASE_NAMES, situation_named
from emitter_optimizer.service import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    MapOptions,
    ServiceSettings,
    Session,
    serve,
)
from emitter_optimizer.service.models import RunRequest, State
from emitter_optimizer.service.options import (
    DEFAULT_RUN_ITERATIONS,
    CommandLineParser,
)


def _add_map_arguments(command: argparse.ArgumentParser) -> None:
    command.add_argument(
        "--case",
        choices=CASE_NAMES,
        help="a case by name; any other flag given overrides its value",
    )
    command.add_argument(
        "--density", type=CommandLineParser.existing_file, help="grayscale image"
    )
    command.add_argument(
        "--collisions",
        type=CommandLineParser.existing_file,
        help="mask or CSV of segments",
    )
    command.add_argument(
        "--map-scale",
        nargs=2,
        type=CommandLineParser.positive_float,
        metavar=("WIDTH", "HEIGHT"),
    )
    command.add_argument(
        "--grid-size",
        nargs=2,
        type=CommandLineParser.positive_int,
        metavar=("ROWS", "COLUMNS"),
    )
    command.add_argument("--emitters", type=CommandLineParser.positive_int)
    command.add_argument("--step-size", type=CommandLineParser.positive_float)
    command.add_argument("--seed", type=int)
    command.add_argument("--emitter-law", type=CommandLineParser.existing_file)
    command.add_argument("--sensor-law", type=CommandLineParser.existing_file)


def _add_iterations_argument(command: argparse.ArgumentParser) -> None:
    command.add_argument(
        "--iterations",
        type=CommandLineParser.positive_int,
        default=DEFAULT_RUN_ITERATIONS,
    )


def build_parser() -> CommandLineParser:
    parser = CommandLineParser(
        prog="emitter-optimizer",
        description="Place emitters so the map they cover is maximized.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    optimize = commands.add_parser("run", help="optimize a map and write the result")
    _add_map_arguments(optimize)
    _add_iterations_argument(optimize)
    optimize.add_argument("--out", type=Path, default=Path("out"))

    service = commands.add_parser(
        "serve", help="serve the engine on 127.0.0.1 for an agent"
    )
    _add_map_arguments(service)
    service.add_argument("--host", default=str(DEFAULT_HOST))
    service.add_argument("--port", type=int, default=DEFAULT_PORT)

    window = commands.add_parser("window", help="open the desktop window on a map")
    _add_map_arguments(window)
    _add_iterations_argument(window)
    window.add_argument(
        "--solve",
        action="store_true",
        help="optimize before opening the window",
    )
    return parser


@contextmanager
def _bad_input_is_a_message() -> Generator[None]:
    try:
        yield
    except (OSError, ValueError) as error:
        build_parser().error(str(error))


def map_options(arguments: argparse.Namespace) -> MapOptions:
    base = (
        MapOptions.standard()
        if arguments.case is None
        else situation_named(arguments.case).options
    )
    return base.overridden_by(arguments)


def _session(arguments: argparse.Namespace) -> Session:
    with _bad_input_is_a_message():
        return map_options(arguments).session()


def run_optimization(arguments: argparse.Namespace) -> int:
    session = _session(arguments)
    state = session.run(RunRequest(iterations=int(arguments.iterations)))
    summary = write_result(arguments.out, session, state)
    print(json.dumps(summary, indent=2))
    return 0


def run_service(arguments: argparse.Namespace) -> int:
    settings = ServiceSettings(host=arguments.host, port=arguments.port)
    serve(_session(arguments), settings)
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


def window_config(arguments: argparse.Namespace) -> GuiConfig:
    with _bad_input_is_a_message():
        return GuiConfig.of(map_options(arguments), int(arguments.iterations))


def open_window(arguments: argparse.Namespace) -> int:
    config = window_config(arguments)
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
