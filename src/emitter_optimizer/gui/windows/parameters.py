from dataclasses import dataclass

import dearpygui.dearpygui as dpg

from emitter_optimizer.gui.configuration import GuiConfig
from emitter_optimizer.gui.widgets import separator, show_item

PARAMETERS_WIDTH = 200
RATE_WIDTH = 120
EMITTERS_WIDTH = 140
SAVE_BUTTON = "save_button"
LOSS_ITEM = "loss"


@dataclass
class ParametersWindow:
    config: GuiConfig

    def __call__(self, _tag: str) -> None:
        with dpg.group(horizontal=True):
            with dpg.group(horizontal=False):
                dpg.add_text("Map scale : ")
                dpg.add_text("Grid size : ")
            with dpg.group(horizontal=False):
                dpg.add_input_floatx(
                    size=2,
                    default_value=self.config.map_scale,
                    callback=self._set_map_scale,
                )
                dpg.add_input_intx(
                    size=2,
                    default_value=self.config.grid_size,
                    callback=self._set_grid_size,
                )

        separator()

        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Manage density map",
                callback=self._show,
                user_data="user_defined_density",
            )
            dpg.add_button(
                label="Manage collisions map",
                callback=self._show,
                user_data="user_defined_collisions",
            )

        separator()

        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Edit the emitter function",
                callback=self._show,
                user_data="user_defined_emitter",
            )
            dpg.add_button(
                label="Edit the sensor function",
                callback=self._show,
                user_data="user_defined_sensor",
            )

        separator()

        with dpg.group(horizontal=True):
            dpg.add_text("Number of emitters")
            dpg.add_input_int(
                min_value=1,
                default_value=self.config.emitter_count,
                width=EMITTERS_WIDTH,
                callback=self._set_emitter_count,
            )

    def _show(
        self,
        _sender: object,
        _app_data: object,
        user_data: str,
    ) -> None:
        show_item(user_data, self.config.ITEMS_TO_HIDE)

    def _set_map_scale(
        self,
        _sender: object,
        value: list[float],
        _user_data: object,
    ) -> None:
        self.config.map_scale = (value[0], value[1])

    def _set_grid_size(
        self,
        _sender: object,
        value: list[int],
        _user_data: object,
    ) -> None:
        self.config.grid_size = (value[0], value[1])

    def _set_emitter_count(
        self,
        _sender: object,
        value: int,
        _user_data: object,
    ) -> None:
        self.config.emitter_count = value
