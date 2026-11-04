import time
from io import BytesIO

import jax
import jax.numpy as jnp
import numpy as np
from PIL import Image

from emitter_optimizer.kernel import (
    Coverage,
    Descender,
    DescentSettings,
    Greedy,
    HardOcclusion,
    Physics,
    Step,
    Volume,
)
from emitter_optimizer.render import FloorsImage
from emitter_optimizer.service.paths import PROJECT_ROOT

FIGURES = PROJECT_ROOT / "docs" / "figures"
LENGTHS = (40.0, 24.0, 9.0)
GRID = (30, 18, 9)
STOREYS = 3
LAYERS_PER_STOREY = GRID[2] // STOREYS
EMITTERS = 6
WALL = 0.9
FLOOR = 1.6
SAMPLES = 16
NOISE = 0.05
HALF_POWER = 4.0
CORRIDOR = (7, 11)
WALL_ROWS = (CORRIDOR[0] - 1, CORRIDOR[1])
WALL_COLUMNS = (5, 10, 15, 20, 25)

PHYSICS = Physics(
    emitter=lambda distance: 1.0 / (1.0 + (distance / HALF_POWER) ** 2),
    sensor=lambda signal: jnp.log1p(signal / NOISE) / jnp.log1p(1.0 / NOISE),
)


def building() -> Volume:
    """Offices along a corridor on three storeys, of walls with doors, no window."""
    absorption = np.zeros(GRID)
    density = np.zeros(GRID)
    for storey in range(STOREYS):
        bottom = storey * LAYERS_PER_STOREY
        eye = bottom + 1
        plan = absorption[:, :, bottom : bottom + LAYERS_PER_STOREY]
        plan[:, WALL_ROWS, :] = WALL
        plan[np.ix_(WALL_COLUMNS, range(WALL_ROWS[0]))] = WALL
        plan[np.ix_(WALL_COLUMNS, range(WALL_ROWS[1], GRID[1]))] = WALL
        for door in range(2, GRID[0], 5):
            plan[door, WALL_ROWS, :] = 0.0
        absorption[:, :, bottom] = FLOOR
        offices = np.ones(GRID[:2])
        offices[:, CORRIDOR[0] - 1 : CORRIDOR[1] + 1] = 0.0
        density[:, :, eye] = offices * (1.0 + storey * 0.5)
    return Volume.of(
        LENGTHS, GRID, jnp.asarray(density), jnp.asarray(absorption), samples=SAMPLES
    )


def main() -> None:
    volume = building()
    coverage = Coverage(volume, HardOcclusion(), PHYSICS)
    draws = volume.sample(jax.random.key(1), 8, EMITTERS)
    random = float(np.mean([coverage.gain(draw) for draw in draws]))
    started = time.perf_counter()
    candidates = volume.lattice((3, 3, 3))
    guess = Greedy(volume, PHYSICS, candidates).place(EMITTERS)
    greedy_seconds = time.perf_counter() - started
    steps: list[np.ndarray] = []

    def capture(step: Step) -> None:
        steps.append(np.asarray(step.positions))

    started = time.perf_counter()
    free = Descender(
        volume,
        PHYSICS,
        DescentSettings(EMITTERS, 150, starts=3, report_every=5, step_size=0.02),
        on_step=capture,
    ).run()
    free_seconds = time.perf_counter() - started
    polish = Descender(
        volume,
        PHYSICS,
        DescentSettings(EMITTERS, 150, report_every=25, step_size=0.005),
        start=guess[None],
    ).run()
    best = max(free, polish, key=lambda result: result.gain)
    print(
        f"random {random:.4f} greedy {float(coverage.gain(guess)):.4f} "
        f"({greedy_seconds:.0f}s) free {free.gain:.4f} ({free_seconds:.0f}s) "
        f"polish {polish.gain:.4f}",
        flush=True,
    )
    image = FloorsImage(volume, coverage, STOREYS, panel_width=300)
    (FIGURES / "layers_building.png").write_bytes(image.demand_png(best.positions))
    (FIGURES / "building_solved.png").write_bytes(image.png(best.positions))
    frames = [Image.open(BytesIO(image.png(step))) for step in steps[::2]]
    frames.append(Image.open(BytesIO(image.png(best.positions))))
    buffer = BytesIO()
    frames[0].save(
        buffer,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=140,
        loop=0,
    )
    (FIGURES / "case_building.gif").write_bytes(buffer.getvalue())


if __name__ == "__main__":
    main()
