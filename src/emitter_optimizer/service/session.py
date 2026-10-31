import threading
from dataclasses import dataclass, field

import jax
import jax.numpy as jnp
import numpy as np

from emitter_optimizer.kernel import (
    Coverage,
    Descender,
    DescentSettings,
    HardOcclusion,
    Physics,
    Scene,
)
from emitter_optimizer.render import GainChart, MapImage
from emitter_optimizer.service.models import (
    PlaceRequest,
    RunRequest,
    State,
    StopResult,
)


@dataclass
class Session:
    scene: Scene
    physics: Physics
    emitters: int = 15
    step_size: float = 0.01
    seed: int = 0
    positions: np.ndarray | None = None
    history: list[float] = field(default_factory=list)
    _descender: Descender | None = field(default=None, repr=False)
    _running: bool = False
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def __post_init__(self) -> None:
        if self.positions is None:
            self.positions = self._sample(self.seed)

    def state(self) -> State:
        positions = (
            self.positions if self.positions is not None else self._sample(self.seed)
        )
        gain = float(self._coverage().gain(jnp.asarray(positions)))
        return State(
            map_scale=(
                float(self.scene.bounds[0]),
                float(self.scene.bounds[1]),
            ),
            grid_size=(self.scene.grid.rows, self.scene.grid.columns),
            emitters=len(positions),
            positions=tuple(
                (float(point[0]), float(point[1])) for point in np.asarray(positions)
            ),
            gain=gain,
            history=tuple(self.history),
            seed=self.seed,
            running=self._running,
        )

    def place(self, request: PlaceRequest) -> State:
        with self._lock:
            if request.seed is not None:
                self.seed = request.seed
            if request.positions is not None:
                self.positions = np.asarray(request.positions, dtype=np.float64)
                self.emitters = len(self.positions)
            elif request.emitters is not None:
                self.emitters = request.emitters
                self.positions = self._sample(self.seed)
            self.history = []
        return self.state()

    def run(self, request: RunRequest) -> State:
        with self._lock:
            if request.seed is not None:
                self.seed = request.seed
                self.positions = self._sample(self.seed)
            self.emitters = len(self.positions) if self.positions is not None else 0
            settings = DescentSettings(
                emitters=self.emitters,
                steps=request.iterations,
                step_size=self.step_size,
                seed=self.seed,
            )
            descender = Descender(self.scene, self.physics, settings)
            self._descender = descender
            self._running = True
        try:
            result = descender.run()
        finally:
            with self._lock:
                self._descender = None
                self._running = False
        with self._lock:
            self.positions = np.asarray(result.positions, dtype=np.float64)
            self.history = list(result.history)
        return self.state()

    def stop(self) -> StopResult:
        descender = self._descender
        if descender is None or not self._running:
            return StopResult(aborted=False)
        descender.stop()
        return StopResult(aborted=True)

    def figure(self) -> bytes:
        positions = (
            self.positions if self.positions is not None else self._sample(self.seed)
        )
        return MapImage(self.scene, self._coverage()).png(jnp.asarray(positions))

    def chart(self) -> str:
        return GainChart(self.history).html()

    def _coverage(self) -> Coverage:
        return Coverage(self.scene, HardOcclusion(), self.physics)

    def _sample(self, seed: int) -> np.ndarray:
        key = jax.random.key(seed)
        return np.asarray(self.scene.sample(key, 1, self.emitters)[0], dtype=np.float64)
