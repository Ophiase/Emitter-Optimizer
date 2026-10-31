from dataclasses import dataclass

import dearpygui.dearpygui as dpg

from emitter_optimizer.engine.laws import Positions
from emitter_optimizer.gui.configuration import GuiConfig
from emitter_optimizer.gui.images import figure_texture

TEXTURE_SIZE = (600, 400)
FIGURE_SCALE = 100
FIGURE_SIZE = (TEXTURE_SIZE[0] / FIGURE_SCALE, TEXTURE_SIZE[1] / FIGURE_SCALE)
LOSS_WIDTH = 580
LOSS_HEIGHT = 320
RENDER_TEXTURE = "render_texture_tag"
SIMULATION_TEXT = "simulation_text"
HISTORY_PLOT = "history_plot_tag"


@dataclass
class LossWindow:
    config: GuiConfig

    def __call__(self, _tag: str) -> None:
        dpg.add_simple_plot(
            tag=HISTORY_PLOT,
            default_value=[],
            width=LOSS_WIDTH,
            height=LOSS_HEIGHT,
        )


@dataclass
class RenderWindow:
    config: GuiConfig

    def __call__(self, _tag: str) -> None:
        with dpg.texture_registry(show=False):
            dpg.add_dynamic_texture(
                width=TEXTURE_SIZE[0],
                height=TEXTURE_SIZE[1],
                default_value=self.texture(),
                tag=RENDER_TEXTURE,
            )
        dpg.add_text(self.state(), tag=SIMULATION_TEXT)
        dpg.add_image(
            RENDER_TEXTURE,
            width=TEXTURE_SIZE[0],
            height=TEXTURE_SIZE[1],
        )
        self.config.update_callback = self.update
        self.config.solver.update_callback = self.update

    def state(self) -> str:
        running = "on" if self.config.solver.is_working else "off"
        return f"Simulation : {running}"

    def texture(self, emitters: Positions | None = None) -> list[float]:
        figure = self.config.solver.make_fig(emitters, FIGURE_SIZE)
        return figure_texture(figure)

    def update(
        self,
        emitters: Positions | None = None,
        history: list[float] | None = None,
    ) -> None:
        dpg.set_value(SIMULATION_TEXT, self.state())
        dpg.set_value(RENDER_TEXTURE, self.texture(emitters))
        dpg.set_value(HISTORY_PLOT, history or [])
