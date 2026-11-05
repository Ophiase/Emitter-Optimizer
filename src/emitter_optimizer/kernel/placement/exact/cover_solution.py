from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CoverSolution:
    """The candidates a program chose, their weight, and its bound on any choice."""

    chosen: tuple[int, ...]
    weight: int
    bound: int
