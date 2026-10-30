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

class WindowParameters :
    def __init__(self, config : GuiConfig):
        self.config = config

    def process(self, window_tag) -> None:
        with dpg.group(horizontal=True):
            with dpg.group(horizontal=False):
                dpg.add_text("Map scale : ")
                dpg.add_text("Grid size : ")
            with dpg.group(horizontal=False):
                map_scale = self.config.map_scale
                grid_size = self.config.grid_size

                dpg.add_input_floatx(size=2, default_value=map_scale,
                                    callback=lambda _, x: setattr(self.config, "map_scale", (x[0], x[1])))
                dpg.add_input_intx(size=2, default_value=grid_size,
                                    callback=lambda _, x: setattr(self.config, "grid_size", (x[0], x[1])))

        DpgUtils.separator()

        with dpg.group(horizontal=True) :
            dpg.add_button(label="Manage density map", callback=lambda:DpgUtils.show_item(
                'user_defined_density', items_to_hide=self.config.ITEMS_TO_HIDE))
            dpg.add_button(label="Manage collisions map", callback=lambda:DpgUtils.show_item(
                'user_defined_collisions', items_to_hide=self.config.ITEMS_TO_HIDE))
        
        DpgUtils.separator()

        with dpg.group(horizontal=True) :
            dpg.add_button(label="Edit the emitter function", callback=lambda:DpgUtils.show_item(
                "user_defined_emitter", items_to_hide=self.config.ITEMS_TO_HIDE))
            dpg.add_button(label="Edit the sensor function", callback=lambda:DpgUtils.show_item(
                "user_defined_sensor", items_to_hide=self.config.ITEMS_TO_HIDE))
        DpgUtils.separator()
        
        with dpg.group(horizontal=True) :
            with dpg.group(horizontal=False):
                #dpg.add_text(default_value="Range of emitters (optional)")
                dpg.add_text(default_value="Number of emitters")
            with dpg.group(horizontal=False) :
                #dpg.add_input_intx(size=2, default_value=(2,5), width=100)
                dpg.add_input_int(min_value=1, default_value=self.config.n_emitters, width=140,
                    callback=lambda _, data: setattr(self.config, "n_emitters", data))
