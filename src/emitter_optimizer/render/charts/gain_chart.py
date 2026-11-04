from collections.abc import Sequence
from dataclasses import dataclass

from plotly.graph_objects import Figure, Scatter


@dataclass(frozen=True, slots=True)
class GainChart:
    history: Sequence[float]

    def figure(self) -> Figure:
        figure = Figure(
            data=[Scatter(y=list(self.history), mode="lines", name="gain")],
            layout={
                "title": "The gain, iteration after iteration",
                "xaxis_title": "iteration",
                "yaxis_title": "gain",
                "template": "plotly_dark",
            },
        )
        return figure

    def html(self) -> str:
        return self.figure().to_html(full_html=True, include_plotlyjs="inline")
