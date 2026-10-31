from typing import Protocol, runtime_checkable

from emitter_optimizer.kernel.descent.step import Step


@runtime_checkable
class StepCallback(Protocol):
    def __call__(self, step: Step, /) -> None: ...
