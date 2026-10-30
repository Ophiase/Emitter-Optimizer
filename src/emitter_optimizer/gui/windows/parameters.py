import dearpygui.dearpygui as dpg

from emitter_optimizer.gui.configuration import GuiConfig
from emitter_optimizer.gui.dpg_utils import DpgUtils


class WindowParameters:
    def __init__(self, config: GuiConfig) -> None:
        self.config = config

    def set_map_scale(self, _: object, value: list[float]) -> None:
        self.config.map_scale = (value[0], value[1])

    def set_grid_size(self, _: object, value: list[int]) -> None:
        self.config.grid_size = (value[0], value[1])

    def set_emitter_count(self, _: object, value: int) -> None:
        self.config.n_emitters = value

    def _show(self, item: str) -> None:
        DpgUtils.show_item(item, items_to_hide=self.config.ITEMS_TO_HIDE)

    def process(self, _window_tag: str) -> None:
        with dpg.group(horizontal=True):
            with dpg.group(horizontal=False):
                dpg.add_text("Map scale : ")
                dpg.add_text("Grid size : ")
            with dpg.group(horizontal=False):
                dpg.add_input_floatx(
                    size=2,
                    default_value=self.config.map_scale,
                    callback=self.set_map_scale,
                )
                dpg.add_input_intx(
                    size=2,
                    default_value=self.config.grid_size,
                    callback=self.set_grid_size,
                )

        DpgUtils.separator()

        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Manage density map",
                callback=lambda: self._show("user_defined_density"),
            )
            dpg.add_button(
                label="Manage collisions map",
                callback=lambda: self._show("user_defined_collisions"),
            )

        DpgUtils.separator()

        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Edit the emitter function",
                callback=lambda: self._show("user_defined_emitter"),
            )
            dpg.add_button(
                label="Edit the sensor function",
                callback=lambda: self._show("user_defined_sensor"),
            )

        DpgUtils.separator()

        with dpg.group(horizontal=True):
            dpg.add_text(default_value="Number of emitters")
            dpg.add_input_int(
                min_value=1,
                default_value=self.config.n_emitters,
                width=140,
                callback=self.set_emitter_count,
            )
