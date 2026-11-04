import jax
import numpy as np

from emitter_optimizer.kernel import (
    Coverage,
    Descender,
    DescentSettings,
    Extent,
    GridShape,
    HardOcclusion,
    Physics,
)
from emitter_optimizer.maps.cases import situation_named
from emitter_optimizer.render import ChartImage, MapImage, ProblemImage
from emitter_optimizer.service.evaluated_law import EvaluatedLaw
from emitter_optimizer.service.options import MapOptions
from emitter_optimizer.service.paths import (
    DEFAULT_EMITTER_FUNCTION,
    DEFAULT_SENSOR_FUNCTION,
    PROJECT_ROOT,
)
from scripts.figures import mosaic, photo_cases, physics_compare
from scripts.situations import situations

FIGURES = PROJECT_ROOT / "docs" / "figures"
EMITTERS = 15
ITERATIONS = 200
STEP_SIZE = 0.01
PHYSICS = Physics(
    emitter=EvaluatedLaw.from_file(DEFAULT_EMITTER_FUNCTION),
    sensor=EvaluatedLaw.from_file(DEFAULT_SENSOR_FUNCTION),
)


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
    settings = DescentSettings(
        emitters=EMITTERS,
        steps=ITERATIONS,
        step_size=STEP_SIZE,
        report_every=10,
    )
    result = Descender(scene, PHYSICS, settings).run()
    before = MapImage(scene, coverage).png(start)
    (FIGURES / "before.png").write_bytes(before)
    (FIGURES / "problem.png").write_bytes(
        ProblemImage(scene, coverage, width=600).png(start)
    )
    (FIGURES / "after.png").write_bytes(MapImage(scene, coverage).png(result.positions))
    (FIGURES / "gain.png").write_bytes(ChartImage(result.history).png())
    for situation in situations():
        print(situation.name, photo_cases.render(situation), "jumps", flush=True)
    physics_compare.render(situation_named("harbor"))
    mosaic.render()


if __name__ == "__main__":
    main()
