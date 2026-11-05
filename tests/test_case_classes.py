import jax.numpy as jnp
import numpy as np
import pytest

from emitter_optimizer.maps.cases import situation_named

CURVATURE_TOLERANCE = 1e-5
CLASSES = {
    "beach": ("rising", True),
    "marina": ("rising", True),
    "garden": ("dome", True),
    "harbor": ("rising", False),
    "ramparts": ("rising", False),
}


@pytest.mark.parametrize("name", CLASSES)
def test_each_case_sensor_has_the_published_shape(name: str) -> None:
    situation = situation_named(name)
    largest = float(situation.physics.emitter(jnp.zeros(1))[0]) * situation.emitters
    signal = jnp.linspace(0.0, largest, 4001)
    scores = np.asarray(situation.physics.sensor(signal), dtype=np.float64)
    slope, curvature = np.diff(scores), np.diff(scores, n=2)
    shape, concave = CLASSES[name]

    assert (np.all(slope >= -1e-6)) == (shape == "rising")
    assert (np.max(curvature) <= CURVATURE_TOLERANCE * np.ptp(scores)) == concave
    assert np.all(
        np.asarray(situation.physics.emitter(jnp.linspace(0.0, 500.0, 500))) >= 0.0
    )
