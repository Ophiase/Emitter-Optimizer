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
- `just install` syncs it; `just run` starts the window; `just test` runs
  pytest.
- `just lint` is `ruff check`, `ruff format --check` and `ty check`.
  `just precommit` fixes what it can.
- `just agent gate` is the one command to declare work done: `just check`
  (lint, tests, markdown) then `just guards`.

## Layout

The package is `src/emitter_optimizer/`, in a src layout: it is imported as
`emitter_optimizer`, never from the source folder. One concept per file,
seven entries per folder, two hundred lines per file
([layout](.agents/rules/layout.md)).

- `engine/` — geometry, maps and the solver: no GUI, no printing.
- `gui/` — Dear PyGui windows and the configuration they edit.
- `settings/` at the root holds the default emitter and sensor functions the
  user edits in the window.

## Python

Follow [.agents/portable/rules/python.md](.agents/portable/rules/python.md):
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
drives the engine without a window. The request bodies are pydantic
models (`service/models.py`); a invalid one is a `422`, never a crash.

| Route | Effect |
| --- | --- |
| `GET /api/state` | map, emitters, gain, history, seed |
| `POST /api/run` | `{"iterations": 200, "seed": 0}` |
| `POST /api/place` | `{"positions": [[x, y], ...]}` or `{"emitters": 12, "seed": 0}` |
| `POST /api/stop` | abort the running descent |
| `GET /api/figure.png` | the current value map |
| `GET /api/export` | the state, as JSON |

`agent.just` wraps them: `just agent::serve`, `state`, `query`, `run`,
`place`, `stop`, `figure`, `export`. The skill
[.claude/skills/place-emitters/SKILL.md](.claude/skills/place-emitters/SKILL.md)
tells an agent when and how to use them.

## Done

A topic is done when `just agent gate` passes. Commit then, on its branch,
without being asked; never push.

## Branches

The agent works on `dev/<topic>` and merges into `main` once the gate passes,
or hands the branch over for review. Nothing is pushed without being asked.
The policy is recorded in [.agents/project.yaml](.agents/project.yaml).

## Never

- A network call the person did not ask for: no telemetry, analytics, crash
  report, update check, nor a font, script or style fetched from elsewhere.
  The fonts in `resources/font/` are local on purpose.
- The name of a company, client or professional project in a tracked file or
  a commit.
- Commit or push without being asked.
