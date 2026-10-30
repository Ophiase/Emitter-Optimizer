# Contributing

The project is written in English: code, comments, markdown and commits.

## Setup

Python 3.14 and [uv](https://docs.astral.sh/uv/) are the only prerequisites.

```sh
just install
just agent install-hooks
```

## Before opening a change

```sh
just agent gate
```

The gate runs `just check` (ruff, ty, pytest, rumdl) then `just guards`
(the project and portable checks over the changed files). A change that does
not pass it is not ready.

Read [AGENTS.md](AGENTS.md) and the rules it links to; they apply to people as
much as to agents.
