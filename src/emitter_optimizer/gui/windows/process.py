import threading

import dearpygui.dearpygui as dpg
import numpy as np

from emitter_optimizer.gui.configuration import GuiConfig
from emitter_optimizer.gui.dpg_utils import DpgUtils


class WindowProcess:
    def __init__(self, config: GuiConfig) -> None:
        self.config = config

    def update_solver(self) -> None:
        if self.config.solver.is_working:
            DpgUtils.show_info("Cannot update while working", "Warning")
            return

        self.config.update_solver()
        self.config.solver.update_callback(None, None)

    def start(self) -> None:
        if self.config.solver.is_working:
            DpgUtils.show_info("Cannot start while working", "Warning")
            return

        DpgUtils.show_item("loss", items_to_hide=self.config.ITEMS_TO_HIDE)
        threading.Thread(target=self.config.solver.solve, daemon=True).start()

    def stop(self) -> None:
        if not self.config.solver.is_working:
            return
        self.config.solver.abort()

    def set_iterations(self, _: object, value: int) -> None:
        if self.config.solver.is_working:
            DpgUtils.show_info("Cannot edit this parameter while working", "Warning")
            return

        self.config.n_iteration = value
        self.config.solver.n_iteration = value

    def set_learning_step(self, _: object, value: float) -> None:
        if self.config.solver.is_working:
            DpgUtils.show_info("Cannot edit this parameter while working", "Warning")
            return

        self.config.learning_step = value
        self.config.solver.epsilon = value

    def set_update_rate(self, _: object, value: int) -> None:
        if self.config.solver.is_working:
            DpgUtils.show_info("Cannot edit this parameter while working", "Warning")
            return

        self.config.update_rate = value
        self.config.solver.update_rate = value

    def save(self) -> None:
        path = self.config.DEFAULT_SAVE_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savetxt(
            path,
            np.asarray(self.config.solver.emitters_positions),
            header="Emitter's positions",
            comments="# ",
        )

    def process(self, _window_tag: str) -> None:
        with dpg.group(horizontal=True):
            with dpg.group(horizontal=False, width=200):
                dpg.add_input_int(
                    label="Number of iterations",
                    default_value=self.config.n_iteration,
                    callback=self.set_iterations,
                )
                dpg.add_input_float(
                    label="Learning step",
                    default_value=self.config.learning_step,
                    callback=self.set_learning_step,
                )
            with dpg.group(horizontal=False, width=120):
                dpg.add_input_int(
                    label="Update Rate",
                    default_value=self.config.update_rate,
                    callback=self.set_update_rate,
                )
                dpg.add_button(
                    label="Show loss",
                    callback=lambda: DpgUtils.show_item(
                        "loss", items_to_hide=self.config.ITEMS_TO_HIDE
                    ),
                )

        with dpg.group(horizontal=True):
            dpg.add_text("Simulate : ")
            dpg.add_button(label="Update parameters", callback=self.update_solver)
            dpg.add_button(label="Process", callback=self.start)
            dpg.add_button(label="Stop", callback=self.stop)
            dpg.add_button(label="Save", callback=self.save, tag="save_button")

            with dpg.tooltip("save_button"):
                dpg.add_text(
                    "Save emitters positions, by default "
                    f"{self.config.DEFAULT_SAVE_PATH}"
                )
