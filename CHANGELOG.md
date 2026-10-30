# CHANGELOG

Milestones of the whole project; the version is in `VERSION`.

## Unreleased

- **The project has a face**: `CONTRIBUTORS.md` records that it started in
  2023 by hand and was modernized in 2026 with an agent; the README says who
  it is for, what the baseline model is, and how to try it in two
  commands.
- **The 2023 model stays the baseline**: newer models are compared against
  it, never silently replace it ([ideas/model](ideas/model/README.md)).
- **`ideas/` is the core again**: the thesis, the vision, the origin, the
  architecture, the engine, the model, the milestones and the roadmap, one
  concept per file. `AGENTS.md` reads it first.
- **The roadmap** names each step, its branch and its acceptance, so a later
  session resumes without asking: M1 a NumPy engine, M2 an agent protocol,
  M3 a model worth publishing, M4 a thin face.

## 2.0.0 — 2026-10-30

- **The project joins the Kanon.** `AGENTS.md`, the portable layer in
  `.agents/`, the sign `<>` in the README and the gate `just agent gate`.
- **uv and Python 3.14.** Conda, the shell installer and the `Makefile` are
  replaced by `pyproject.toml`, `uv.lock` and a `justfile`.
- **A src layout**: the code moves to `src/emitter_optimizer/` and every
  import is absolute against the package.
- **ruff and ty** replace the absent linter and type checker; the code is
  rewritten to their standard.
- **TensorFlow 2.22** is the first release with a CPython 3.14 wheel, and is
  pinned as a pre-release until 2.22 is final.

## 1.3 - 2024

## 1.2 - 2023
