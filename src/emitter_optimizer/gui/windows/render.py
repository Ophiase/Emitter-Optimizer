import dearpygui.dearpygui as dpg

from emitter_optimizer.engine.solver import Positions
from emitter_optimizer.gui.configuration import GuiConfig
from emitter_optimizer.gui.dpg_utils import DpgUtils

TEXTURE_SIZE = (600, 400)
FIGURE_SCALE = 100
FIGURE_SIZE = (TEXTURE_SIZE[0] / FIGURE_SCALE, TEXTURE_SIZE[1] / FIGURE_SCALE)


class WindowRender:
    def __init__(self, config: GuiConfig) -> None:
        self.config = config

    def simulation_state(self) -> str:
        state = "on" if self.config.solver.is_working else "off"
        return f"Simulation : {state}"

    def get_texture(self, emitters: Positions | None = None) -> list[float]:
        figure = self.config.solver.make_fig(emitters, FIGURE_SIZE)
        return DpgUtils.fig_to_dpg_texture(figure)

    def update(
        self,
        emitters: Positions | None = None,
        history: list[float] | None = None,
    ) -> None:
        dpg.set_value("simulation_text", self.simulation_state())
        dpg.set_value("render_texture_tag", self.get_texture(emitters))
        dpg.set_value("history_plot_tag", history or [])

    def process(self, _window_tag: str) -> None:
        with dpg.texture_registry(show=False):
            dpg.add_dynamic_texture(
                width=TEXTURE_SIZE[0],
                height=TEXTURE_SIZE[1],
                default_value=self.get_texture(),
                tag="render_texture_tag",
            )

        dpg.add_text(self.simulation_state(), tag="simulation_text")
        dpg.add_image(
            "render_texture_tag",
            width=TEXTURE_SIZE[0],
            height=TEXTURE_SIZE[1],
        )

        self.config.update_callback = self.update
        self.config.solver.update_callback = self.update
