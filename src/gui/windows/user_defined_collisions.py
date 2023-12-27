import dearpygui.dearpygui as dpg
import tensorflow as tf
import matplotlib.pyplot as plt
from threading import Thread
import cv2

from gui.configuration import GuiConfig
from gui.dpg_utils import DpgUtils

from engine.solver import Solver
from engine.map_type import MapType
from engine.density_map import DensityMap
from engine.collision_map import CollisionMap

TEXTURE_SIZE = (200, 200)

class WindowUserDefinedCollisions:
    def __init__(self, config : GuiConfig):
        self.config = config

    def load_collision_map(self):
        path = dpg.get_value("input_text_collision_map")
        
        input_types = [MapType.GRID]
        input_type = input_types[
            int(dpg.get_value("collision_input_radio"))]

        storage_types = [MapType.SEGMENTS]
        storage_type = storage_types[
            int(dpg.get_value("collision_storage_radio"))]

        match (input_type) :
            case MapType.GRID :
                data = cv2.imread(path)
                
                if data is None:
                    DpgUtils.show_info('Unreadable image', 'Warning')
                    return
                else :
                    self.config.collision_map = CollisionMap(
                        data, input_type, storage_type)
                    dpg.set_value("collision_texture_tag", self.get_texture())
                    return
            case MapType.SEGMENTS :
                raise NotImplementedError() # TODO
            case _ :
                raise NotImplementedError()
        

    def remove_collision_map(self):
        self.config.collision_map = None
        dpg.set_value("collision_texture_tag", self.get_texture())

    def get_texture(self) :
        if self.config.collision_map is None :
            return [1.0 for i in range(
                TEXTURE_SIZE[0]*TEXTURE_SIZE[1]*4
                )]

        match self.config.collision_map.storage_type :
            case MapType.SEGMENTS :
                image = DpgUtils.draw_segments_on_image(
                    self.config.collision_map.data, TEXTURE_SIZE)
                print(image.shape)
                return DpgUtils.np_image_to_dpg_texture(image)
            
            case _ :
                raise NotImplementedError()

    def process(self, window_tag) -> None:

        with dpg.group(horizontal=True) :
            dpg.add_text("Collision map")
            dpg.add_input_text(multiline=False, width=250,
                tag="input_text_collision_map")
            dpg.add_button(label = "Browse",
                callback=lambda: DpgUtils.load_path("input_text_collision_map", [DpgUtils.IMAGE_EXTENSIONS]))
        
        def input_radio():
            dpg.add_text("Input data type :")
            dpg.add_radio_button(tag="collision_input_radio", items=['Grid'], default_value=0)
        def storage_radio():
            dpg.add_text("Algorithmic data type : ")
            dpg.add_radio_button(tag="collision_storage_radio", items=['Segments'], default_value=0)

        with dpg.group(horizontal=True) :
            with dpg.group(horizontal=False):
                dpg.add_button(label = "Load", callback=self.load_collision_map)
                dpg.add_button(label = "Remove", callback=self.remove_collision_map)
            with dpg.group(horizontal=False) :
                with dpg.group(horizontal=True): input_radio()
                with dpg.group(horizontal=True): storage_radio()

        with dpg.texture_registry(show=False):
            dpg.add_dynamic_texture(width=TEXTURE_SIZE[0], height=TEXTURE_SIZE[1], 
                default_value=self.get_texture(), tag="collision_texture_tag")
        dpg.add_image("collision_texture_tag", 
                        width=TEXTURE_SIZE[0], height=TEXTURE_SIZE[1])
        