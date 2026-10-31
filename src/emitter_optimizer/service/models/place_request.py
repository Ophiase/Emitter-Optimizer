from typing import Annotated

from pydantic import BaseModel, Field


class PlaceRequest(BaseModel):
    positions: tuple[tuple[float, float], ...] | None = None
    emitters: Annotated[int, Field(ge=1)] | None = None
    seed: Annotated[int, Field(ge=0)] | None = None
