from emitter_optimizer import bench


def test_a_situation_is_measured_and_reported() -> None:
    situation = bench.Situation("tiny", None, None, (10.0, 10.0), (4, 4))

    result = bench.measure(situation, iterations=2, emitters=2, seed=0)
    text = bench.report((result,), iterations=2)

    assert result.situation.cells == 16
    assert result.gain >= result.initial_gain
    assert "| tiny | 16 | 2 |" in text
    assert "Improvement" in text
