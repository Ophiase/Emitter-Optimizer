from dataclasses import dataclass

import numpy as np

from emitter_optimizer.kernel.placement.exact.instance import Instance

ON_WALL = 1e-9
NUDGE = 1e-7
PARALLEL = 1e-12
ROWS = 256


@dataclass(frozen=True, slots=True)
class Arrangement:
    """The finite positions among which an optimal placement exists.

    The set an emitter must enter to cover a point is a disk cut by the shadows
    of the walls. An optimal emitter can slide until two boundaries of those sets
    meet, so their pairwise crossings, the wall ends and the points themselves are
    enough: Church's circle intersection points, extended by walls and shadows.
    A crossing on a wall is taken once per side, since no emitter sees through.
    """

    instance: Instance

    def vertices(self) -> np.ndarray:
        segments = self._segments()
        found = np.concatenate((
            self.instance.points,
            segments.reshape(-1, 2),
            self._circle_crossings(),
            self._segment_crossings(segments),
            self._circle_segment_crossings(segments),
        ))
        inside = self._inside(found)
        return np.unique(self._sided(inside), axis=0)

    def _segments(self) -> np.ndarray:
        width, height = self.instance.width, self.instance.height
        corners = np.array([[0.0, 0.0], [width, 0.0], [width, height], [0.0, height]])
        edges = np.stack((corners, np.roll(corners, -1, axis=0)), axis=1)
        return np.concatenate((edges, self.instance.walls, self._shadows()))

    def _shadows(self) -> np.ndarray:
        ends = self.instance.walls.reshape(-1, 2)
        seen = self.instance.covers_at_most(ends)
        end_index, point_index = np.nonzero(seen)
        chosen_ends = ends[end_index]
        rays = chosen_ends - self.instance.points[point_index]
        lengths = np.linalg.norm(rays, axis=1, keepdims=True)
        far = self.instance.points[point_index] + (
            rays / np.where(lengths > 0.0, lengths, 1.0) * self.instance.radius
        )
        return np.stack((chosen_ends, far), axis=1)

    def _circle_crossings(self) -> np.ndarray:
        points, radius = self.instance.points, self.instance.radius
        first, second = np.triu_indices(points.shape[0], k=1)
        between = points[second] - points[first]
        apart = np.sum(between**2, axis=1)
        near = (apart > 0.0) & (apart <= 4.0 * radius**2)
        first, between, apart = first[near], between[near], apart[near]
        height = np.sqrt(radius**2 - apart / 4.0)[:, None]
        middle = points[first] + between / 2.0
        normal = np.stack((-between[:, 1], between[:, 0]), axis=1)
        normal = normal / np.sqrt(apart)[:, None]
        return np.concatenate((middle + height * normal, middle - height * normal))

    def _segment_crossings(self, segments: np.ndarray) -> np.ndarray:
        found = [
            self._crossings_of_rows(segments, first)
            for first in range(0, segments.shape[0], ROWS)
        ]
        return np.concatenate(found) if found else np.zeros((0, 2))

    def _crossings_of_rows(self, segments: np.ndarray, first: int) -> np.ndarray:
        rows = segments[first : first + ROWS]
        row_start = rows[:, None, 0, :]
        row_along = rows[:, None, 1, :] - row_start
        other_start = segments[None, :, 0, :]
        other_along = segments[None, :, 1, :] - other_start
        offset = other_start - row_start
        turn = _cross(row_along, other_along)
        steady = np.where(np.abs(turn) > PARALLEL, turn, np.inf)
        row_share = _cross(offset, other_along) / steady
        other_share = _cross(offset, row_along) / steady
        meet = (
            (np.abs(turn) > PARALLEL)
            & (row_share >= 0.0)
            & (row_share <= 1.0)
            & (other_share >= 0.0)
            & (other_share <= 1.0)
        )
        row_index, other_index = np.nonzero(meet)
        keep = other_index > row_index + first
        row_index, other_index = row_index[keep], other_index[keep]
        shares = row_share[row_index, other_index][:, None]
        return rows[row_index, 0] + shares * (rows[row_index, 1] - rows[row_index, 0])

    def _circle_segment_crossings(self, segments: np.ndarray) -> np.ndarray:
        found = [
            self._circle_rows(segments[first : first + ROWS])
            for first in range(0, segments.shape[0], ROWS)
        ]
        return np.concatenate(found) if found else np.zeros((0, 2))

    def _circle_rows(self, rows: np.ndarray) -> np.ndarray:
        start, along = rows[:, None, 0, :], rows[:, None, 1, :] - rows[:, None, 0, :]
        offset = start - self.instance.points[None, :, :]
        square = np.maximum(np.sum(along**2, axis=-1), PARALLEL)
        half = np.sum(offset * along, axis=-1)
        rest = np.sum(offset**2, axis=-1) - self.instance.radius**2
        discriminant = half**2 - square * rest
        root = np.sqrt(np.maximum(discriminant, 0.0))
        found = []
        for sign in (-1.0, 1.0):
            share = (-half + sign * root) / square
            hits = (discriminant >= 0.0) & (share >= 0.0) & (share <= 1.0)
            found.append(_at(start, along, share, hits))
        return np.concatenate(found)

    def _inside(self, positions: np.ndarray) -> np.ndarray:
        bounds = np.array([self.instance.width, self.instance.height])
        keep = np.all((positions >= -ON_WALL) & (positions <= bounds + ON_WALL), axis=1)
        return np.clip(positions[keep], 0.0, bounds)

    def _sided(self, positions: np.ndarray) -> np.ndarray:
        sided = []
        free = np.ones(positions.shape[0], dtype=bool)
        for wall in self.instance.walls:
            along = wall[1] - wall[0]
            length = float(np.linalg.norm(along))
            unit = along / length
            offset = positions - wall[0]
            share = offset @ unit / length
            on_wall = (np.abs(_cross(unit, offset)) < ON_WALL) & (
                (share > ON_WALL) & (share < 1.0 - ON_WALL)
            )
            normal = np.array([-unit[1], unit[0]])
            sided += [
                positions[on_wall] + NUDGE * normal,
                positions[on_wall] - NUDGE * normal,
            ]
            free &= ~on_wall
        return np.concatenate([positions[free], *sided])


def _cross(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    return first[..., 0] * second[..., 1] - first[..., 1] * second[..., 0]


def _at(
    start: np.ndarray, along: np.ndarray, share: np.ndarray, hits: np.ndarray
) -> np.ndarray:
    row_index, point_index = np.nonzero(hits)
    return start[row_index, 0] + (
        share[row_index, point_index][:, None] * along[row_index, 0]
    )
