import cv2
import dearpygui.dearpygui as dpg
import numpy as np

from emitter_optimizer.engine import DensityMap, MapType
from emitter_optimizer.gui.configuration import GuiConfig
from emitter_optimizer.gui.dpg_utils import IMAGE_EXTENSIONS, DpgUtils

TEXTURE_SIZE = (200, 200)
OPAQUE_TEXTURE = [1.0] * (TEXTURE_SIZE[0] * TEXTURE_SIZE[1] * 4)


class WindowUserDefinedDensity:
    def __init__(self, config: GuiConfig) -> None:
        self.config = config

    def load_density_map(self) -> None:
        path = dpg.get_value("input_text_density_map")
        image = cv2.imread(path)
        if image is None:
            DpgUtils.show_info("Unreadable image", "Warning")
            return

        self.config.density_map = DensityMap.from_data(
            np.mean(image, axis=2) / 255.0,
            MapType.from_string(dpg.get_value("density_input_radio")),
            MapType.from_string(dpg.get_value("density_storage_radio")),
        )
        dpg.set_value("density_texture_tag", self.get_texture())

    def remove_density_map(self) -> None:
        self.config.density_map = None
        dpg.set_value("density_texture_tag", self.get_texture())

    def input_radio(self) -> None:
        dpg.add_text("Input data type :")
        dpg.add_radio_button(
            tag="density_input_radio",
            items=["Grid"],
            default_value="Grid",
        )

    def storage_radio(self) -> None:
        dpg.add_text("Algorithmic data type : ")
        dpg.add_radio_button(
            tag="density_storage_radio",
            items=["Grid"],
            default_value="Grid",
        )

    def get_texture(self) -> list[float]:
        density_map = self.config.density_map
        if density_map is None:
            return OPAQUE_TEXTURE

        return DpgUtils.np_image_to_dpg_texture(
            density_map.data,
            (TEXTURE_SIZE[0], TEXTURE_SIZE[1]),
        )

    def process(self, _window_tag: str) -> None:
        with dpg.group(horizontal=True):
            dpg.add_text("Density map")
            dpg.add_input_text(
                multiline=False,
                width=250,
                tag="input_text_density_map",
            )
            dpg.add_button(
                label="Browse",
                callback=lambda: DpgUtils.load_path(
                    "input_text_density_map",
                    [IMAGE_EXTENSIONS],
                ),
            )

        with dpg.group(horizontal=True):
            with dpg.group(horizontal=False):
                dpg.add_button(label="Load", callback=self.load_density_map)
                dpg.add_button(label="Remove", callback=self.remove_density_map)
            with dpg.group(horizontal=False):
                with dpg.group(horizontal=True):
                    self.input_radio()
                with dpg.group(horizontal=True):
                    self.storage_radio()

        with dpg.texture_registry(show=False):
            dpg.add_dynamic_texture(
                width=TEXTURE_SIZE[0],
                height=TEXTURE_SIZE[1],
                default_value=self.get_texture(),
                tag="density_texture_tag",
            )
        dpg.add_image(
            "density_texture_tag",
            width=TEXTURE_SIZE[0],
            height=TEXTURE_SIZE[1],
        )
