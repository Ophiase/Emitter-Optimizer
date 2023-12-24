import tensorflow as tf
from engine.solver import Solver
import dearpygui.dearpygui as dpg
from typing import Callable, Optional

from engine.collision_map import CollisionMap
from engine.density_map import DensityMap
from engine.map_type import MapType

from settings import DEFAULT_EMITTER_FUNCTION, DEFAULT_SENSOR_FUNCTION

class GuiConfig:
    DEFAULT_EMITTER_FUNCTION = DEFAULT_EMITTER_FUNCTION
    DEFAULT_SENSOR_FUNCTION = DEFAULT_SENSOR_FUNCTION

    @staticmethod
    def load_file(file : str) -> str : 
        with open(file, 'r') as f :
            return f.read()

    @staticmethod
    def load_function(user_input : str) :
        namespace = {}
        exec(user_input, namespace)
        return namespace["eval"]

    def __init__(self, update_callback : Callable = None) -> None:
        self.n_iteration : int = 400
        self.learning_step : float = 1.0

        self.n_emitters : int = 20
        self.density_map : Optional[DensityMap] = None
        self.collision_map : Optional[CollisionMap] = None

        self.map_scale = [100.0, 100.0] # unit x unit
        self.grid_size = [20, 20]
 
        self.emitter_function = GuiConfig.load_function(
            GuiConfig.load_file(GuiConfig.DEFAULT_EMITTER_FUNCTION))
        self.sensor_function = GuiConfig.load_function(
            GuiConfig.load_file(GuiConfig.DEFAULT_SENSOR_FUNCTION))
        
        self.update_callback = update_callback
        self.update_rate = 30

        self.update_solver()
        
    def update_solver(self):
        self.solver = self.to_solver()

    def to_solver(self) -> Solver:
        return Solver(
            self.n_emitters, 
            self.density_map, self.collision_map,

            self.map_scale, self.grid_size,
            self.emitter_function, self.sensor_function,

            self.n_iteration, self.learning_step,
            self.update_callback, self.update_rate
        )
