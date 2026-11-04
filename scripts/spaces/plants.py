import jax
import jax.numpy as jnp
import numpy as np
from PIL import Image, ImageDraw

from emitter_optimizer.kernel import (
    Coverage,
    Descender,
    DescentSettings,
    Extent,
    Greedy,
    GridShape,
    HardOcclusion,
    Physics,
    Relocation,
    Scene,
    Step,
)
from emitter_optimizer.service.paths import PROJECT_ROOT

FIGURES = PROJECT_ROOT / "docs" / "figures"
EXTENT = Extent(30.0, 20.0)
GRID = GridShape(40, 60)
PLANTS = 70
SOURCES = 5
REACH = 3.0
THIRST = 3.0
STEPS = 200
EVERY = 5
RANDOM_DRAWS = 32
WIDTH = 720
SOIL = np.array((92, 68, 46))
WATER = np.array((60, 140, 230))
DRY = np.array((190, 160, 70))
LUSH = np.array((60, 170, 70))
PLANT_RADIUS = 9.0
HOLD_MILLISECONDS = 2400
FRAME_MILLISECONDS = 70
JUMP_MILLISECONDS = 350

PHYSICS = Physics(
    emitter=lambda distance: jnp.exp(-((distance / REACH) ** 2)),
    sensor=lambda signal: 1.0 - jnp.exp(-THIRST * signal),
)


def field() -> Scene:
    """Three patches of plants on bare soil; a cell holds one plant or none."""
    generator = np.random.default_rng(0)
    centres = np.array([[8.0, 6.0], [22.0, 5.0], [15.0, 15.0]])
    density = np.zeros((GRID.rows, GRID.columns))
    while density.sum() < PLANTS:
        centre = centres[generator.integers(len(centres))]
        x, y = generator.normal(centre, 3.2)
        row = int(y / EXTENT.height * GRID.rows)
        column = int(x / EXTENT.width * GRID.columns)
        if 0 <= row < GRID.rows and 0 <= column < GRID.columns:
            density[row, column] = 1.0
    return Scene.of(EXTENT, GRID, jnp.asarray(density))


def growth(scene: Scene, positions: jax.Array) -> np.ndarray:
    """How far each plant has grown, from 0 to 1, in the order of its cell."""
    received = jnp.sum(
        Coverage(scene, HardOcclusion(), PHYSICS).sent(positions), axis=1
    )
    grown = np.asarray(PHYSICS.sensor(received))
    return grown[np.asarray(scene.measure) > 0]


def _disc(x: float, y: float, radius: float) -> tuple[float, float, float, float]:
    return (x - radius, y - radius, x + radius, y + radius)


def _frame(scene: Scene, positions: np.ndarray) -> Image.Image:
    height = round(WIDTH * EXTENT.height / EXTENT.width)
    image = Image.new("RGB", (WIDTH, height), tuple(int(c) for c in SOIL))
    draw = ImageDraw.Draw(image, "RGBA")
    scale = WIDTH / EXTENT.width
    for x, y in positions:
        for ring, alpha in ((REACH, 40), (REACH / 2, 70)):
            radius = ring * scale
            draw.ellipse(
                (
                    x * scale - radius,
                    y * scale - radius,
                    x * scale + radius,
                    y * scale + radius,
                ),
                fill=(int(WATER[0]), int(WATER[1]), int(WATER[2]), alpha),
            )
    planted = np.asarray(scene.points)[np.asarray(scene.measure) > 0]
    grown = growth(scene, jnp.asarray(positions))
    for (x, y), share in zip(planted, grown, strict=True):
        colour = tuple(int(c) for c in DRY + (LUSH - DRY) * share)
        radius = 2.0 + PLANT_RADIUS * float(share)
        draw.ellipse(
            (
                x * scale - radius,
                y * scale - radius,
                x * scale + radius,
                y * scale + radius,
            ),
            fill=colour,
            outline=(20, 50, 20, 255),
        )
    for x, y in positions:
        draw.ellipse(
            (x * scale - 7, y * scale - 7, x * scale + 7, y * scale + 7),
            fill=(30, 100, 220, 255),
            outline=(255, 255, 255, 255),
            width=2,
        )
    return image


def _mean_growth(scene: Scene, positions: jax.Array) -> float:
    return 100.0 * float(np.mean(growth(scene, positions)))


def main() -> None:
    scene = field()
    draws = scene.sample(jax.random.key(1), RANDOM_DRAWS, SOURCES)
    random = np.mean([_mean_growth(scene, draw) for draw in draws])
    greedy = Greedy(scene, PHYSICS).place(SOURCES)
    start = scene.sample(jax.random.key(0), 1, SOURCES)
    path = [np.asarray(start[0])]

    def capture(step: Step) -> None:
        path.append(np.asarray(step.positions))

    descent = Descender(
        scene,
        PHYSICS,
        DescentSettings(SOURCES, STEPS, report_every=EVERY),
        on_step=capture,
        start=start,
    ).run()
    first_jump = len(path)
    current = descent.positions
    for placed in Relocation(scene, PHYSICS).jumps(current):
        current = placed
        path.append(np.asarray(placed))
    jumps = len(path) - first_jump
    polish = Descender(
        scene,
        PHYSICS,
        DescentSettings(SOURCES, STEPS, step_size=0.003, report_every=STEPS),
        start=current[None],
    ).run()
    path.append(np.asarray(polish.positions))
    print(
        f"random {random:.1f}% greedy {_mean_growth(scene, greedy):.1f}% "
        f"descent {_mean_growth(scene, descent.positions):.1f}% "
        f"relocated {_mean_growth(scene, polish.positions):.1f}% jumps {jumps}"
    )
    frames = [_frame(scene, positions) for positions in path]
    durations = [
        JUMP_MILLISECONDS
        if first_jump <= index < first_jump + jumps
        else FRAME_MILLISECONDS
        for index in range(len(frames))
    ]
    durations[-1] = HOLD_MILLISECONDS
    frames[0].save(
        FIGURES / "case_plants.webp",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        quality=75,
        method=4,
    )
    sheet = Image.new("RGB", (frames[0].width * 2 + 8, frames[0].height), "white")
    sheet.paste(frames[0], (0, 0))
    sheet.paste(frames[-1], (frames[0].width + 8, 0))
    sheet.save(FIGURES / "plants_before_after.jpg", quality=88)


if __name__ == "__main__":
    main()
