# Reference projects — how the author works

Read these before proposing a structure, a convention or a style. Their
paths, and why each one is readable, are in `.agents/local/projects.yaml`
(gitignored; template: [local.example.yaml](local.example.yaml)). Read only;
take the **method**, never the content.

**Absolute rule**: treat every project below as private unless its
`.agents/guard.yaml` says otherwise. Never name them, quote them or describe
their content in a tracked file or a commit. Refer to them by role only.

## Sibling reference

A Rust monorepo of the author, the most recent state of the conventions:
`ideas/` as the core, `.agents/portable/` copied from it, workspace lints,
`justfile` modules, hooks, the merge-master skill. This repository was its
inspiration; that one now carries the newer agent layer.

## Research reference

- `ideas/` first: short files, one notion each, a map, status tags.
- A report in **Typst**, figures drawn natively from data.
- Python to check by brute force, never to explain.

## Industrial Python reference

- `AGENTS.md` for every agent, `.claude/CLAUDE.md` importing it.
- Written architecture decisions, `justfile`, strict tooling (uv, ruff),
  changelog and version. The Python skin follows it.

## Founding case

A private record where the need first appeared. It may hold identifying
health data: read it locally only, take the need and never the content,
never send it to an external service, follow its own `AGENTS.md`, and never
link this project to it in a tracked file. Its code is deliberately rough:
a record of needs, not a model.

## Before reusing

Each project's `.agents/guard.yaml`, then `.agents/local/guard.yaml`, says
what may be reused, attributed or published; read them first. A missing
guard is permissive, never confidential.
