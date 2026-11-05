from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class Scores:
    """One instance: its proved weights, and what each method covered."""

    name: str
    points: int
    emitters: int
    walls: int
    lower: int
    upper: int
    vertices: int
    columns: int
    exact_seconds: float
    random: float
    demand_sites: int
    grid_16: int
    grid_32: int
    grid_64: int
    greedy: int
    descent: int
    relocation: int
    engine_seconds: float

    def record(self) -> dict[str, object]:
        return asdict(self)
