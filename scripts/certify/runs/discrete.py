from dataclasses import dataclass

import numpy as np

from emitter_optimizer.kernel.placement.exact import CoverProgram, Instance

RANDOM_DRAWS = 32


@dataclass(frozen=True, slots=True)
class Discrete:
    """The classical answers: the best placement among sites fixed in advance."""

    instance: Instance
    seconds: float = 300.0

    def on_demand_sites(self) -> int:
        return self._best_among(self.instance.points)

    def on_grid(self, side: int) -> int:
        axis_x = np.linspace(0.0, self.instance.width, side)
        axis_y = np.linspace(0.0, self.instance.height, side)
        return self._best_among(
            np.stack(np.meshgrid(axis_x, axis_y), axis=-1).reshape(-1, 2)
        )

    def random(self, seed: int = 0) -> float:
        generator = np.random.default_rng(seed)
        weights = self.instance.weights / self.instance.weights.sum()
        draws = generator.choice(
            self.instance.points.shape[0],
            (RANDOM_DRAWS, self.instance.emitters),
            p=weights,
        )
        return float(
            np.mean([
                self.instance.covered_weight(self.instance.points[draw])
                for draw in draws
            ])
        )

    def _best_among(self, sites: np.ndarray) -> int:
        coverage = self.instance.covers(sites)
        kept = CoverProgram.maximal_rows(coverage)
        program = CoverProgram(
            coverage[kept], self.instance.weights, self.instance.emitters, self.seconds
        )
        return program.solve().weight
