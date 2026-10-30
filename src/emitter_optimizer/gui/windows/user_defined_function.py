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

class WindowUserDefinedFunction:
    def __init__(self, config : GuiConfig, 
                name : str, default_code : str ,
                object_that_contains_the_lambda, lambda_attribute_name : str
                ):
        '''
        - This generic window is meant to edit a lambda.
            - name : GUI name of the method
            - default_code

            - object_that_contains_the_lambda : the object that contains the lambda
            - lambda_attribute_name : name of the lambda as attribute of the object
        '''
        
        self.config = config

        self.name = name
        self.default_code = default_code
        self.object_that_contains_the_lambda = object_that_contains_the_lambda
        self.lambda_attribute_name = lambda_attribute_name

    def process(self, window_tag) -> None :
        code_editor_input_tag = f"input_{self.name}_code"
        
        def resize_code():
            width, height = dpg.get_item_rect_size(window_tag)
            if height > 0 and width > 0:
                dpg.set_item_width(code_editor_input_tag, width - 225)
                dpg.set_item_height(code_editor_input_tag, height - 45)

        resize_handler = window_tag + "_resize_handler"
        with dpg.item_handler_registry(tag=resize_handler):
            dpg.add_item_resize_handler(callback=resize_code)
        dpg.bind_item_handler_registry(window_tag, resize_handler)
        resize_code()
        
        def try_load() :
            try:
                setattr(
                    self.object_that_contains_the_lambda,
                    self.lambda_attribute_name,
                    GuiConfig.load_function(dpg.get_value(f'input_{self.name}_code'))
                )
            except: 
                DpgUtils.show_info("Can't parse the function passed", "Error")
        
        def load_code() :
            try :
                print(dpg.get_value(f"input_{self.name}"))
                with open(dpg.get_value(f"input_{self.name}"), 'r') as r:
                    dpg.set_value(f"input_{self.name}_code", r.read())
            except :
                DpgUtils.show_info("Invalid path", "Error")

        def update_plot():
            function = getattr(self.object_that_contains_the_lambda, self.lambda_attribute_name)
            data_x, data_y = DpgUtils.make_plot_data(function,
                            dpg.get_value(f'plot_{self.name}_range'))
            dpg.configure_item(f"{self.name}_serie", x=data_x, y=data_y)
        
        with dpg.group(horizontal=True):
            with dpg.group(horizontal=False):
                with dpg.plot(label="Line Series", height=200, width=200):
                    dpg.add_plot_axis(dpg.mvXAxis)
                    dpg.add_plot_axis(dpg.mvYAxis, tag=f"{self.name}_y_axis")

                    function = getattr(self.object_that_contains_the_lambda, self.lambda_attribute_name)
                    data_x, data_y = DpgUtils.make_plot_data(function, (0.0, 5.0))
                    dpg.add_line_series(data_x, data_y, tag=f"{self.name}_serie", parent=f"{self.name}_y_axis")
                dpg.add_input_floatx(size=2, default_value=[0, 5], width=200, tag=f"plot_{self.name}_range")
                
                with dpg.group(horizontal=True) :
                    def update_callback() :
                        try_load()
                        update_plot()

                    def reset_callback():
                        dpg.set_value(f'input_{self.name}_code', 
                            GuiConfig.load_file(self.default_code))
                        update_plot()

                    dpg.add_button(label="Update",
                        callback=update_callback)
                    dpg.add_button(label="Reset (code)   ",
                        callback=reset_callback)
                
                dpg.add_input_text(default_value="", tag=f"input_{self.name}_code_path", width=200)
                with dpg.group(horizontal=True) :
                    dpg.add_button(label="Browse", 
                                    callback=lambda:DpgUtils.load_path(f"input_{self.name}_code_path", [DpgUtils.PYTHON_EXTENSIONS]))
                    dpg.add_button(label="Load", callback=load_code)
            
            dpg.add_input_text(multiline=True, height=325, tag=code_editor_input_tag,
                                default_value=GuiConfig.load_file(self.default_code))
