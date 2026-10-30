import dearpygui.dearpygui as dpg
import tensorflow as tf
import matplotlib.pyplot as plt
from threading import Thread
import cv2
import numpy as np
import os

from gui.configuration import GuiConfig
from gui.dpg_utils import DpgUtils

from engine.solver import Solver
from engine.map_type import MapType
from engine.density_map import DensityMap
from engine.collision_map import CollisionMap

class WindowProcess :
    def __init__(self, config : GuiConfig):
        self.config = config

    def set_solver(self):
        '''
            Reset solver with new paramater interface 
        '''
        if (self.config.solver.is_working):
            DpgUtils.show_info("Cannot update will working", "Warning")
            return

        self.config.update_solver()
        self.config.solver.update_callback()

    def simulation_start(self):
        '''
            make solver work
        '''
        if (self.config.solver.is_working) : 
            DpgUtils.show_info("Cannot start will working", "Warning")
            return

        DpgUtils.show_item(
                "loss", items_to_hide=self.config.ITEMS_TO_HIDE)
        Thread(target=self.config.solver.solve).start()
        
    def simulation_stop(self):
        '''
            force solver to stop working
        '''
        if (not self.config.solver.is_working) : return
        self.config.solver.abort()

    def update_iterations(self, sender, value):
        if (self.config.solver.is_working) :
            DpgUtils.show_info("Cannot edit this parameter will working", "Warning")
            return

        self.config.n_iteration = value
        self.config.solver.n_iteration = value

    def update_learning_step(self, sender, value):
        if (self.config.solver.is_working) :
            DpgUtils.show_info("Cannot edit this parameter will working", "Warning")
            return
        
        self.config.learning_step = value
        self.config.solver.epsilon = value

    def update_refresh_rate(self, sender, value):
        if (self.config.solver.is_working) :
            DpgUtils.show_info("Cannot edit this parameter will working", "Warning")
            return
        
        self.config.update_rate = value
        self.config.solver.update_rate = value

    def save(self, sender, value):
        path = self.config.DEFAULT_SAVE_PATH
        
        folder = os.path.dirname(path)
        if not os.path.exists(folder):
            os.makedirs(folder)

        np.savetxt(
            path, 
            self.config.solver.emitters_positions, 
            header='Emitter\'s positions', 
            comments='# ')

    def process(self, window_tag) -> None:
        with dpg.group(horizontal=True):
            with dpg.group(horizontal=False, width=200):
                dpg.add_input_int(label="Number of iterations", 
                    default_value=self.config.n_iteration,
                    callback=self.update_iterations)
                dpg.add_input_float(label="Learning step", 
                    default_value=self.config.learning_step,
                    callback=self.update_learning_step)
            with dpg.group(horizontal=False, width=120):
                dpg.add_input_int(label="Update Rate",
                    default_value=self.config.update_rate,
                    callback=self.update_refresh_rate
                    )
                
                dpg.add_button(
                    label="Show loss",
                    callback=lambda:DpgUtils.show_item(
                        "loss", items_to_hide=self.config.ITEMS_TO_HIDE)
                    )

        with dpg.group(horizontal=True):
            dpg.add_text("Simulate : ")
            dpg.add_button(label="Update parameters", callback=self.set_solver)
            dpg.add_button(label="Process", callback=self.simulation_start)
            dpg.add_button(label="Stop", callback=self.simulation_stop)
            dpg.add_button(label="Save", callback=self.save, tag="save_button")

            with dpg.tooltip("save_button") :
                dpg.add_text(
                    f"Save emitters positions. (by default : {self.config.DEFAULT_SAVE_PATH})")

        #dpg.add_button(label="Search with optimal number of sensors", callback=lambda _:DpgUtils.show_not_implemented())