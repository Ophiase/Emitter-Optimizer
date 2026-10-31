from dataclasses import dataclass
from pathlib import Path

import dearpygui.dearpygui as dpg

from emitter_optimizer.engine.maps import load_density
from emitter_optimizer.gui.configuration import GuiConfig
from emitter_optimizer.gui.dialogs import FileDialog, show_info
from emitter_optimizer.gui.images import IMAGE_EXTENSIONS, array_texture

TEXTURE_SIZE = (200, 200)
OPAQUE_TEXTURE = [1.0] * (TEXTURE_SIZE[0] * TEXTURE_SIZE[1] * 4)
INPUT = "input_text_density_map"
TEXTURE = "density_texture_tag"


@dataclass
class DensityWindow:
    config: GuiConfig

    def __call__(self, _tag: str) -> None:
        with dpg.group(horizontal=True):
            dpg.add_text("Density map")
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
        density = self.config.density_map
        if density is None:
            return OPAQUE_TEXTURE
        return array_texture(density.data, (TEXTURE_SIZE[0], TEXTURE_SIZE[1]))

    def _browse(self, _sender: object, _app_data: object, user_data: str) -> None:
        FileDialog(user_data, (IMAGE_EXTENSIONS,)).open()

    def _load(self, _sender: object, _app_data: object, _user_data: object) -> None:
        try:
            self.config.density_map = load_density(Path(dpg.get_value(INPUT)))
        except OSError, ValueError:
            show_info("Unreadable image", "Warning")
            return
        dpg.set_value(TEXTURE, self.texture())

    def _remove(self, _sender: object, _app_data: object, _user_data: object) -> None:
        self.config.density_map = None
        dpg.set_value(TEXTURE, self.texture())
