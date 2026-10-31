import pytest

from emitter_optimizer.kernel import (
    SGD,
    Adam,
    AdamW,
    DescentSettings,
    Lion,
    NAdam,
    Optimizer,
)


@pytest.mark.parametrize(
    "optimizer",
    [Adam(), AdamW(), NAdam(), Lion(), SGD()],
)
def test_each_optimizer_builds_an_optax_transformation(optimizer: Optimizer) -> None:
    assert optimizer.to_optax(0.01) is not None


def test_the_settings_default_to_a_named_optimizer() -> None:
    settings = DescentSettings(emitters=2, steps=2)

    assert settings.optimizer == Adam()
