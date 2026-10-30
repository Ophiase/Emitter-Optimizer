from typing import Annotated

from pydantic import BaseModel, Field

DEFAULT_ITERATIONS = 50
MAXIMUM_ITERATIONS = 100_000


class State(BaseModel):
    map_scale: tuple[float, float]
    grid_size: tuple[int, int]
    emitters: Annotated[int, Field(ge=0)]
    positions: tuple[tuple[float, float], ...]
    gain: float
    history: tuple[float, ...]
    seed: Annotated[int, Field(ge=0)]
    running: bool


class RunRequest(BaseModel):
    """Run the descent; a seed re-draws the emitters before climbing."""

    iterations: Annotated[int, Field(ge=0, le=MAXIMUM_ITERATIONS)] = DEFAULT_ITERATIONS
    seed: Annotated[int, Field(ge=0)] | None = None


class PlaceRequest(BaseModel):
    positions: tuple[tuple[float, float], ...] | None = None
    emitters: Annotated[int, Field(ge=1)] | None = None
    seed: Annotated[int, Field(ge=0)] | None = None


class StopResult(BaseModel):
    aborted: bool


class Health(BaseModel):
    ok: bool = True
