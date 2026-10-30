import importlib
import pkgutil

import emitter_optimizer


def test_every_module_imports() -> None:
    package = emitter_optimizer
    modules = pkgutil.walk_packages(package.__path__, package.__name__ + ".")
    for module in modules:
        if module.name.endswith(".__main__"):
            continue
        importlib.import_module(module.name)
