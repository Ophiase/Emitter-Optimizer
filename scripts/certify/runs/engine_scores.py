from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EngineScores:
    """What each stage of the engine covers, each scored by the instance itself."""

    greedy: int
    descent: int
    relocation: int
    seconds: float
