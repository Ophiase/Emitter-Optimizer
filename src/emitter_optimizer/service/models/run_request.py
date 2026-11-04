from typing import Annotated

from pydantic import BaseModel, Field

DEFAULT_ITERATIONS = 50
MAXIMUM_ITERATIONS = 100_000


class RunRequest(BaseModel):
    """Run the descent; a seed re-draws the emitters before climbing.

    `relocate` then moves the emitters a gradient cannot, and polishes the result.
    """

    iterations: Annotated[int, Field(ge=0, le=MAXIMUM_ITERATIONS)] = DEFAULT_ITERATIONS
    seed: Annotated[int, Field(ge=0)] | None = None
    relocate: bool = False
