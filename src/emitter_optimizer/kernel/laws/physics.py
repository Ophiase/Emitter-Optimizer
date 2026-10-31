from dataclasses import dataclass

from emitter_optimizer.kernel.laws.law import Law


@dataclass(frozen=True, slots=True)
class Physics:
    """`emitter` maps a distance to a signal, `sensor` a received signal to a score."""

    emitter: Law
    sensor: Law
