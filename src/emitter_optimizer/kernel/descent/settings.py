from dataclasses import dataclass, field

from emitter_optimizer.kernel.descent.optimizer import Adam, Optimizer


@dataclass(frozen=True, slots=True)
class DescentSettings:
    emitters: int
    steps: int
    starts: int = 1
    optimizer: Optimizer = field(default_factory=Adam)
    step_size: float = 0.01
    report_every: int = 50
    seed: int = 0
