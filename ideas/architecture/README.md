# Architecture — the principles

**[sketch]** Small, sharp pieces, each with one job, joined by contracts that
outlive the code. The shape follows the author's other projects: a headless
core, a local protocol, a thin face.

- [kernel.md](kernel.md) — the author's decisions on the engine.
- [stack.md](stack.md) — Python 3.14, JAX, uv, ruff, ty, just; what stays
  out.
- [layers.md](layers.md) — engine, service, ui; what depends on what.
- [agent-interop.md](agent-interop.md) — one local protocol for agents and
  for the window.
- [zero-telemetry.md](zero-telemetry.md) — nothing leaves the machine
  without a yes.
- [language.md](language.md) — Python stays; Rust only behind a benchmark.
- [faces.md](faces.md) — what a face is for, and where DearPyGui stops.
