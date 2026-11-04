from dataclasses import dataclass

import optax

from emitter_optimizer.kernel.descent.optimizer.optimizer import Optimizer


@dataclass(frozen=True, slots=True)
class Lion(Optimizer):
    def to_optax(self, rate: optax.ScalarOrSchedule) -> optax.GradientTransformation:
        return optax.lion(rate)
