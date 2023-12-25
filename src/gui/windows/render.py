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

TEXTURE_SIZE = 600, 400
class WindowRender:
    def __init__(self, config : GuiConfig):
        self.config = config

    def simulation_state_str(self):
        return "Simulation : " + ("on" if self.config.solver.is_working else "off")

    def get_texture(self, emitters_positions=None):
        fig = self.config.solver.make_fig(emitters_positions,
            ((TEXTURE_SIZE[0]/100), (TEXTURE_SIZE[1])/100))
        texture, size = DpgUtils.fig_to_dpg_texture(fig)
        plt.close(fig)
        return texture

    def update_callback(self, 
            emitters_positions=None, history=None) -> None:
        
        dpg.set_value("simulation_text", self.simulation_state_str())
        dpg.set_value("render_texture_tag", self.get_texture(emitters_positions))
        
        if history is None:
            history = []
        
        dpg.set_value("history_plot_tag", history)

    def process(self, window_tag) -> None:
        with dpg.texture_registry(show=False):
            dpg.add_dynamic_texture(width=TEXTURE_SIZE[0], height=TEXTURE_SIZE[1], 
                default_value=self.get_texture(), tag="render_texture_tag")
            
        dpg.add_text(self.simulation_state_str(), tag="simulation_text")
        dpg.add_image("render_texture_tag", 
                        width=TEXTURE_SIZE[0], height=TEXTURE_SIZE[1])
        
        self.config.update_callback = self.update_callback
        self.config.solver.update_callback = self.update_callback
