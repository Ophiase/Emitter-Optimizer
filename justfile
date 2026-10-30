mod agent

default:
    @just --list --list-submodules

[group("install")]
[doc("Create the uv environment for Python 3.14 and install every dependency")]
install:
    uv sync

[group("user")]
[doc("Start the optimizer window")]
run:
    uv run python -m emitter_optimizer

[group("dev")]
[doc("Rewrite the code with ruff, then type-check it with ty")]
precommit:
    uv run ruff check . --fix
    uv run ruff format .
    uv run ty check .

[group("dev")]
[doc("Report style and typing defects without changing the code")]
lint:
    uv run ruff check .
    uv run ruff format --check .
    uv run ty check .

[group("dev")]
[doc("Run the test suite")]
test:
    uv run pytest

[group("dev")]
[doc("Everything that must pass before declaring work done")]
check: lint test rumdl

rumdl:
    rumdl check .

rumdl-fmt:
    rumdl fmt .

[group("dev")]
[doc("Run the project's and the portable checks over every changed file")]
[script("bash")]
guards:
    status=0
    for check in markdown french comment-slop hardcoded-url portable folder-size yaml-extension config-format file-length version; do
        just _guard "$check" || status=1
    done
    exit $status

_guard check:
    @.agents/portable/checks/changed-files.sh | xargs -r -d '\n' .agents/checks/run.sh {{ check }}
