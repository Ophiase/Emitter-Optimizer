from typing import Annotated

from pydantic import BaseModel, Field


class State(BaseModel):
    map_scale: tuple[float, float]
    grid_size: tuple[int, int]
    emitters: Annotated[int, Field(ge=0)]
    positions: tuple[tuple[float, float], ...]
    gain: float
    history: tuple[float, ...]
    seed: Annotated[int, Field(ge=0)]
    running: bool
