# Project instructions

The rules are in [AGENTS.md](../../AGENTS.md) at the repository root; read it
first and follow it over this pointer.

The gate is `just agent gate`. The checks in `.agents/checks/` are the
source; Kilo documents no lifecycle hook, so run the gate yourself, and
`just agent install-hooks` once to run `just guards` on every commit.
