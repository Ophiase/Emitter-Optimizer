import json

import numpy as np
import pytest

from emitter_optimizer.kernel.placement.exact import ExactPlacement, Instance
from emitter_optimizer.service.paths import RESOURCES_DIRECTORY
from scripts.certify.family import Family

REFERENCE = RESOURCES_DIRECTORY / "reference" / "coverage-with-walls.json"
RECORDS = json.loads(REFERENCE.read_text(encoding="utf-8"))
SIMPLEST = ("n100-k3-w0-s0", "n100-k5-w4-s1", "n100-k10-w12-s2", "n100-k20-w4-s3")


def _record(name: str) -> dict[str, object]:
    return next(record for record in RECORDS if record["name"] == name)


def test_every_stored_placement_reaches_its_lower_bound() -> None:
    for record in RECORDS:
        instance = Instance.of(record)
        placement = np.asarray(record["placement"])
        assert placement.shape[0] <= instance.emitters
        assert instance.covered_weight(placement) == record["lower"]
        assert record["lower"] <= record["upper"]


@pytest.mark.parametrize("name", SIMPLEST)
def test_a_stored_optimum_solves_to_the_same_value(name: str) -> None:
    record = _record(name)

    certificate = ExactPlacement(Instance.of(record)).solve()

    assert (certificate.lower, certificate.upper) == (record["lower"], record["upper"])


def test_the_generator_still_draws_the_stored_instance() -> None:
    drawn = Family(100, 5, 4).instance(1)
    stored = Instance.of(_record("n100-k5-w4-s1"))

    assert np.array_equal(drawn.points, stored.points)
    assert np.array_equal(drawn.weights, stored.weights)
    assert np.array_equal(drawn.walls, stored.walls)
