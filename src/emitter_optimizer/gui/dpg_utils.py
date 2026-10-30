"""Small helpers shared by the Dear PyGui windows."""

import io
from collections.abc import Sequence

import cv2
import dearpygui.dearpygui as dpg
import numpy as np
from matplotlib.figure import Figure
from PIL import Image

from emitter_optimizer.engine.laws import SignalFunction

IMAGE_EXTENSIONS = "Image (*.bmp *.jpg *.png *.gif){.bmp,.jpg,.png,.gif}"
PYTHON_EXTENSIONS = "Source file (*.py){.py}"
SPACER_HEIGHT = 5
ALPHA = 1.0


class DpgUtils:
    @staticmethod
    def separator(height: int = SPACER_HEIGHT) -> None:
        dpg.add_spacer(height=height)
        dpg.add_separator()
        dpg.add_spacer(height=height)

    @staticmethod
    def load_path(text_box_target: str, extensions: Sequence[str] = ()) -> None:
        """Prompt for a file and write its path into the text box."""
        dialog_tag = f"file_dialog_for_{text_box_target}"

        def callback(_: object, data: dict[str, dict[str, str]]) -> None:
            selected = next(iter(data["selections"].values()))
            dpg.set_value(text_box_target, selected)
            dpg.delete_item(dialog_tag)

        with dpg.file_dialog(
            directory_selector=False,
            show=True,
            file_count=1,
            tag=dialog_tag,
            width=700,
            height=400,
            callback=callback,
            cancel_callback=lambda _: dpg.delete_item(dialog_tag),
        ):
            dpg.add_file_extension(".*", color=(255, 150, 150, 255))
            for extension in extensions:
                dpg.add_file_extension(extension, color=(0, 255, 0, 255))
            dpg.add_file_extension("", color=(150, 180, 180, 255))

    @staticmethod
    def show_item(item: str, items_to_hide: Sequence[str] | None = None) -> None:
        dpg.configure_item(item, show=True)

        for item_to_hide in items_to_hide or ():
            dpg.configure_item(item_to_hide, show=item_to_hide == item)

        dpg.focus_item(item)

    @staticmethod
    def show_info(
        message: str,
        info_type: str = "Info",
        title: str = "",
        *,
        verbose: bool = False,
    ) -> None:
        def close(*_: object) -> None:
            dpg.delete_item(modal_id)

        if verbose:
            print(f"{info_type} : {message}")

        with dpg.mutex():
            viewport_width = dpg.get_viewport_client_width()
            viewport_height = dpg.get_viewport_client_height()

            with dpg.window(
                label=f"< {info_type} > {title}",
                modal=True,
                no_close=True,
            ) as modal_id:
                dpg.add_text(message)
                dpg.add_button(label="Ok", width=75, callback=close)

        dpg.split_frame()
        width = int(dpg.get_item_width(modal_id) or 0)
        height = int(dpg.get_item_height(modal_id) or 0)
        dpg.set_item_pos(
            modal_id,
            [
                viewport_width // 2 - width // 2,
                viewport_height // 2 - height // 2,
            ],
        )

    @staticmethod
    def show_not_implemented() -> None:
        DpgUtils.show_info("Not Implemented yet!", "Error")

    @staticmethod
    def make_plot_data(
        function: SignalFunction,
        interval: tuple[float, float],
        samples: int = 20,
    ) -> tuple[list[float], list[float]]:
        abscissas = np.linspace(interval[0], interval[1], samples)
        ordinates = function(abscissas)
        return abscissas.tolist(), np.asarray(ordinates).tolist()

    @staticmethod
    def fig_to_dpg_texture(figure: Figure) -> list[float]:
        buffer = io.BytesIO()
        figure.savefig(buffer, format="png")
        buffer.seek(0)
        image = Image.open(buffer).convert("RGBA")
        texture = np.asarray(image, dtype=np.float32) / 255.0
        return texture.ravel().tolist()

    @staticmethod
    def np_image_to_dpg_texture(
        image: np.ndarray,
        size: tuple[int, int] | None = None,
    ) -> list[float]:
        resized = image if size is None else cv2.resize(image, size)
        normalized = np.clip(resized, 0.0, 1.0).astype(np.float32)
        rgba = np.empty((*normalized.shape, 4), dtype=np.float32)
        rgba[..., :3] = normalized[..., None]
        rgba[..., 3] = ALPHA
        return rgba.ravel().tolist()

    @staticmethod
    def draw_segments_on_image(
        segments: np.ndarray,
        image_size: tuple[int, int],
    ) -> np.ndarray:
        width, height = image_size
        image = np.zeros((height, width), dtype=np.float32)
        scaled = segments * np.array([width, height])
        for start, end in scaled.astype(int):
            cv2.line(image, tuple(start), tuple(end), 1.0, 1)
        return image
