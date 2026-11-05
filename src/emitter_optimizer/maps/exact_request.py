from dataclasses import dataclass
from pathlib import Path

import numpy as np

from emitter_optimizer.kernel.placement.exact import Instance

POINT_COLUMNS = 3
WALL_COLUMNS = 4


@dataclass(frozen=True, slots=True)
class ExactRequest:
    """Files and numbers that state a coverage problem, in world units.

    `points` holds `x,y,weight` with an integer weight, `walls` holds `x1,y1,x2,y2`.
    """

    points: Path
    walls: Path | None
    radius: float
    emitters: int
    width: float
    height: float

    def instance(self) -> Instance:
        demand = self._table(self.points, POINT_COLUMNS)
        weights = demand[:, 2].astype(np.int64)
        if not np.array_equal(weights, demand[:, 2]) or np.any(weights <= 0):
            message = f"{self.points}: a weight is a positive integer"
            raise ValueError(message)
        walls = (
            np.zeros((0, WALL_COLUMNS))
            if self.walls is None
            else self._table(self.walls, WALL_COLUMNS)
        )
        return Instance(
            name=self.points.stem,
            points=demand[:, :2],
            weights=weights,
            walls=walls.reshape(-1, 2, 2),
            radius=self.radius,
            emitters=self.emitters,
            width=self.width,
            height=self.height,
        )

    def _table(self, path: Path, columns: int) -> np.ndarray:
        table = np.loadtxt(path, delimiter=",", ndmin=2, comments="#")
        if table.shape[1] != columns:
            message = f"{path}: {columns} columns, not {table.shape[1]}"
            raise ValueError(message)
        return table
