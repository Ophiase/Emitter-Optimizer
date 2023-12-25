import dearpygui.dearpygui as dpg
import tensorflow as tf
import matplotlib.pyplot as plt
from threading import Thread
import cv2

from .configuration import GuiConfig
from .dpg_utils import DpgUtils

from gui.windows.parameters import WindowParameters
from gui.windows.process import WindowProcess
from gui.windows.render import WindowRender

from gui.windows.loss import WindowLoss

from gui.windows.user_defined_collisions import WindowUserDefinedCollisions
from gui.windows.user_defined_density import WindowUserDefinedDensity
from gui.windows.user_defined_function import WindowUserDefinedFunction


from settings import DEFAULT_GUI_FONT, DEFAULT_GUI_JSON

class Application:

    # -----------------------------------
    # Init

    def __init__(self) -> None:
        # parameters
        self.config = GuiConfig()

        # windows

        self.window_loss = WindowLoss(self.config).process

        self.window_parameters = WindowParameters(self.config).process
        self.window_process = WindowProcess(self.config).process
        self.window_render = WindowRender(self.config).process
        
        self.window_user_defined_collisions = WindowUserDefinedCollisions(self.config).process
        self.window_user_defined_density = WindowUserDefinedDensity(self.config).process

        self.window_user_defined_emitter = WindowUserDefinedFunction(self.config,
            "emitter", GuiConfig.DEFAULT_EMITTER_FUNCTION, self.config, "emitter_function"
            ).process
        self.window_user_defined_sensor = WindowUserDefinedFunction(self.config,
            "sensor", GuiConfig.DEFAULT_SENSOR_FUNCTION, self.config, "sensor_function"
            ).process

        self._dpg_context()
        dpg.destroy_context()

    def _dpg_context(self) -> None:
        '''
        This method generates all the GUI within a dearpygui (DPG) context.
        \n- Functionalities are windowed modules separated in methods _window_<functionality> :
            \n\t- Render
            \n\t- Process (solver)
            \n\t- Parameters
                \n\t\t- User Defined Density
                \n\t\t- User Defined Collisions
                \n\t\t- User Defined Emitters
                \n\t\t- User Defined Sensors
        '''

        dpg.create_context()

        with dpg.font_registry():
            self.default_font = dpg.add_font(DEFAULT_GUI_FONT, 20)
        dpg.bind_font(self.default_font)
        
        # -----------------------------------

        with dpg.window() as self.background_window: pass
        dpg.set_primary_window(self.background_window, True)

        def generate_window(window_info):
            with dpg.window(
                    label=window_info['label'],
                    tag=window_info['tag'],
                    no_close=window_info.get('no_close', False),
                    width=window_info['width'],
                    height=window_info['height'],
                    pos=window_info.get('position', [0, 0]),
                    show=window_info.get('show', True),
                    modal=window_info.get('modal', False),
                    no_title_bar=window_info.get('no_title_bar', False)
            ):
                content_function = getattr(self, window_info['content'], None)
                if content_function and callable(content_function):
                    content_function(window_info['tag'])

        for window_info in DEFAULT_GUI_JSON.get('windows', []) :
            generate_window(window_info)

        # -----------------------------------
        
        viewport_default = DEFAULT_GUI_JSON["viewport"]
        dpg.create_viewport(
            width=viewport_default["width"],
            height=viewport_default["height"],
            title=viewport_default["title"],
            min_width=viewport_default["min_width"],
            min_height=viewport_default["min_height"]
        )
        
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui() # BLOCKING