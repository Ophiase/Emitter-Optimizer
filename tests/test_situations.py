import numpy as np

from emitter_optimizer.engine.situations import measure, situations, solver_for


def test_every_case_matches_its_grid() -> None:
    for situation in situations():
        solver = solver_for(situation, iterations=1)

        assert solver.field.grid_size == situation.grid_size
        if situation.density is not None:
            assert situation.density.data.shape == situation.grid_size
        if situation.collisions is not None:
            np.testing.assert_array_less(situation.collisions.data, 1.0001)
            assert situation.collisions.data.min() >= 0.0


def test_a_case_improves_its_gain() -> None:
    situation = situations()[0]

    result = measure(situation, iterations=10)

    assert result.gain >= result.initial_gain
