import numpy as np

from emitter_optimizer.kernel.placement.exact import Instance
from emitter_optimizer.maps.cases import situation_named

RADII = {
    "garden": 6.0,
    "beach": 29.0,
    "marina": 20.0,
    "harbor": 32.0,
    "ramparts": 140.0,
}
WEIGHT_LEVELS = 100


def case_instance(name: str) -> Instance:
    """A published map, its law reduced to the disk one emitter serves on its own."""
    situation = situation_named(name)
    scene = situation.scene
    measure = np.asarray(scene.measure, dtype=np.float64)
    served = measure > 0.0
    walls = np.asarray(scene.walls, dtype=np.float64)
    long_enough = np.linalg.norm(walls[:, 1] - walls[:, 0], axis=1) > 0.0
    bounds = np.asarray(scene.bounds, dtype=np.float64)
    return Instance(
        name=name,
        points=np.asarray(scene.points, dtype=np.float64)[served],
        weights=np.maximum(
            1, np.round(measure[served] / measure.max() * WEIGHT_LEVELS)
        ).astype(np.int64),
        walls=walls[long_enough],
        radius=RADII[name],
        emitters=situation.emitters,
        width=float(bounds[0]),
        height=float(bounds[1]),
    )
