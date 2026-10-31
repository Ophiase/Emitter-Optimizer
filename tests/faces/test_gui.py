from emitter_optimizer.gui.application import Application
from emitter_optimizer.gui.configuration import GuiConfig


def test_the_window_builds_its_layout_and_uses_the_kernel() -> None:
    config = GuiConfig(emitter_count=2, iteration_count=2)

    assert len(Application(config).layout.windows) == 8

    config.solver.solve()

    assert config.solver.positions.shape == (2, 2)
    assert config.solver.history
    assert config.solver.figure().startswith(b"\x89PNG")
