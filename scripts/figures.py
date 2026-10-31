from io import BytesIO

import jax
import numpy as np
from PIL import Image

from emitter_optimizer.kernel import (
    Coverage,
    Descender,
    DescentSettings,
    Extent,
    GridShape,
    HardOcclusion,
    Scene,
    Step,
)
from emitter_optimizer.paths import (
    DEFAULT_EMITTER_FUNCTION,
    DEFAULT_SENSOR_FUNCTION,
    PROJECT_ROOT,
)
from emitter_optimizer.render import ChartImage, MapImage
from emitter_optimizer.service.options import MapOptions
from scripts.situations import PHYSICS, measure, situations

FIGURES = PROJECT_ROOT / "docs" / "figures"
EMITTERS = 15
ITERATIONS = 200
STEP_SIZE = 0.01


def _sheet(images: list[bytes], columns: int = 3) -> bytes:
    tiles = [Image.open(BytesIO(data)) for data in images]
    width, height = tiles[0].size
    rows = (len(tiles) + columns - 1) // columns
    sheet = Image.new("RGB", (width * columns, height * rows), "#0b0f14")
    for index, tile in enumerate(tiles):
        sheet.paste(tile, ((index % columns) * width, (index // columns) * height))
    buffer = BytesIO()
    sheet.save(buffer, format="PNG")
    return buffer.getvalue()


def _gif(start: np.ndarray, steps: list[np.ndarray], scene: Scene) -> bytes:
    coverage = Coverage(scene, HardOcclusion(), PHYSICS)
    image = MapImage(scene, coverage)
    frames = [Image.open(BytesIO(image.png(start)))]
    frames.extend(Image.open(BytesIO(image.png(step))) for step in steps)
    buffer = BytesIO()
    frames[0].save(
        buffer,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=80,
        loop=0,
    )
    return buffer.getvalue()


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    options = MapOptions(
        extent=Extent(100.0, 100.0),
        grid=GridShape(32, 32),
        emitters=EMITTERS,
        step_size=STEP_SIZE,
        seed=0,
        density_path=PROJECT_ROOT / "resources" / "map" / "value_001.png",
        collisions_path=PROJECT_ROOT / "resources" / "map" / "collide_001.png",
        emitter_law=DEFAULT_EMITTER_FUNCTION,
        sensor_law=DEFAULT_SENSOR_FUNCTION,
    )
    scene = options.scene()
    coverage = Coverage(scene, HardOcclusion(), PHYSICS)
    start = np.asarray(scene.sample(jax.random.key(0), 1, EMITTERS)[0])
    trajectories: list[np.ndarray] = []
    settings = DescentSettings(
        emitters=EMITTERS,
        steps=ITERATIONS,
        step_size=STEP_SIZE,
        report_every=10,
    )

    def on_step(step: Step) -> None:
        trajectories.append(np.asarray(step.positions))

    result = Descender(scene, PHYSICS, settings, on_step=on_step).run()
    before = MapImage(scene, coverage).png(start)
    (FIGURES / "before.png").write_bytes(before)
    (FIGURES / "problem.png").write_bytes(before)
    (FIGURES / "after.png").write_bytes(MapImage(scene, coverage).png(result.positions))
    (FIGURES / "paths.png").write_bytes(
        MapImage(scene, coverage).png(result.positions, trajectories)
    )
    (FIGURES / "gain.png").write_bytes(ChartImage(result.history).png())
    (FIGURES / "descent.gif").write_bytes(_gif(start, trajectories, scene))
    cases: list[bytes] = []
    for situation in situations():
        case = measure(situation, iterations=20)
        cases.append(
            MapImage(
                situation.scene,
                Coverage(situation.scene, HardOcclusion(), PHYSICS),
                size=(300, 200),
            ).png(case.positions)
        )
    (FIGURES / "cases.png").write_bytes(_sheet(cases))


if __name__ == "__main__":
    main()
