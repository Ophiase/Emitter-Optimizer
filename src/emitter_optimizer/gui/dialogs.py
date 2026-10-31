from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import dearpygui.dearpygui as dpg

OK_WIDTH = 75
DIALOG_WIDTH = 700
DIALOG_HEIGHT = 400


def show_info(message: str, kind: str = "Info", title: str = "") -> None:
    modal = dpg.generate_uuid()

    def close(_sender: object, _app_data: object, _user_data: object) -> None:
        dpg.delete_item(modal)

    with dpg.mutex():
        viewport_width = dpg.get_viewport_client_width()
        viewport_height = dpg.get_viewport_client_height()
        with dpg.window(
            label=f"< {kind} > {title}",
            tag=modal,
            modal=True,
            no_close=True,
        ):
            dpg.add_text(message)
            dpg.add_button(label="Ok", width=OK_WIDTH, callback=close)

    dpg.split_frame()
    width = int(dpg.get_item_width(modal) or 0)
    height = int(dpg.get_item_height(modal) or 0)
    dpg.set_item_pos(
        modal,
        [viewport_width // 2 - width // 2, viewport_height // 2 - height // 2],
    )


@dataclass(frozen=True)
class FileDialog:
    target: str
    extensions: Sequence[str] = ()

    @property
    def tag(self) -> str:
        return f"file_dialog_for_{self.target}"

    def open(self) -> None:
        with dpg.file_dialog(
            directory_selector=False,
            show=True,
            file_count=1,
            tag=self.tag,
            width=DIALOG_WIDTH,
            height=DIALOG_HEIGHT,
            callback=self._choose,
            cancel_callback=self._cancel,
        ):
            dpg.add_file_extension(".*", color=(255, 150, 150, 255))
            for extension in self.extensions:
                dpg.add_file_extension(extension, color=(0, 255, 0, 255))
            dpg.add_file_extension("", color=(150, 180, 180, 255))

    def _choose(
        self, _sender: object, data: dict[str, Any], _user_data: object
    ) -> None:
        dpg.set_value(self.target, data["file_path_name"])
        dpg.delete_item(self.tag)

    def _cancel(self, _sender: object, _app_data: object, _user_data: object) -> None:
        dpg.delete_item(self.tag)
