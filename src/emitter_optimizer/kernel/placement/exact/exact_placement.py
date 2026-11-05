import time
from dataclasses import dataclass

import numpy as np

from emitter_optimizer.kernel.placement.exact.arrangement import Arrangement
from emitter_optimizer.kernel.placement.exact.certificate import Certificate
from emitter_optimizer.kernel.placement.exact.cover_program import CoverProgram
from emitter_optimizer.kernel.placement.exact.instance import Instance

REPAIR_RADII = (0.0, 1e-8, 1e-7, 1e-6)
REPAIR_DIRECTIONS = 32


@dataclass(frozen=True, slots=True)
class ExactPlacement:
    """Solve an instance over its arrangement, and say whether the answer is proved.

    The bound comes from a coverage slightly wider than the scored one, so it holds
    for the scored one; the placement is scored as anyone else's would be. The two
    meeting is the proof, and they are compared rather than assumed to meet.
    """

    instance: Instance
    seconds: float = 600.0

    def solve(self) -> Certificate:
        started = time.perf_counter()
        vertices = Arrangement(self.instance).vertices()
        coverage = self.instance.covers_at_most(vertices)
        kept = CoverProgram.maximal_rows(coverage)
        program = CoverProgram(
            coverage[kept], self.instance.weights, self.instance.emitters, self.seconds
        )
        solution = program.solve()
        positions = np.stack([
            self._repaired(vertices[kept[index]], coverage[kept[index]])
            for index in solution.chosen
        ])
        return Certificate(
            positions,
            self.instance.covered_weight(positions),
            solution.bound,
            vertices.shape[0],
            kept.shape[0],
            time.perf_counter() - started,
        )

    def _repaired(self, vertex: np.ndarray, wanted: np.ndarray) -> np.ndarray:
        """The vertex, or the nearest point that really covers what it promised."""
        angles = np.linspace(0.0, 2.0 * np.pi, REPAIR_DIRECTIONS, endpoint=False)
        directions = np.stack((np.cos(angles), np.sin(angles)), axis=1)
        tried = np.concatenate([
            vertex + radius * directions for radius in REPAIR_RADII
        ])
        bounds = [self.instance.width, self.instance.height]
        tried = np.clip(tried, 0.0, bounds)
        missing = np.sum(wanted & ~self.instance.covers(tried), axis=1)
        return tried[int(np.argmin(missing))]
