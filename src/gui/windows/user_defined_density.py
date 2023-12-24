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

class WindowUserDefinedDensity:
    def __init__(self, config : GuiConfig):
        self.config = config

    def process(self, window_tag) -> None :
        def load_density_map():
            path = dpg.get_value("input_text_density_map")
            
            input_types = [MapType.GRID]
            input_type = input_types[
                int(dpg.get_value("density_input_radio"))]

            storage_types = [MapType.GRID]
            storage_type = storage_types[
                int(dpg.get_value("density_storage_radio"))]

            data = cv2.imread(path)
            if data is not None:
                self.config.density_map = DensityMap(
                    data, input_type, storage_type)
                return
            
            DpgUtils.show_info('Unreadable image', 'Warning')

        def remove_density_map():
            self.config.density_map = None

        with dpg.group(horizontal=True) :
            dpg.add_text("Density map")
            dpg.add_input_text(multiline=False, width=250,
                tag="input_text_density_map")
            dpg.add_button(label = "Browse",
                callback=lambda: DpgUtils.load_path("input_text_density_map", [DpgUtils.IMAGE_EXTENSIONS]))
        
        def input_radio():
            dpg.add_text("Input data type :")
            dpg.add_radio_button(tag="density_input_radio", items=['Grid'], default_value=0)
        def storage_radio():
            dpg.add_text("Algorithmic data type : ")
            dpg.add_radio_button(tag="density_storage_radio", items=['Grid'], default_value=0)

        with dpg.group(horizontal=True) :
            with dpg.group(horizontal=False):
                dpg.add_button(label = "Load", callback=load_density_map)
                dpg.add_button(label = "Remove", callback=remove_density_map)
            with dpg.group(horizontal=False) :
                with dpg.group(horizontal=True): input_radio()
                with dpg.group(horizontal=True): storage_radio()
