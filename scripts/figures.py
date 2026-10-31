import io
from collections.abc import Sequence

import numpy as np
from matplotlib.figure import Figure
from PIL import Image

from emitter_optimizer.engine.laws import load_law_file
from emitter_optimizer.engine.maps import load_collisions, load_density
from emitter_optimizer.engine.solver import Solver
from emitter_optimizer.paths import (
    DEFAULT_EMITTER_FUNCTION,
    DEFAULT_SENSOR_FUNCTION,
    PROJECT_ROOT,
)

OUTPUT = PROJECT_ROOT / "docs" / "figures"
RESOURCES = PROJECT_ROOT / "resources" / "map"
ITERATIONS = 200
EMITTERS = 15
SEED = 0
UPDATE_RATE = 5
GIF_DURATION = 80
FIGURE_SIZE = (6, 4)


def build_solver() -> Solver:
    return Solver(
        n_emitters=EMITTERS,
        density_map=load_density(RESOURCES / "value_001.png"),
        collision_map=load_collisions(RESOURCES / "collide_001.png"),
        map_scale=(100.0, 100.0),
        grid_size=(32, 32),
        emitter_law=load_law_file(DEFAULT_EMITTER_FUNCTION),
        sensor_law=load_law_file(DEFAULT_SENSOR_FUNCTION),
        n_iteration=ITERATIONS,
        epsilon=1.0,
        seed=SEED,
        update_rate=UPDATE_RATE,
    )


def history_figure(history: Sequence[float]) -> Figure:
    figure = Figure(figsize=FIGURE_SIZE)
    axes = figure.add_subplot(1, 1, 1)
    axes.plot([-value for value in history])
    axes.set_xlabel("iteration")
    axes.set_ylabel("gain")
    axes.set_title("Gain, iteration after iteration")
    axes.grid(visible=True)
    return figure


def png_bytes(figure: Figure) -> bytes:
    buffer = io.BytesIO()
    figure.savefig(buffer, format="png")
    return buffer.getvalue()


def frame_image(figure: Figure) -> Image.Image:
    return Image.open(io.BytesIO(png_bytes(figure))).convert("RGB")


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    solver = build_solver()
    start = np.array(solver.emitters_positions, copy=True)
    frames: list[Image.Image] = []

    def capture(emitters: np.ndarray | None, _history: list[float] | None) -> None:
        if emitters is None:
            return
        frames.append(frame_image(solver.make_fig(emitters)))

    solver.update_callback = capture
    solver.solve()

    solver.make_fig(start).savefig(OUTPUT / "before.png")
    solver.make_fig().savefig(OUTPUT / "after.png")
    history_figure(solver.history).savefig(OUTPUT / "gain.png")
    frames[0].save(
        OUTPUT / "descent.gif",
        save_all=True,
        append_images=frames[1:],
        duration=GIF_DURATION,
        loop=0,
    )
    print(f"{OUTPUT} · {len(frames)} frames")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
