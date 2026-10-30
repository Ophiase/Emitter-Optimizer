import io
import numpy as np
import tensorflow as tf
import dearpygui.dearpygui as dpg
from PIL import Image
import matplotlib.pyplot as plt
from typing import List, Tuple
import cv2

class DpgUtils:
    IMAGE_EXTENSIONS : str = "Image (*.bmp *.jpg *.png *.gif){.bmp,.jpg,.png,.gif}"
    PYTHON_EXTENSIONS : str = "Source file (*.py){.py}"

    @staticmethod
    def separator(height : int = 5) -> None:
            dpg.add_spacer(height=height)
            dpg.add_separator()
            dpg.add_spacer(height=height)

    @staticmethod
    def load_path(text_box_target : str, 
                  extensions : List[str] = []
                  ) -> None:
        """
        Create a file_dialog. 
        Prompts a path to enter in the text_box.  
        Destroys the file_dialog.
        """
        
        file_dialog_tag = f"file_dialog_for_{text_box_target}"

        def callback(sender, data) :
            selections_path = data['selections'].values()
            value = next(iter(selections_path))
            
            dpg.set_value(text_box_target, value)
            dpg.delete_item(file_dialog_tag)
        
        with dpg.file_dialog(
                directory_selector=False, show=True, file_count=1,
                tag=file_dialog_tag, width=700 ,height=400,
                
                callback=callback,
                cancel_callback=lambda _: dpg.delete_item(file_dialog_tag)
            ):

            dpg.add_file_extension(".*", color=(255, 150, 150, 255))
            if extensions is not None : 
                for extension in extensions: 
                    dpg.add_file_extension(extension, color=(0, 255, 0, 255))
            dpg.add_file_extension('', color=(150, 180, 180, 255))

    @staticmethod
    def show_item(item, items_to_hide=None):
        dpg.configure_item(item, show=True)

        if items_to_hide is not None :
            for item_to_hide in items_to_hide :
                dpg.configure_item(item_to_hide, show=(item_to_hide == item))
        
        dpg.focus_item(item)

    @staticmethod
    def show_info(message, info_type="Info", 
                  title = "", verbose=False, 
                  selection_callback=lambda:None, 
                  cancel_enabled=False):
        
        def close() -> None:
            dpg.delete_item(modal_id)
            selection_callback()
        
        if verbose:
            print(f"{info_type} : {message}")
        
        with dpg.mutex():
            viewport_width = dpg.get_viewport_client_width()
            viewport_height = dpg.get_viewport_client_height()

            with dpg.window(label=f"< {info_type} > {title}", modal=True, no_close=True) as modal_id:
                dpg.add_text(message)
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Ok", width=75, 
                                   user_data=(modal_id, True), 
                                   callback=close)
                    if cancel_enabled: 
                        dpg.add_button(label="Cancel", width=75, user_data=(modal_id, False), callback=close)
        
        dpg.split_frame()
        width = dpg.get_item_width(modal_id)
        height = dpg.get_item_height(modal_id)
        dpg.set_item_pos(modal_id, [viewport_width // 2 - width // 2, viewport_height // 2 - height // 2])

    @staticmethod
    def show_not_implemented() -> None :
        DpgUtils.show_info("Not Implemented yet!", "Error")

    @staticmethod
    def make_plot_data(
        f, interval : Tuple[int], samples : int = 20
        ) -> Tuple[tf.Tensor, tf.Tensor]:
        
        X = tf.linspace(interval[0], interval[1], samples)
        Y = tf.vectorized_map(f, X)
        return X, Y

    @staticmethod
    def fig_to_dpg_texture(fig):
        buf = io.BytesIO()
        fig.canvas.draw()
        fig.savefig(buf)
        buf.seek(0)
        fig.canvas.flush_events()
        image = Image.open(buf)
        texture = np.frombuffer(image.tobytes(), dtype=np.uint8)
        return texture / 255.0, image.size
    
    @staticmethod
    def np_image_to_dpg_texture(image : np.array, res=None, grayscale=True):
        if not grayscale :
            raise NotImplementedError()
        
        if res is None :
            res = image.shape
        else :
            image = cv2.resize(image, res)

        texture = []
        for x in range(res[0]):
            for y in range(res[1]):
                for _ in range(3):
                    texture.append(image[x][y])
                texture.append(1)

        return texture

    @staticmethod
    def cv2_to_dpg_texture(image, width, height):
        raise NotImplementedError()
    
    @staticmethod
    def draw_segments_on_image(segments, image_size):
        image = np.zeros((image_size[0], image_size[1]), dtype=np.uint8)

        segment_coords = (segments * np.array(image_size)).astype(int)

        for segment in segment_coords:
            cv2.line(image, tuple(segment[0]), tuple(segment[1]), (1.0, 1.0, 1.0), 1)

        return image