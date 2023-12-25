import dearpygui.dearpygui as dpg
import tensorflow as tf
import matplotlib.pyplot as plt
from threading import Thread
import cv2
import numpy as np

from gui.configuration import GuiConfig
from gui.dpg_utils import DpgUtils

from engine.solver import Solver
from engine.map_type import MapType
from engine.density_map import DensityMap
from engine.collision_map import CollisionMap

TEXTURE_SIZE = (200, 200)

class WindowUserDefinedDensity:
    def __init__(self, config : GuiConfig):
        self.config = config

    def load_density_map(self):
        path = dpg.get_value("input_text_density_map")
        
        input_types = [MapType.GRID]
        input_type = input_types[
            int(dpg.get_value("density_input_radio"))]

        storage_types = [MapType.GRID]
        storage_type = storage_types[
            int(dpg.get_value("density_storage_radio"))]

        data = cv2.imread(path)
        if data is not None:
            data = np.mean(data, axis=2) / 255.0
            self.config.density_map = DensityMap(
                data, input_type, storage_type)
            dpg.set_value("density_texture_tag", self.get_texture())
            return
        
        DpgUtils.show_info('Unreadable image', 'Warning')

    def remove_density_map(self):
        self.config.density_map = None
        dpg.set_value("density_texture_tag", self.get_texture())

    def input_radio(self):
        dpg.add_text("Input data type :")
        dpg.add_radio_button(tag="density_input_radio", 
                             items=['Grid'], default_value=0)
    def storage_radio(self):
        dpg.add_text("Algorithmic data type : ")
        dpg.add_radio_button(tag="density_storage_radio", 
                             items=['Grid'], default_value=0)

    def get_texture(self) :
        if self.config.density_map is None :
            return [1.0 for i in range(
                TEXTURE_SIZE[0]*TEXTURE_SIZE[1]*4
                )]

        match self.config.density_map.storage_type :
            case MapType.GRID :
                return DpgUtils.np_image_to_dpg_texture(
                    self.config.density_map.data, TEXTURE_SIZE)

            case _ :
                raise NotImplementedError()

    def process(self, window_tag) -> None :
        with dpg.group(horizontal=True) :
            dpg.add_text("Density map")
            dpg.add_input_text(multiline=False, width=250,
                tag="input_text_density_map")
            dpg.add_button(label = "Browse",
                callback=lambda: DpgUtils.load_path("input_text_density_map", [DpgUtils.IMAGE_EXTENSIONS]))
        
        with dpg.group(horizontal=True) :
            with dpg.group(horizontal=False):
                dpg.add_button(label = "Load", callback=self.load_density_map)
                dpg.add_button(label = "Remove", callback=self.remove_density_map)
            with dpg.group(horizontal=False) :
                with dpg.group(horizontal=True): self.input_radio()
                with dpg.group(horizontal=True): self.storage_radio()

        with dpg.texture_registry(show=False):
            dpg.add_dynamic_texture(width=TEXTURE_SIZE[0], height=TEXTURE_SIZE[1], 
                default_value=self.get_texture(), tag="density_texture_tag")
        dpg.add_image("density_texture_tag", 
                        width=TEXTURE_SIZE[0], height=TEXTURE_SIZE[1])
        
