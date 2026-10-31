from pydantic import BaseModel


class StopResult(BaseModel):
    aborted: bool
