from emitter_optimizer.gui.application import Application
from emitter_optimizer.gui.configuration import GuiConfig


def test_every_window_of_the_layout_has_a_content() -> None:
    application = Application(GuiConfig())

    declared = {window.content for window in application.layout.windows}

    assert declared == set(application.windows)
