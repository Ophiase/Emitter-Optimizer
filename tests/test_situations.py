from scripts.situations import measure, situations


def test_every_case_matches_its_grid() -> None:
    for situation in situations():
        assert situation.scene.grid == situation.grid
        if situation.density is not None:
            assert situation.density.values.shape == (
                situation.grid.rows,
                situation.grid.columns,
            )
        if situation.walls is not None:
            assert situation.walls.segments.min() >= 0.0


def test_a_case_improves_its_gain() -> None:
    result = measure(situations()[0], iterations=6)

    assert result.gain >= result.initial_gain
