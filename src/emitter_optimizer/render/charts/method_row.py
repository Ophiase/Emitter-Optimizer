from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MethodRow:
    """The gain of each method on one case, with a random placement as the base."""

    case: str
    emitters: int
    random: float
    greedy: float
    descent: float

    def above_random(self, gain: float) -> float:
        return 100.0 * (gain - self.random) / abs(self.random)
