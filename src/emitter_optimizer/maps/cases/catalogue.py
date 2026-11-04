from emitter_optimizer.maps.cases.situation import Situation
from emitter_optimizer.service.paths import RESOURCES_DIRECTORY

CASES_DIRECTORY = RESOURCES_DIRECTORY / "cases"
SITUATIONS = (
    Situation(
        CASES_DIRECTORY / "garden", "Sprinklers over allotment beds.", 120.0, 32, 24
    ),
    Situation(
        CASES_DIRECTORY / "beach", "Lifeguards over the bathing strip.", 150.0, 32, 5
    ),
    Situation(
        CASES_DIRECTORY / "marina",
        "Wi-Fi over a marina and its old town.",
        300.0,
        32,
        8,
    ),
    Situation(
        CASES_DIRECTORY / "harbor",
        "Lamps along the quays of a ferry port.",
        400.0,
        32,
        14,
    ),
    Situation(
        CASES_DIRECTORY / "ramparts", "Sirens inside a walled old town.", 350.0, 32, 4
    ),
)
CASE_NAMES = tuple(situation.name for situation in SITUATIONS)


def situation_named(name: str) -> Situation:
    return SITUATIONS[CASE_NAMES.index(name)]
