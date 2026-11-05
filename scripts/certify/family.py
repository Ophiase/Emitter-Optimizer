from dataclasses import dataclass

import numpy as np

from emitter_optimizer.kernel.placement.exact import Instance

SIDE = 100.0
COVERED_AREA = 0.7
CLUSTER_SHARE = 0.5
CLUSTERS = 5
CLUSTER_SPREAD = 0.06
WALL_LENGTHS = (0.15, 0.4)
MARGIN = 0.05
DECIMALS = 3


@dataclass(frozen=True, slots=True)
class Family:
    """A size of instance; its seeds draw uniform and clustered demand, and walls.

    The radius is such that the disks would cover `COVERED_AREA` of the map if they
    did not overlap, so that the emitters must choose and cannot cover everything.
    """

    points: int
    emitters: int
    walls: int

    def instance(self, seed: int) -> Instance:
        generator = np.random.default_rng([
            self.points,
            self.emitters,
            self.walls,
            seed,
        ])
        return Instance(
            name=f"n{self.points}-k{self.emitters}-w{self.walls}-s{seed}",
            points=self._demand(generator),
            weights=generator.integers(1, 101, self.points),
            walls=self._walls(generator),
            radius=round(
                SIDE * np.sqrt(COVERED_AREA / (self.emitters * np.pi)), DECIMALS
            ),
            emitters=self.emitters,
            width=SIDE,
            height=SIDE,
        )

    def _demand(self, generator: np.random.Generator) -> np.ndarray:
        clustered = int(self.points * CLUSTER_SHARE)
        centres = generator.uniform(0.0, SIDE, (CLUSTERS, 2))
        around = centres[generator.integers(0, CLUSTERS, clustered)]
        near = around + generator.normal(0.0, SIDE * CLUSTER_SPREAD, (clustered, 2))
        spread = generator.uniform(0.0, SIDE, (self.points - clustered, 2))
        return np.round(np.clip(np.concatenate((near, spread)), 0.0, SIDE), DECIMALS)

    def _walls(self, generator: np.random.Generator) -> np.ndarray:
        walls: list[np.ndarray] = []
        while len(walls) < self.walls:
            wall = self._wall(generator)
            inside = np.all((wall >= 0.0) & (wall <= SIDE))
            if inside and not any(_meet(wall, other) for other in walls):
                walls.append(wall)
        return np.array(walls).reshape(-1, 2, 2)

    def _wall(self, generator: np.random.Generator) -> np.ndarray:
        start = generator.uniform(SIDE * MARGIN, SIDE * (1.0 - MARGIN), 2)
        angle = generator.uniform(0.0, 2.0 * np.pi)
        length = generator.uniform(*WALL_LENGTHS) * SIDE
        end = start + length * np.array([np.cos(angle), np.sin(angle)])
        return np.round(np.stack((start, end)), DECIMALS)


def _meet(first: np.ndarray, second: np.ndarray) -> bool:
    return _straddles(first, second) and _straddles(second, first)


def _straddles(line: np.ndarray, segment: np.ndarray) -> bool:
    along = line[1] - line[0]
    sides = along[0] * (segment[:, 1] - line[0, 1]) - along[1] * (
        segment[:, 0] - line[0, 0]
    )
    return bool(sides[0] * sides[1] <= 0.0)
