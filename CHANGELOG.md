# CHANGELOG

Milestones of the whole project; the version is in `VERSION`.

## Unreleased

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
