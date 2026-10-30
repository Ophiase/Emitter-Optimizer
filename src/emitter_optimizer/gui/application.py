"""The Dear PyGui face: build the windows from the layout, then run."""

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import dearpygui.dearpygui as dpg

from emitter_optimizer.gui.configuration import GuiConfig
from emitter_optimizer.gui.windows.loss import WindowLoss
from emitter_optimizer.gui.windows.parameters import WindowParameters
from emitter_optimizer.gui.windows.process import WindowProcess
from emitter_optimizer.gui.windows.render import WindowRender
from emitter_optimizer.gui.windows.user_defined_collisions import (
    WindowUserDefinedCollisions,
)
from emitter_optimizer.gui.windows.user_defined_density import (
    WindowUserDefinedDensity,
)
from emitter_optimizer.gui.windows.user_defined_function import (
    WindowUserDefinedFunction,
)
from emitter_optimizer.paths import DEFAULT_GUI_CONFIGURATION, DEFAULT_GUI_FONT

FONT_SIZE = 20
DEFAULT_POSITION = (0, 0)
WindowContent = Callable[[str], None]


@dataclass(frozen=True)
class WindowSpec:
    """One window of the layout file, typed."""

    label: str
    tag: str
    width: int
    height: int
    content: str
    position: tuple[int, int] = DEFAULT_POSITION
    show: bool = True
    modal: bool = False
    no_close: bool = False
    no_title_bar: bool = False

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> WindowSpec:
        position = data.get("position", DEFAULT_POSITION)
        return cls(
            label=str(data["label"]),
            tag=str(data["tag"]),
            width=int(data["width"]),
            height=int(data["height"]),
            content=str(data["content"]),
            position=(int(position[0]), int(position[1])),
            show=bool(data.get("show", True)),
            modal=bool(data.get("modal")),
            no_close=bool(data.get("no_close")),
            no_title_bar=bool(data.get("no_title_bar")),
        )


@dataclass(frozen=True)
class ViewportSpec:
    """The window the application opens into."""

    width: int
    height: int
    title: str
    min_width: int
    min_height: int

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> ViewportSpec:
        return cls(
            width=int(data["width"]),
            height=int(data["height"]),
            title=str(data["title"]),
            min_width=int(data["min_width"]),
            min_height=int(data["min_height"]),
        )


@dataclass(frozen=True)
class GuiLayout:
    """Every window of the application and the viewport that holds them."""

    windows: tuple[WindowSpec, ...]
    viewport: ViewportSpec

    @classmethod
    def from_file(cls, path: Path) -> GuiLayout:
        return cls.from_mapping(json.loads(path.read_text(encoding="utf-8")))

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> GuiLayout:
        return cls(
            windows=tuple(
                WindowSpec.from_mapping(window) for window in data["windows"]
            ),
            viewport=ViewportSpec.from_mapping(data["viewport"]),
        )


class Application:
    """Build the windows once, then run the Dear PyGui loop when called."""

    def __init__(
        self,
        config: GuiConfig | None = None,
        layout: GuiLayout | None = None,
    ) -> None:
        self.config = config or GuiConfig()
        self.layout = layout or GuiLayout.from_file(DEFAULT_GUI_CONFIGURATION)
        self.windows = self._content_functions()

    def __call__(self) -> None:
        dpg.create_context()
        try:
            self._bind_font()
            self._create_background()
            for window in self.layout.windows:
                self._add_window(window)
            self._run_viewport()
        finally:
            dpg.destroy_context()

    def _content_functions(self) -> dict[str, WindowContent]:
        return {
            "window_loss": WindowLoss(self.config).process,
            "window_parameters": WindowParameters(self.config).process,
            "window_process": WindowProcess(self.config).process,
            "window_render": WindowRender(self.config).process,
            "window_user_defined_collisions": WindowUserDefinedCollisions(
                self.config
            ).process,
            "window_user_defined_density": WindowUserDefinedDensity(
                self.config
            ).process,
            "window_user_defined_emitter": WindowUserDefinedFunction(
                self.config,
                "emitter",
                self.config.DEFAULT_EMITTER_FUNCTION,
                "emitter_function",
            ).process,
            "window_user_defined_sensor": WindowUserDefinedFunction(
                self.config,
                "sensor",
                self.config.DEFAULT_SENSOR_FUNCTION,
                "sensor_function",
            ).process,
        }

    def _bind_font(self) -> None:
        with dpg.font_registry():
            font = dpg.add_font(str(DEFAULT_GUI_FONT), FONT_SIZE)
        dpg.bind_font(font)

    def _create_background(self) -> None:
        with dpg.window() as background:
            pass
        dpg.set_primary_window(background, True)

    def _add_window(self, window: WindowSpec) -> None:
        content = self.windows.get(window.content)
        if content is None:
            message = f"unknown window content: {window.content}"
            raise ValueError(message)
        with dpg.window(
            label=window.label,
            tag=window.tag,
            no_close=window.no_close,
            width=window.width,
            height=window.height,
            pos=list(window.position),
            show=window.show,
            modal=window.modal,
            no_title_bar=window.no_title_bar,
        ):
            content(window.tag)

    def _run_viewport(self) -> None:
        viewport = self.layout.viewport
        dpg.create_viewport(
            width=viewport.width,
            height=viewport.height,
            title=viewport.title,
            min_width=viewport.min_width,
            min_height=viewport.min_height,
        )
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
