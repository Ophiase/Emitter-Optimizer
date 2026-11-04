from collections import Counter
from io import BytesIO

import numpy as np
from PIL import Image

from emitter_optimizer.kernel import Coverage, HardOcclusion
from emitter_optimizer.render import AtomsImage, FloorsImage, GlobeImage
from scripts.spaces import building, urea


def test_the_urea_cell_holds_two_molecules() -> None:
    atoms = urea.atoms()

    assert Counter(atom.element for atom in atoms) == {
        "C": 2,
        "O": 2,
        "N": 4,
        "H": 8,
    }


def test_the_atoms_are_whole_molecules_in_the_drawing() -> None:
    atoms = urea.atoms()
    image = AtomsImage(
        [atom.element for atom in atoms],
        np.stack([atom.position for atom in atoms]),
        urea.CELL,
    )

    assert len(image._bonds(image._whole_molecules())) == 14
    assert image.draw(30.0).size == (520, 520)


def test_a_globe_only_shows_the_emitters_facing_the_viewer() -> None:
    field = np.zeros((8, 16))
    hidden = np.array([[-1.0, 0.0, 0.0]])
    facing = np.array([[1.0, 0.0, 0.0]])
    globe = GlobeImage(field, size=64)

    blank = np.asarray(globe.draw(hidden, latitude=0.0))
    drawn = np.asarray(globe.draw(facing, latitude=0.0))

    assert not np.array_equal(blank, drawn)


def test_the_building_draws_one_panel_per_storey() -> None:
    volume = building.building()
    coverage = Coverage(volume, HardOcclusion(), building.PHYSICS)
    positions = volume.sample(building.jax.random.key(0), 1, 2)[0]

    png = FloorsImage(volume, coverage, building.STOREYS, panel_width=100).demand_png(
        positions
    )

    assert Image.open(BytesIO(png)).width == 3 * 100 + 2 * 8
