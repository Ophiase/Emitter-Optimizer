import json
from typing import Any

import dearpygui.dearpygui as dpg

from emitter_optimizer.gui.configuration import GuiConfig
from emitter_optimizer.gui.windows.loss import WindowLoss
from emitter_optimizer.gui.windows.parameters import WindowParameters
from emitter_optimizer.gui.windows.process import WindowProcess
from emitter_optimizer.gui.windows.render import WindowRender
from emitter_optimizer.gui.windows.user_defined_collisions import (
    WindowUserDefinedCollisions,
)
from emitter_optimizer.gui.windows.user_defined_density import (
    WindowUserDefinedDensity,
)
from emitter_optimizer.gui.windows.user_defined_function import (
    WindowUserDefinedFunction,
)
from emitter_optimizer.paths import DEFAULT_GUI_CONFIGURATION, DEFAULT_GUI_FONT

FONT_SIZE = 20


def load_gui_configuration() -> dict[str, Any]:
    return json.loads(DEFAULT_GUI_CONFIGURATION.read_text(encoding="utf-8"))


class Application:
    def __init__(self) -> None:
        self.config = GuiConfig()
        self.configuration = load_gui_configuration()

        self.windows = {
            "window_loss": WindowLoss(self.config).process,
            "window_parameters": WindowParameters(self.config).process,
            "window_process": WindowProcess(self.config).process,
            "window_render": WindowRender(self.config).process,
            "window_user_defined_collisions": WindowUserDefinedCollisions(
                self.config
            ).process,
            "window_user_defined_density": WindowUserDefinedDensity(
                self.config
            ).process,
            "window_user_defined_emitter": WindowUserDefinedFunction(
                self.config,
                "emitter",
                self.config.DEFAULT_EMITTER_FUNCTION,
                "emitter_function",
            ).process,
            "window_user_defined_sensor": WindowUserDefinedFunction(
                self.config,
                "sensor",
                self.config.DEFAULT_SENSOR_FUNCTION,
                "sensor_function",
            ).process,
        }

        self._run()

    def _run(self) -> None:
        dpg.create_context()

        with dpg.font_registry():
            font = dpg.add_font(str(DEFAULT_GUI_FONT), FONT_SIZE)
        dpg.bind_font(font)

        with dpg.window() as background:
            pass
        dpg.set_primary_window(background, True)

        for window in self.configuration.get("windows", []):
            self._add_window(window)

        viewport = self.configuration["viewport"]
        dpg.create_viewport(
            width=viewport["width"],
            height=viewport["height"],
            title=viewport["title"],
            min_width=viewport["min_width"],
            min_height=viewport["min_height"],
        )
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    def _add_window(self, window: dict[str, Any]) -> None:
        with dpg.window(
            label=window["label"],
            tag=window["tag"],
            no_close=window.get("no_close", False),
            width=window["width"],
            height=window["height"],
            pos=window.get("position", [0, 0]),
            show=window.get("show", True),
            modal=window.get("modal", False),
            no_title_bar=window.get("no_title_bar", False),
        ):
            content = self.windows.get(window["content"])
            if content is not None:
                content(window["tag"])
