import numpy as np
from PIL import Image

from scripts.situations import measure, situations


def test_every_layer_has_the_resolution_of_its_photograph() -> None:
    for situation in situations():
        size = Image.open(situation.source).size
        for layer in ("attraction.png", "collision.png"):
            assert Image.open(situation.folder / layer).size == size


def test_every_case_matches_its_grid() -> None:
    for situation in situations():
        scene = situation.scene
        bounds = np.array([situation.extent.width, situation.extent.height])
        assert scene.grid == situation.grid
        assert np.asarray(scene.walls).size > 0
        assert np.all(np.asarray(scene.walls) >= 0.0)
        assert np.all(np.asarray(scene.walls) <= bounds)


def test_a_case_improves_its_gain() -> None:
    result = measure(situations()[0], iterations=6)

    assert result.gain >= result.initial_gain
