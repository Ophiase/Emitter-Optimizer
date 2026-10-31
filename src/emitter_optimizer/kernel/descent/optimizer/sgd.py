from dataclasses import dataclass

import optax

from emitter_optimizer.kernel.descent.optimizer.optimizer import Optimizer


@dataclass(frozen=True, slots=True)
class SGD(Optimizer):
    momentum: float = 0.9
    nesterov: bool = True

    def to_optax(self, rate: float) -> optax.GradientTransformation:
        return optax.sgd(rate, momentum=self.momentum, nesterov=self.nesterov)
