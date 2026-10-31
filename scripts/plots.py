from collections.abc import Sequence

import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from emitter_optimizer.engine.field import Field
from emitter_optimizer.engine.laws import Positions
from emitter_optimizer.engine.situations import Result

WALL_COLOUR = "0.1"
EMITTER_COLOUR = "crimson"
START_COLOUR = "0.45"
CMAP = "plasma"
WALL_WIDTH = 1.4
EMITTER_SIZE = 22
PATH_WIDTH = 0.8
WIDE_FIGURE = (10.0, 4.2)
CASES_FIGURE = (12.0, 6.4)
BENCHMARK_FIGURE = (7.0, 3.6)


def _scale(axes: Axes, field: Field) -> None:
    width, height = field.map_scale
    axes.set_xlim(0, width)
    axes.set_ylim(height, 0)
    axes.set_aspect("equal")


def _walls(axes: Axes, obstacles: np.ndarray | None) -> None:
    if obstacles is None:
        return
    for start, end in obstacles:
        axes.plot(
            [start[0], end[0]],
            [start[1], end[1]],
            color=WALL_COLOUR,
            linewidth=WALL_WIDTH,
            solid_capstyle="round",
        )


def _emitters(axes: Axes, positions: Positions, colour: str = EMITTER_COLOUR) -> None:
    axes.scatter(
        positions[:, 0],
        positions[:, 1],
        s=EMITTER_SIZE,
        color=colour,
        zorder=5,
    )


def _values(axes: Axes, field: Field, positions: Positions) -> None:
    width, height = field.map_scale
    axes.imshow(
        field.value_map(positions),
        aspect="equal",
        origin="upper",
        extent=(0, width, height, 0),
        cmap=CMAP,
    )
    _scale(axes, field)


def _density(axes: Axes, field: Field) -> None:
    width, height = field.map_scale
    density = (
        np.ones(field.grid_size)
        if field.density is None
        else field.density.reshape(field.grid_size)
    )
    axes.imshow(
        density,
        aspect="equal",
        origin="upper",
        extent=(0, width, height, 0),
        cmap="Greys",
    )
    _scale(axes, field)


def comparison_figure(field: Field, positions: Positions) -> Figure:
    figure = Figure(figsize=WIDE_FIGURE)
    demand = figure.add_subplot(1, 2, 1)
    coverage = figure.add_subplot(1, 2, 2)

    _density(demand, field)
    _walls(demand, field.obstacles)
    _emitters(demand, positions)
    demand.set_title("The map: demand, walls, emitters")

    _values(coverage, field, positions)
    _walls(coverage, field.obstacles)
    _emitters(coverage, positions)
    coverage.set_title("The score: what each place receives")
    return figure


def paths_figure(
    field: Field,
    trajectories: Sequence[Positions],
) -> Figure:
    figure = Figure(figsize=WIDE_FIGURE)
    axes = figure.add_subplot(1, 1, 1)
    _values(axes, field, trajectories[-1])
    _walls(axes, field.obstacles)

    emitters = trajectories[0].shape[0]
    for index in range(emitters):
        path = np.array([step[index] for step in trajectories])
        axes.plot(path[:, 0], path[:, 1], color="white", linewidth=PATH_WIDTH)
    _emitters(axes, trajectories[0], START_COLOUR)
    _emitters(axes, trajectories[-1])
    axes.set_title("Each emitter climbs the gain; a wall is not crossed")
    return figure


def cases_figure(results: Sequence[Result]) -> Figure:
    figure = Figure(figsize=CASES_FIGURE)
    for index, result in enumerate(results, start=1):
        axes = figure.add_subplot(2, 3, index)
        solver = result.solver
        _values(axes, solver.field, solver.emitters_positions)
        _walls(axes, solver.field.obstacles)
        _emitters(axes, solver.emitters_positions)
        axes.set_title(
            f"{result.situation.name}  {result.improvement:+.3f}",
            fontsize=10,
        )
    figure.tight_layout()
    return figure


def benchmark_figure(results: Sequence[Result]) -> Figure:
    figure = Figure(figsize=BENCHMARK_FIGURE)
    axes = figure.add_subplot(1, 1, 1)
    names = [result.situation.name for result in results]
    gains = [result.improvement for result in results]
    positions = np.arange(len(names))
    axes.barh(positions, gains, color="tab:blue")
    axes.set_yticks(positions, names)
    axes.invert_yaxis()
    axes.set_xlabel("gain, from the first positions to the last")
    axes.set_title("What the descent gains")
    for position, result in zip(positions, results, strict=True):
        axes.text(
            result.improvement,
            float(position),
            f"  {result.improvement:+.3f} in {result.seconds:.2f} s",
            va="center",
            fontsize=8,
        )
    figure.tight_layout()
    return figure
