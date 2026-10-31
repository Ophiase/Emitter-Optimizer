import threading
from dataclasses import dataclass

import dearpygui.dearpygui as dpg
import numpy as np

from emitter_optimizer.gui.configuration import GuiConfig
from emitter_optimizer.gui.dialogs import show_info
from emitter_optimizer.gui.widgets import show_item

PARAMETERS_WIDTH = 200
RATE_WIDTH = 120
SAVE_BUTTON = "save_button"
LOSS_ITEM = "loss"


@dataclass
class ProcessWindow:
    config: GuiConfig

    def __call__(self, _tag: str) -> None:
        with dpg.group(horizontal=True):
            with dpg.group(horizontal=False, width=PARAMETERS_WIDTH):
                dpg.add_input_int(
                    label="Number of iterations",
                    default_value=self.config.iteration_count,
                    callback=self._set_iterations,
                )
                dpg.add_input_float(
                    label="Learning rate",
                    default_value=self.config.learning_rate,
                    callback=self._set_learning_rate,
                )
            with dpg.group(horizontal=False, width=RATE_WIDTH):
                dpg.add_input_int(
                    label="Report every",
                    default_value=self.config.report_every,
                    callback=self._set_report_every,
                )
                dpg.add_button(
                    label="Show loss",
                    callback=self._show,
                    user_data=LOSS_ITEM,
                )

        with dpg.group(horizontal=True):
            dpg.add_text("Simulate : ")
            dpg.add_button(label="Update parameters", callback=self._update_solver)
            dpg.add_button(label="Process", callback=self._start)
            dpg.add_button(label="Stop", callback=self._stop)
            dpg.add_button(label="Save", callback=self._save, tag=SAVE_BUTTON)

            with dpg.tooltip(SAVE_BUTTON):
                dpg.add_text(
                    f"Save emitters positions, by default {self.config.SAVE_PATH}"
                )

    def _show(
        self,
        _sender: object,
        _app_data: object,
        user_data: str,
    ) -> None:
        show_item(user_data, self.config.ITEMS_TO_HIDE)

    def _update_solver(
        self,
        _sender: object,
        _app_data: object,
        _user_data: object,
    ) -> None:
        if self.config.solver.is_working:
            show_info("Cannot update while working", "Warning")
            return
        self.config.update_solver()
        self.config.solver.update_callback(None, None)

    def _start(self, _sender: object, _app_data: object, _user_data: object) -> None:
        if self.config.solver.is_working:
            show_info("Cannot start while working", "Warning")
            return
        show_item(LOSS_ITEM, self.config.ITEMS_TO_HIDE)
        threading.Thread(target=self.config.solver.solve, daemon=True).start()

    def _stop(self, _sender: object, _app_data: object, _user_data: object) -> None:
        if self.config.solver.is_working:
            self.config.solver.abort()

    def _save(self, _sender: object, _app_data: object, _user_data: object) -> None:
        path = self.config.SAVE_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savetxt(
            path,
            np.asarray(self.config.solver.positions),
            header="x,y",
            comments="",
        )

    def _set_iterations(
        self,
        _sender: object,
        value: int,
        _user_data: object,
    ) -> None:
        if self._refuse():
            return
        self.config.iteration_count = value
        self.config.solver.set_iteration_count(value)

    def _set_learning_rate(
        self,
        _sender: object,
        value: float,
        _user_data: object,
    ) -> None:
        if self._refuse():
            return
        self.config.learning_rate = value
        self.config.solver.set_learning_rate(value)

    def _set_report_every(
        self,
        _sender: object,
        value: int,
        _user_data: object,
    ) -> None:
        if self._refuse():
            return
        self.config.report_every = value
        self.config.solver.set_report_every(value)

    def _refuse(self) -> bool:
        if not self.config.solver.is_working:
            return False
        show_info("Cannot edit this parameter while working", "Warning")
        return True
