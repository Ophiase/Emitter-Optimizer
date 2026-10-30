"""A window that edits one of the two functions the solver applies."""

from pathlib import Path

import dearpygui.dearpygui as dpg

from emitter_optimizer.engine.types import SignalFunction
from emitter_optimizer.gui.configuration import GuiConfig
from emitter_optimizer.gui.dpg_utils import PYTHON_EXTENSIONS, DpgUtils

CODE_EDITOR_HEIGHT = 325
PLOT_SIZE = 200
PLOT_INTERVAL = (0.0, 5.0)
RESIZE_HORIZONTAL_MARGIN = 225
RESIZE_VERTICAL_MARGIN = 45


class WindowUserDefinedFunction:
    def __init__(
        self,
        config: GuiConfig,
        name: str,
        default_code: Path,
        attribute: str,
    ) -> None:
        self.config = config
        self.name = name
        self.default_code = default_code
        self.attribute = attribute

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

    def _function(self) -> SignalFunction:
        return getattr(self.config, self.attribute)

    def _resize(self, window_tag: str) -> None:
        width, height = dpg.get_item_rect_size(window_tag)
        if width <= 0 or height <= 0:
            return
        dpg.set_item_width(self.code_tag, width - RESIZE_HORIZONTAL_MARGIN)
        dpg.set_item_height(self.code_tag, height - RESIZE_VERTICAL_MARGIN)

    def _plot(self) -> None:
        lower, upper = dpg.get_value(self.range_tag)
        abscissas, ordinates = DpgUtils.make_plot_data(
            self._function(),
            (lower, upper),
        )
        dpg.configure_item(self.plot_tag, x=abscissas, y=ordinates)

    def _try_load(self) -> None:
        try:
            function = GuiConfig.load_function(dpg.get_value(self.code_tag))
        except SyntaxError, KeyError, NameError, TypeError:
            DpgUtils.show_info("Can't parse the function passed", "Error")
            return
        setattr(self.config, self.attribute, function)

    def _load_code(self) -> None:
        path = Path(dpg.get_value(self.path_tag))
        try:
            source = path.read_text(encoding="utf-8")
        except OSError:
            DpgUtils.show_info("Invalid path", "Error")
            return
        dpg.set_value(self.code_tag, source)

    def _reset(self) -> None:
        dpg.set_value(self.code_tag, GuiConfig.load_file(self.default_code))
        self._plot()

    def _update(self) -> None:
        self._try_load()
        self._plot()

    def process(self, window_tag: str) -> None:
        handler = f"{window_tag}_resize_handler"
        with dpg.item_handler_registry(tag=handler):
            dpg.add_item_resize_handler(callback=lambda *_: self._resize(window_tag))
        dpg.bind_item_handler_registry(window_tag, handler)
        self._resize(window_tag)

        with dpg.group(horizontal=True):
            with dpg.group(horizontal=False):
                with dpg.plot(label="Line Series", height=PLOT_SIZE, width=PLOT_SIZE):
                    dpg.add_plot_axis(dpg.mvXAxis)
                    dpg.add_plot_axis(dpg.mvYAxis, tag=f"{self.name}_y_axis")
                    abscissas, ordinates = DpgUtils.make_plot_data(
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
                    dpg.add_button(
                        label="Browse",
                        callback=lambda: DpgUtils.load_path(
                            self.path_tag,
                            [PYTHON_EXTENSIONS],
                        ),
                    )
                    dpg.add_button(label="Load", callback=self._load_code)

            dpg.add_input_text(
                multiline=True,
                height=CODE_EDITOR_HEIGHT,
                tag=self.code_tag,
                default_value=GuiConfig.load_file(self.default_code),
            )
