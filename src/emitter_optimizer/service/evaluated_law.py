from dataclasses import dataclass
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import cast

from jax import Array

from emitter_optimizer.kernel import Law


@dataclass(frozen=True, slots=True)
class EvaluatedLaw:
    """A user's `eval` function, run with JAX arrays so it can be traced."""

    function: Law

    @classmethod
    def from_source(cls, source: str, name: str = "user") -> EvaluatedLaw:
        """Load the `eval` function the window's editor holds."""
        with NamedTemporaryFile(
            "w", suffix=".py", prefix=f"{name}_", delete=False, encoding="utf-8"
        ) as file:
            file.write(source)
            path = Path(file.name)
        try:
            return cls.from_file(path)
        finally:
            path.unlink(missing_ok=True)

    @classmethod
    def from_file(cls, path: Path) -> EvaluatedLaw:
        spec = spec_from_file_location(f"emitter_optimizer.laws.{path.stem}", path)
        if spec is None or spec.loader is None:
            message = f"cannot load the law: {path}"
            raise ValueError(message)
        module = module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as error:
            message = f"cannot load the law {path}: {error}"
            raise ValueError(message) from error
        function = getattr(module, "eval", None)
        if not callable(function):
            message = f"{path} does not define a callable eval"
            raise ValueError(message)
        return cls(cast(Law, function))

    def __call__(self, values: Array, /) -> Array:
        return self.function(values)
