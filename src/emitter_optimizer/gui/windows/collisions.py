from dataclasses import dataclass
from pathlib import Path

import dearpygui.dearpygui as dpg

from emitter_optimizer.gui.configuration import GuiConfig
from emitter_optimizer.gui.dialogs import FileDialog, show_info
from emitter_optimizer.maps import Walls
from emitter_optimizer.render.texture import (
    CSV_EXTENSIONS,
    IMAGE_EXTENSIONS,
    segments_texture,
)

TEXTURE_SIZE = (200, 200)
OPAQUE_TEXTURE = [1.0] * (TEXTURE_SIZE[0] * TEXTURE_SIZE[1] * 4)
INPUT = "input_text_collision_map"
TEXTURE = "collision_texture_tag"


@dataclass
class CollisionsWindow:
    config: GuiConfig

    def __call__(self, _tag: str) -> None:
        with dpg.group(horizontal=True):
            dpg.add_text("Collision map")
            dpg.add_input_text(multiline=False, width=250, tag=INPUT)
            dpg.add_button(label="Browse", callback=self._browse, user_data=INPUT)

        with dpg.group(horizontal=True):
            dpg.add_button(label="Load", callback=self._load)
            dpg.add_button(label="Remove", callback=self._remove)

        with dpg.texture_registry(show=False):
            dpg.add_dynamic_texture(
                width=TEXTURE_SIZE[0],
                height=TEXTURE_SIZE[1],
                default_value=self.texture(),
                tag=TEXTURE,
            )
        dpg.add_image(
            TEXTURE,
            width=TEXTURE_SIZE[0],
            height=TEXTURE_SIZE[1],
        )

    def texture(self) -> list[float]:
        walls = self.config.walls
        if walls is None:
            return OPAQUE_TEXTURE
        return segments_texture(walls.segments, TEXTURE_SIZE)

    def _browse(self, _sender: object, _app_data: object, user_data: str) -> None:
        FileDialog(user_data, (IMAGE_EXTENSIONS, CSV_EXTENSIONS)).open()

    def _load(self, _sender: object, _app_data: object, _user_data: object) -> None:
        try:
            self.config.walls = Walls.load(Path(dpg.get_value(INPUT)))
        except OSError, ValueError:
            show_info("Unreadable collision map", "Warning")
            return
        dpg.set_value(TEXTURE, self.texture())

    def _remove(self, _sender: object, _app_data: object, _user_data: object) -> None:
        self.config.walls = None
        dpg.set_value(TEXTURE, self.texture())
