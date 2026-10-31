from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DescentSettings:
    emitters: int
    steps: int
    starts: int = 1
    optimizer: str = "adam"
    step_size: float = 0.01
    report_every: int = 50
    seed: int = 0
