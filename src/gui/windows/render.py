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

class WindowRender:
    def __init__(self, config : GuiConfig):
        self.config = config

    def process(self, window_tag) -> None:
        TEXTURE_SIZE = 600, 400

        def simulation_state_str():
            return "Simulation : " + ("on" if self.config.solver.is_working else "off")

        def get_texture(emitters_positions=None):
            fig = self.config.solver.make_fig(emitters_positions,
                ((TEXTURE_SIZE[0]/100), (TEXTURE_SIZE[1])/100))
            texture, size = DpgUtils.fig_to_dpg_texture(fig)
            plt.close(fig)
            return texture

        def update_callback(emitters_positions=None) -> None:
            dpg.set_value("simulation_text", simulation_state_str())
            dpg.set_value("render_texture_tag", get_texture(emitters_positions))

        with dpg.texture_registry(show=False):
            dpg.add_dynamic_texture(width=TEXTURE_SIZE[0], height=TEXTURE_SIZE[1], 
                default_value=get_texture(), tag="render_texture_tag")
            
        dpg.add_text(simulation_state_str(), tag="simulation_text")
        dpg.add_image("render_texture_tag", 
                        width=TEXTURE_SIZE[0], height=TEXTURE_SIZE[1])
        
        self.config.update_callback = update_callback
        self.config.solver.update_callback = update_callback
