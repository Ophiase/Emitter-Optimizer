# AGENTS.md

Instructions for any coding agent in this repository. Claude Code reads them
through `.claude/CLAUDE.md`.

## What this project is

A desktop application that places emitters on a map so that the signal they
cover, weighted by a density and blocked by obstacles, is maximized. The gain
is differentiable, so the search is a gradient descent.

## Language

English everywhere: code, comments, markdown, commits. The author may write to
you in French; answer in French, write files in English.

## Ideas

Everything starts in `ideas/`: one concept per file, short, a status tag on
every claim, and the map [ideas/README.md](ideas/README.md) kept current. A
choice absent from `ideas/` is not made; a question that belongs to the author
waits in [ideas/open.md](ideas/open.md). The plan, its branches and how to
resume it are in [ideas/roadmap.md](ideas/roadmap.md).

## Before working

Read [.agents/references.md](.agents/references.md), the reference projects
whose paths are in `.agents/local/projects.yaml` (gitignored; template:
[.agents/local.example.yaml](.agents/local.example.yaml)), and the Python rules
in [.agents/portable/rules/python.md](.agents/portable/rules/python.md).

## Toolchain

- Python 3.14, managed by `uv`; the environment comes from `pyproject.toml`
  and `uv.lock`. Never `pip install` into the environment.
- `just install` syncs it; `just run` opens the desktop window;
  `just test` runs pytest.
- `just lint` is `ruff check`, `ruff format --check` and `ty check`.
  `just precommit` fixes what it can.
- `just agent gate` is the one command to declare work done: `just check`
  (lint, tests, markdown) then `just guards`.
- `just audit` checks the lock, the vulnerabilities and the licences. It asks
  the network, so it stays out of the gate.
- CI exists and runs by hand only; activating it is the author's consent.

## Layout

The package is `src/emitter_optimizer/`, in a src layout: it is imported as
`emitter_optimizer`, never from the source folder. One concept per file,
seven entries per folder, two hundred lines per file
([layout](.agents/rules/layout.md)).

- `kernel/` — the JAX kernel: shapes, laws, scene, occlusion, coverage and
  descent. No GUI, no printing.
- `maps/` — Pillow and scikit-image load a density and a wall mask.
- `render/` — Pillow draws the map; plotly draws the gain.
- `gui/` — DearPyGui: the render window, the process controls, the parameters
  and the law editors.
- `service/` — FastAPI, pydantic models, the session and the local page for an
  agent.
- `settings/` at the root holds the default emitter and sensor functions the
  user edits.

## Python

Follow [.agents/portable/rules/python.md](.agents/portable/rules/python.md)
and this project's [.agents/rules/python.md](.agents/rules/python.md):
type annotations everywhere, names that say what a value means, short
functions, one concern per file, dataclasses for internal data and pydantic
only at a boundary. A comment records a **why** the code cannot express
([comments](.agents/portable/rules/comments.md)).

## Rules and checks

`.agents/portable/` is copied as is from the author's other repositories and
stays project-agnostic (`.agents/checks/portable.sh` guards it). Project
rules and checks go to `.agents/rules/` and `.agents/checks/`.
`.agents/checks/run.sh <check> <file>...` runs one; `just guards` runs them
all over the changed files.

The canon is [.agents/kanon.md](.agents/kanon.md); the `<>` in the README is
its sign.

## For agents: the local service

`emitter-optimizer serve` binds `127.0.0.1` and answers JSON, so an agent
drives the kernel through the local page. FastAPI serves the routes; the request
bodies are pydantic models (`service/models.py`); an invalid one is a `422`,
never a crash.

| Route | Effect |
| --- | --- |
| `GET /api/state` | map, emitters, gain, history, seed |
| `POST /api/run` | `{"iterations": 200, "seed": 0}` |
| `POST /api/place` | `{"positions": [[x, y], ...]}` or `{"emitters": 12, "seed": 0}` |
| `POST /api/stop` | abort the running descent |
| `GET /api/figure.png` | the current value map |
| `GET /api/export` | the state, as JSON |

`agent.just` wraps them: `just agent::serve`, `state`, `query`, `run`,
`place`, `stop`, `figure`, `save`. The skill
[.claude/skills/place-emitters/SKILL.md](.claude/skills/place-emitters/SKILL.md)
tells an agent when and how to use them.

## Done

A topic is done when `just agent gate` passes. Commit then, on its branch,
without being asked; never push. `main` is always valid: merge each finished
step into it, so that any stopping point can be judged from `main`.

## Branches

The agent works on `dev/<topic>` and merges into `main` once the gate passes,
or hands the branch over for review. Nothing is pushed without being asked.
The policy is recorded in [.agents/project.yaml](.agents/project.yaml).

## Never

- A network call the person did not ask for: no telemetry, analytics, crash
  report, update check, nor a font, script or style fetched from elsewhere.
- The name of a company, client or professional project in a tracked file or
  a commit.
- Commit or push without being asked.
