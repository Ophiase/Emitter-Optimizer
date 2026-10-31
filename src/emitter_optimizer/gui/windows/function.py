from dataclasses import dataclass, field
from pathlib import Path

import dearpygui.dearpygui as dpg

from emitter_optimizer.engine.laws import SignalFunction, load_law
from emitter_optimizer.gui.configuration import GuiConfig
from emitter_optimizer.gui.dialogs import FileDialog, show_info
from emitter_optimizer.gui.images import PYTHON_EXTENSIONS
from emitter_optimizer.gui.widgets import plot_data

CODE_EDITOR_HEIGHT = 325
PLOT_SIZE = 200
PLOT_INTERVAL = (0.0, 5.0)
RESIZE_HORIZONTAL_MARGIN = 225
RESIZE_VERTICAL_MARGIN = 45


@dataclass
class FunctionWindow:
    config: GuiConfig
    name: str
    default_code: Path
    attribute: str
    tag: str = field(default="", init=False)

    @property
    def code_tag(self) -> str:
        return f"input_{self.name}_code"

    @property
    def path_tag(self) -> str:
        return f"input_{self.name}_code_path"

    @property
    def plot_tag(self) -> str:
        return f"{self.name}_serie"

    @property
    def range_tag(self) -> str:
        return f"plot_{self.name}_range"

    def __call__(self, tag: str) -> None:
        self.tag = tag
        handler = f"{tag}_resize_handler"
        with dpg.item_handler_registry(tag=handler):
            dpg.add_item_resize_handler(callback=self._on_resize)
        dpg.bind_item_handler_registry(tag, handler)
        self._resize()

        with dpg.group(horizontal=True):
            with dpg.group(horizontal=False):
                with dpg.plot(label="Line Series", height=PLOT_SIZE, width=PLOT_SIZE):
                    dpg.add_plot_axis(dpg.mvXAxis)
                    dpg.add_plot_axis(dpg.mvYAxis, tag=f"{self.name}_y_axis")
                    abscissas, ordinates = plot_data(
                        self._function(),
                        PLOT_INTERVAL,
                    )
                    dpg.add_line_series(
                        abscissas,
                        ordinates,
                        tag=self.plot_tag,
                        parent=f"{self.name}_y_axis",
                    )
                dpg.add_input_floatx(
                    size=2,
                    default_value=list(PLOT_INTERVAL),
                    width=PLOT_SIZE,
                    tag=self.range_tag,
                )

                with dpg.group(horizontal=True):
                    dpg.add_button(label="Update", callback=self._update)
                    dpg.add_button(label="Reset (code)", callback=self._reset)

                dpg.add_input_text(default_value="", tag=self.path_tag, width=PLOT_SIZE)
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Browse", callback=self._browse)
                    dpg.add_button(label="Load", callback=self._load_code)

            dpg.add_input_text(
                multiline=True,
                height=CODE_EDITOR_HEIGHT,
                tag=self.code_tag,
                default_value=self.default_code.read_text(encoding="utf-8"),
            )

    def _function(self) -> SignalFunction:
        return getattr(self.config, self.attribute).value

    def _on_resize(
        self,
        _sender: object,
        _app_data: object,
        _user_data: object,
    ) -> None:
        self._resize()

    def _resize(self) -> None:
        width, height = dpg.get_item_rect_size(self.tag)
        if width <= 0 or height <= 0:
            return
        dpg.set_item_width(self.code_tag, width - RESIZE_HORIZONTAL_MARGIN)
        dpg.set_item_height(self.code_tag, height - RESIZE_VERTICAL_MARGIN)

    def _plot(self) -> None:
        lower, upper = dpg.get_value(self.range_tag)
        abscissas, ordinates = plot_data(self._function(), (lower, upper))
        dpg.configure_item(self.plot_tag, x=abscissas, y=ordinates)

    def _try_load(self) -> None:
        try:
            law = load_law(dpg.get_value(self.code_tag))
        except Exception:
            show_info("Can't parse the function passed", "Error")
            return
        setattr(self.config, self.attribute, law)

    def _load_code(
        self,
        _sender: object,
        _app_data: object,
        _user_data: object,
    ) -> None:
        try:
            source = Path(dpg.get_value(self.path_tag)).read_text(encoding="utf-8")
        except OSError:
            show_info("Invalid path", "Error")
            return
        dpg.set_value(self.code_tag, source)

    def _browse(self, _sender: object, _app_data: object, _user_data: object) -> None:
        FileDialog(self.path_tag, (PYTHON_EXTENSIONS,)).open()

    def _reset(self, _sender: object, _app_data: object, _user_data: object) -> None:
        dpg.set_value(
            self.code_tag,
            self.default_code.read_text(encoding="utf-8"),
        )
        self._plot()

    def _update(self, _sender: object, _app_data: object, _user_data: object) -> None:
        self._try_load()
        self._plot()
