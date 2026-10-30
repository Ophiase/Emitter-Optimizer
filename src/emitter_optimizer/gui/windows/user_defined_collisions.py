import cv2
import dearpygui.dearpygui as dpg
import numpy as np

from emitter_optimizer.engine import CollisionMap, MapType
from emitter_optimizer.gui.configuration import GuiConfig
from emitter_optimizer.gui.dpg_utils import IMAGE_EXTENSIONS, DpgUtils

TEXTURE_SIZE = (200, 200)
OPAQUE_TEXTURE = [1.0] * (TEXTURE_SIZE[0] * TEXTURE_SIZE[1] * 4)
SEGMENT_SHAPE = (-1, 2, 2)


class WindowUserDefinedCollisions:
    def __init__(self, config: GuiConfig) -> None:
        self.config = config

    def load_collision_map(self) -> None:
        path = dpg.get_value("input_text_collision_map")
        input_type = MapType.from_string(dpg.get_value("collision_input_radio"))
        storage_type = MapType.from_string(dpg.get_value("collision_storage_radio"))

        if input_type is MapType.GRID:
            data = cv2.imread(path)
        else:
            data = np.loadtxt(path).reshape(SEGMENT_SHAPE)

        if data is None:
            DpgUtils.show_info("Unreadable image", "Warning")
            return

        self.config.collision_map = CollisionMap.from_data(
            data,
            input_type,
            storage_type,
        )
        dpg.set_value("collision_texture_tag", self.get_texture())

    def remove_collision_map(self) -> None:
        self.config.collision_map = None
        dpg.set_value("collision_texture_tag", self.get_texture())

    def get_texture(self) -> list[float]:
        collision_map = self.config.collision_map
        if collision_map is None:
            return OPAQUE_TEXTURE

        image = DpgUtils.draw_segments_on_image(
            collision_map.data,
            (TEXTURE_SIZE[0], TEXTURE_SIZE[1]),
        )
        return DpgUtils.np_image_to_dpg_texture(image)

    def input_radio(self) -> None:
        dpg.add_text("Input data type :")
        dpg.add_radio_button(
            tag="collision_input_radio",
            items=["Grid", "Segments"],
            default_value="Grid",
        )

    def storage_radio(self) -> None:
        dpg.add_text("Algorithmic data type : ")
        dpg.add_radio_button(
            tag="collision_storage_radio",
            items=["Segments"],
            default_value="Segments",
        )

    def process(self, _window_tag: str) -> None:
        with dpg.group(horizontal=True):
            dpg.add_text("Collision map")
            dpg.add_input_text(
                multiline=False,
                width=250,
                tag="input_text_collision_map",
            )
            dpg.add_button(
                label="Browse",
                callback=lambda: DpgUtils.load_path(
                    "input_text_collision_map",
                    [IMAGE_EXTENSIONS],
                ),
            )

        with dpg.group(horizontal=True):
            with dpg.group(horizontal=False):
                dpg.add_button(label="Load", callback=self.load_collision_map)
                dpg.add_button(label="Remove", callback=self.remove_collision_map)
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
                tag="collision_texture_tag",
            )
        dpg.add_image(
            "collision_texture_tag",
            width=TEXTURE_SIZE[0],
            height=TEXTURE_SIZE[1],
        )
