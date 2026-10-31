from collections.abc import Sequence

import dearpygui.dearpygui as dpg
import jax.numpy as jnp
import numpy as np

from emitter_optimizer.kernel import Law

SPACER_HEIGHT = 5
PLOT_SAMPLES = 20


def separator(height: int = SPACER_HEIGHT) -> None:
    dpg.add_spacer(height=height)
    dpg.add_separator()
    dpg.add_spacer(height=height)


def show_item(item: str, items: Sequence[str]) -> None:
    dpg.configure_item(item, show=True)
    for other in items:
        dpg.configure_item(other, show=other == item)
    dpg.focus_item(item)


def plot_data(
    function: Law,
    interval: tuple[float, float],
    samples: int = PLOT_SAMPLES,
) -> tuple[list[float], list[float]]:
    abscissas = np.linspace(interval[0], interval[1], samples)
    ordinates = function(jnp.asarray(abscissas))
    return abscissas.tolist(), np.asarray(ordinates, dtype=np.float64).tolist()
