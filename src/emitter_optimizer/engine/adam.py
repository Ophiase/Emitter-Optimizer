from dataclasses import dataclass

import numpy as np

from emitter_optimizer.engine.laws import Positions

ADAM_BETA1 = 0.9
ADAM_BETA2 = 0.999
ADAM_EPSILON = 1e-8


@dataclass
class Adam:
    learning_rate: float
    first_moment: Positions
    second_moment: Positions
    steps: int = 0

    def step(self, gradient: Positions) -> Positions:
        self.steps += 1
        self.first_moment = (
            ADAM_BETA1 * self.first_moment + (1.0 - ADAM_BETA1) * gradient
        )
        self.second_moment = (
            ADAM_BETA2 * self.second_moment + (1.0 - ADAM_BETA2) * gradient**2
        )
        first = self.first_moment / (1.0 - ADAM_BETA1**self.steps)
        second = self.second_moment / (1.0 - ADAM_BETA2**self.steps)
        return self.learning_rate * first / (np.sqrt(second) + ADAM_EPSILON)
