from dataclasses import dataclass
from typing import Self

import numpy as np

EXACT_SLACK = 1e-9
RELAXED_SLACK = 1e-6
CHUNK = 4096


@dataclass(frozen=True, slots=True)
class Instance:
    """Weighted points, disjoint walls, a covering radius and a number of emitters.

    A point is covered by an emitter within `radius` whose sight line properly
    crosses no wall. `points` is `(points, 2)`, `weights` holds integers `(points,)`,
    `walls` is `(walls, 2, 2)`; emitters stay in the rectangle `width` by `height`.
    """

    name: str
    points: np.ndarray
    weights: np.ndarray
    walls: np.ndarray
    radius: float
    emitters: int
    width: float
    height: float

    def __post_init__(self) -> None:
        lengths = np.linalg.norm(self.walls[:, 1] - self.walls[:, 0], axis=1)
        if np.any(lengths <= 0.0):
            message = f"{self.name}: a wall has no length"
            raise ValueError(message)
        if self.emitters <= 0 or self.radius <= 0.0:
            message = f"{self.name}: emitters and a radius must be positive"
            raise ValueError(message)

    @classmethod
    def of(cls, record: dict[str, object]) -> Self:
        return cls(
            name=str(record["name"]),
            points=np.asarray(record["points"], dtype=np.float64),
            weights=np.asarray(record["weights"], dtype=np.int64),
            walls=np.asarray(record["walls"], dtype=np.float64).reshape(-1, 2, 2),
            radius=float(str(record["radius"])),
            emitters=int(str(record["emitters"])),
            width=float(str(record["width"])),
            height=float(str(record["height"])),
        )

    def record(self) -> dict[str, object]:
        return {
            "name": self.name,
            "radius": self.radius,
            "emitters": self.emitters,
            "width": self.width,
            "height": self.height,
            "points": self.points.tolist(),
            "weights": self.weights.tolist(),
            "walls": self.walls.tolist(),
        }

    def covers(self, positions: np.ndarray) -> np.ndarray:
        """`(positions, points)`: the coverage this instance is scored by."""
        return self._covers(positions, EXACT_SLACK, EXACT_SLACK)

    def covers_at_most(self, positions: np.ndarray) -> np.ndarray:
        """`covers` with a wider reach and sight: its optimum bounds the true one."""
        return self._covers(positions, RELAXED_SLACK, RELAXED_SLACK)

    def covered_weight(self, positions: np.ndarray) -> int:
        inside = np.clip(positions, 0.0, [self.width, self.height])
        reached = self.covers(inside).any(axis=0)
        return int(self.weights[reached].sum())

    def share(self, weight: float) -> float:
        return float(weight) / float(self.weights.sum())

    def _covers(self, positions: np.ndarray, reach: float, sight: float) -> np.ndarray:
        chunks = [
            self._covers_chunk(positions[first : first + CHUNK], reach, sight)
            for first in range(0, positions.shape[0], CHUNK)
        ]
        if not chunks:
            return np.zeros((0, self.points.shape[0]), dtype=bool)
        return np.concatenate(chunks)

    def _covers_chunk(
        self, positions: np.ndarray, reach: float, sight: float
    ) -> np.ndarray:
        between = positions[:, None, :] - self.points[None, :, :]
        covered = np.sum(between**2, axis=-1) <= (self.radius + reach) ** 2
        for wall in self.walls:
            emitter_index, point_index = np.nonzero(covered)
            blocked = self._blocked(
                wall, positions[emitter_index], self.points[point_index], sight
            )
            covered[emitter_index[blocked], point_index[blocked]] = False
        return covered

    def _blocked(
        self, wall: np.ndarray, emitters: np.ndarray, points: np.ndarray, sight: float
    ) -> np.ndarray:
        """For each emitter and point, in step: does their line cross this wall?"""
        start, end = wall[0], wall[1]
        along = (end - start) / np.linalg.norm(end - start)
        sights = emitters - points
        lengths = np.sqrt(np.sum(sights**2, axis=-1))
        lengths = np.where(lengths > 0.0, lengths, 1.0)
        return _apart(
            _cross(along, emitters - start), _cross(along, points - start), EXACT_SLACK
        ) & _apart(
            _cross(sights, start - points) / lengths,
            _cross(sights, end - points) / lengths,
            sight,
        )


def _cross(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    return first[..., 0] * second[..., 1] - first[..., 1] * second[..., 0]


def _apart(first: np.ndarray, second: np.ndarray, slack: float) -> np.ndarray:
    return ((first > slack) & (second < -slack)) | ((first < -slack) & (second > slack))
