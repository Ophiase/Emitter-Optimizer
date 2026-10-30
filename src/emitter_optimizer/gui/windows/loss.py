import dearpygui.dearpygui as dpg

from emitter_optimizer.gui.configuration import GuiConfig


class WindowLoss:
    def __init__(self, config: GuiConfig) -> None:
        self.config = config

    def process(self, _window_tag: str) -> None:
        dpg.add_simple_plot(
            tag="history_plot_tag",
            default_value=[],
            width=580,
            height=320,
        )
