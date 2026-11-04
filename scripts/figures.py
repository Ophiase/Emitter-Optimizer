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
    Physics,
    Scene,
    Step,
)
from emitter_optimizer.maps.cases import Situation
from emitter_optimizer.render import ChartImage, MapImage, ProblemImage
from emitter_optimizer.service.evaluated_law import EvaluatedLaw
from emitter_optimizer.service.options import MapOptions
from emitter_optimizer.service.paths import (
    DEFAULT_EMITTER_FUNCTION,
    DEFAULT_SENSOR_FUNCTION,
    PROJECT_ROOT,
)
from scripts.situations import measure, situations

FIGURES = PROJECT_ROOT / "docs" / "figures"
EMITTERS = 15
ITERATIONS = 200
STEP_SIZE = 0.01
CASE_ITERATIONS = 20
PHYSICS = Physics(
    emitter=EvaluatedLaw.from_file(DEFAULT_EMITTER_FUNCTION),
    sensor=EvaluatedLaw.from_file(DEFAULT_SENSOR_FUNCTION),
)


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
        duration=120,
        loop=0,
    )
    return buffer.getvalue()


def _case_gif(image: MapImage, start: np.ndarray, steps: list[np.ndarray]) -> bytes:
    frames = [Image.open(BytesIO(image.png(start)))]
    frames.extend(Image.open(BytesIO(image.png(step))) for step in steps)
    buffer = BytesIO()
    frames[0].save(
        buffer,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=300,
        loop=0,
    )
    return buffer.getvalue()


def _case(situation: Situation) -> bytes:
    steps: list[np.ndarray] = []

    def capture(step: Step) -> None:
        steps.append(np.asarray(step.positions))

    result = measure(
        situation,
        iterations=CASE_ITERATIONS,
        report_every=2,
        on_step=capture,
    )
    coverage = Coverage(situation.scene, HardOcclusion(), situation.physics)
    image = MapImage(situation.scene, coverage, width=400)
    return _case_gif(image, result.start, steps)


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
    steps: list[np.ndarray] = []
    settings = DescentSettings(
        emitters=EMITTERS,
        steps=ITERATIONS,
        step_size=STEP_SIZE,
        report_every=10,
    )

    def on_step(step: Step) -> None:
        steps.append(np.asarray(step.positions))

    result = Descender(scene, PHYSICS, settings, on_step=on_step).run()
    before = MapImage(scene, coverage).png(start)
    (FIGURES / "before.png").write_bytes(before)
    (FIGURES / "problem.png").write_bytes(
        ProblemImage(scene, coverage, width=600).png(start)
    )
    (FIGURES / "after.png").write_bytes(MapImage(scene, coverage).png(result.positions))
    (FIGURES / "gain.png").write_bytes(ChartImage(result.history).png())
    (FIGURES / "descent.gif").write_bytes(_gif(start, steps, scene))
    for situation in situations():
        (FIGURES / f"case_{situation.name}.gif").write_bytes(_case(situation))


if __name__ == "__main__":
    main()
