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


class WindowLoss :
    def __init__(self, config : GuiConfig):
        self.config = config

    def process(self, window_tag) -> None:
        dpg.add_simple_plot(tag="history_plot_tag", 
            default_value=[],
            width=580,
            height=320
            )