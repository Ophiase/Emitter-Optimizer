from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GridShape:
    rows: int
    columns: int

    def __post_init__(self) -> None:
        if self.rows <= 0 or self.columns <= 0:
            message = f"a grid has cells, not {self.rows} x {self.columns}"
            raise ValueError(message)

    @property
    def cells(self) -> int:
        return self.rows * self.columns
