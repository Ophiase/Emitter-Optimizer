mod agent

default:
    @just --list --list-submodules

[group("install")]
[doc("Create the uv environment for Python 3.14 and install every dependency")]
install:
    uv sync

[group("user")]
[doc("Start the optimizer window")]
@run *args:
    uv run python -m emitter_optimizer window {{ args }}

[group("user")]
[doc("Optimize the demo map and write out/demo: positions, history, figure, summary")]
@demo:
    uv run python -m emitter_optimizer run --density resources/map/value_001.png --collisions resources/map/collide_001.png --emitters 15 --iterations 200 --seed 0 --out out/demo

[group("user")]
[doc("Optimize a case by name and write out/<name>: just case garden --iterations 50")]
@case name *args:
    uv run python -m emitter_optimizer run --case {{ name }} --out out/{{ name }} {{ args }}

[group("user")]
[doc("The cases beyond the plane: just space plants, thomson, globe, building or urea")]
space name:
    uv run python -m scripts.spaces.{{ name }}

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
[doc("Check the lock, the known vulnerabilities and the licences; asks the network, so it stays out of the gate")]
audit:
    uv lock --check
    uv audit
    uv run --with pip-licenses pip-licenses --partial-match --fail-on "GPL;AGPL;SSPL"

[group("dev")]
[doc("Run the published benchmark into docs/benchmark/results.md")]
bench:
    uv run python -m scripts.bench

[group("dev")]
[doc("Solve the reference set to its proved optima and measure the engine against them")]
certify:
    uv run python -m scripts.certify

[group("dev")]
[doc("Compile the report on the proved optimum to report/build/; needs typst")]
report:
    mkdir -p report/build
    typst compile --root . report/certified-coverage.typ report/build/certified-coverage.pdf

[group("dev")]
[doc("Recompute the README figures into docs/figures: the demo, the cases and the mosaic")]
figures:
    uv run python -m scripts.figures

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
    for check in markdown markdown-smell french comment-slop no-suppression no-module-docstring one-class no-protocol callable-alias hardcoded-url portable folder-size yaml-extension config-format file-length version; do
        just _guard "$check" || status=1
    done
    exit $status

_guard check:
    @.agents/portable/checks/changed-files.sh | xargs -r -d '\n' .agents/checks/run.sh {{ check }}
