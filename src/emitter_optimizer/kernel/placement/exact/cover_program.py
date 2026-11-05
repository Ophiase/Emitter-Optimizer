import math
from dataclasses import dataclass

import numpy as np
from scipy import sparse
from scipy.optimize import Bounds, LinearConstraint, milp

from emitter_optimizer.kernel.placement.exact.cover_solution import CoverSolution

BOUND_ROUNDING = 1e-6
SOLVED = 0


@dataclass(frozen=True, slots=True)
class CoverProgram:
    """Maximum weighted coverage over `(candidates, points)`, as an integer program."""

    coverage: np.ndarray
    weights: np.ndarray
    emitters: int
    seconds: float = 600.0

    @staticmethod
    def maximal_rows(coverage: np.ndarray) -> np.ndarray:
        """The indices of the rows no other row contains, one per distinct row."""
        packed = np.packbits(coverage, axis=1)
        _, first = np.unique(packed, axis=0, return_index=True)
        order = first[np.argsort(-coverage[first].sum(axis=1), kind="stable")]
        kept: list[int] = []
        held = np.zeros((order.shape[0], packed.shape[1]), dtype=np.uint8)
        for index in order:
            row = packed[index]
            if not np.any(np.all((held[: len(kept)] & row) == row, axis=1)):
                held[len(kept)] = row
                kept.append(int(index))
        return np.array(kept)

    def solve(self) -> CoverSolution:
        candidates, points = self.coverage.shape
        objective = np.concatenate((np.zeros(candidates), -self.weights))
        result = milp(
            objective,
            integrality=np.concatenate((np.ones(candidates), np.zeros(points))),
            bounds=Bounds(0.0, 1.0),
            constraints=self._constraints(),
            options={"time_limit": self.seconds, "mip_rel_gap": 0.0},
        )
        if result.x is None:
            message = f"the program found no solution: {result.message}"
            raise ValueError(message)
        chosen = tuple(
            int(index) for index in np.nonzero(result.x[:candidates] > 0.5)[0]
        )
        reached = self.coverage[list(chosen)].any(axis=0)
        return CoverSolution(
            chosen,
            int(self.weights[reached].sum()),
            self._bound(result),
        )

    def _constraints(self) -> tuple[LinearConstraint, LinearConstraint]:
        candidates, points = self.coverage.shape
        budget = sparse.hstack((
            sparse.csr_array(np.ones((1, candidates))),
            sparse.csr_array((1, points)),
        ))
        served = sparse.hstack((
            -sparse.csr_array(self.coverage.T.astype(np.float64)),
            sparse.identity(points, format="csr"),
        ))
        return (
            LinearConstraint(sparse.csr_array(budget), -np.inf, float(self.emitters)),
            LinearConstraint(sparse.csr_array(served), -np.inf, 0.0),
        )

    def _bound(self, result: object) -> int:
        dual = getattr(result, "mip_dual_bound", None)
        if dual is None or getattr(result, "status", None) not in {SOLVED, 1}:
            return int(self.weights.sum())
        return math.floor(-float(dual) + BOUND_ROUNDING)
