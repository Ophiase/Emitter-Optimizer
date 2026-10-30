"""Loading one of the two laws a person edits."""

from pathlib import Path
from typing import Any, cast

from emitter_optimizer.engine.types import Derivative, Law, SignalFunction

ENTRY = "eval"
DERIVATIVE = "derivative"


def load_law(source: str) -> Law:
    namespace: dict[str, Any] = {}
    exec(source, namespace)  # ruff: ignore[exec-builtin]
    value = cast(SignalFunction, namespace[ENTRY])
    derivative = cast(Derivative | None, namespace.get(DERIVATIVE))
    return Law(value, derivative)


def load_law_file(path: Path) -> Law:
    return load_law(path.read_text(encoding="utf-8"))
