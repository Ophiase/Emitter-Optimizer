# Python or Rust

**[sketch]** Python stays. Rust is a possible kernel later, behind the same
API, and only a benchmark can ask for it. The choice is recorded here so it is
not reopened at every session.

## Why Python, for this project specifically

1. **The user's laws are Python.** `phi` and `psi` are the point of the
   project: a person writes their physics in a file, edits it in a window,
   and sees the curve. Rust would need either an embedded Python, a small
   expression language, or a compile step for the user — a product decision,
   not an optimization.
2. **The hot loop is NumPy, not the interpreter.** The gain is a handful of
   broadcast operations on `(cells, emitters)` arrays; the GIL is released
   during them. The per-iteration Python cost is a few dozen calls.
3. **The problem is small.** Fifteen emitters, a 32×32 grid: milliseconds. A
   compiled core would optimize the part that already costs nothing.
4. **The faces are Python.** The window, the service, the command line, the
   tests: one language, one toolchain, one gate.

## When Rust would be right

| Trigger | Why Rust |
| --- | --- |
| A benchmark situation above one second per run | the loop, not the calls, dominates |
| Embedding in a native application, a game, a browser (WASM) | no Python runtime available |
| A shared geometry core with the point-cloud project | one crate, two products |
| Shipping a single binary to a person who has no Python | distribution |

**[caution]** None of these is true today. A Rust rewrite now would cost weeks
and buy milliseconds; it would also put the user's laws behind a boundary.

## If it comes

- A crate `emitter-core` with the gain, the distance strategies and the
  optimizer, no I/O, no printing.
- `pyo3` + `maturin` bindings, NumPy arrays without copy, as in the
  point-cloud project.
- The user's laws stay Python: the core calls back through a function
  pointer, or accepts a small DSL compiled once. Both are real work and must
  be justified by the benchmark.
- The Python engine stays as the reference implementation, so a result can
  always be checked against it. Two implementations, one property test.

## [question]

Is the shared geometry with the point-cloud project worth a common crate? It
is the only argument that would make Rust attractive before a benchmark asks
for it. It belongs to the author ([../open.md](../open.md)).
