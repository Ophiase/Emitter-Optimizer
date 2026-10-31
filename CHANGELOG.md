# CHANGELOG

Milestones of the whole project; the version is in `VERSION`.

## Unreleased

- **The legacy engine and the window are gone**: the CLI, the service and the
  page all run on the JAX kernel; `engine/` and `gui/` are deleted, not kept
  as shims.
- **The stack is modern**: plotly draws the interactive gain, scikit-image
  finds the wall contours, Pillow renders the maps; matplotlib, OpenCV and
  DearPyGui left the dependencies.
- **The face is a local page**: FastAPI serves it, `just run` opens it, and the
  page drives the same routes as an agent.
- **The kernel is one concept per module**: `shapes/`, `descent/` and
  `occlusion/` hold one class each; `Scene.visibility` owns the ray crossing,
  and the free geometry module is gone.
- **The length rule is a flag, not a law**: past 80 lines of code a check
  prints a note, past 200 it fails; a concept with several classes becomes a
  package, not a four-class file.
- **An is-a hierarchy is an ABC**: `Occlusion` is an `ABC`, `HardOcclusion` and
  `SoftOcclusion` subclass it, one class per file under `kernel/occlusion/`;
  `Protocol` is now refused by a guard in `src/`.
- **The author's decisions are recorded**: JAX and optax are the engine, laws
  are `jax.numpy` with `eval` only, matplotlib and OpenCV leave, walls become
  an absorption field, the window and a Rust kernel stay open
  ([kernel](ideas/architecture/kernel.md)).
- **The service is FastAPI.** The standard-library handler, the hand-written
  router and the error mapping are gone: FastAPI serves the routes, pydantic
  validates the bodies, and `ServiceSettings` holds the host and the port.
  `TestClient` replaces the server threads in the tests.

## 2.1.1 — 2026-10-31

- **A README built on generated figures**: the problem, five use cases, the
  path of each emitter and the benchmark chart, each computed by
  `just figures` from a seeded run. The page keeps the equations and drops
  the prose the figures carry.
- **A crossover is sketched**: place fiducial markers so that a pose is
  observable from every viewpoint, using the point-cloud project as the
  evaluator ([ideas/crossover.md](ideas/crossover.md)).

## 2.1.0 — 2026-10-31

- **Five named use cases** replace the four anonymous benchmark rows: a
  uniform map, a farm with crop rows and a hedge, a building with two rooms and
  a corridor, a shop with three demand peaks, and a wide map. `just bench`
  writes the table and a figure per case.
- **Generated figures and a GIF**: `just figures` writes the before, after and
  gain figures and the descent animation into `docs/figures/`, from a seeded
  run. The README shows them instead of the 2021 screenshots.
- **The project is agent-native**: `emitter-optimizer serve` binds
  `127.0.0.1` and answers `/api/state`, `/run`, `/place`, `/stop`,
  `/figure.png` and `/export`. Requests and state are pydantic models, the
  router answers an invalid body with a `422` instead of a traceback, and
  `agent.just` wraps every route. A skill tells an agent when to use them.
- **The GUI is a typed client again**: `Application.__call__` runs the
  loop, the layout is parsed into frozen specs, and an unknown content name
  fails loudly.
- **The README is rewritten in the shape of the author's other projects**:
  badges, a start-here table, the problem in plain words, the model in one
  screen with its symbols, the gradient and its meaning, the commands, the
  what-you-can-change table, the status, the repository, the prior art, the
  roadmap, and the agent's name.
- **The 3D case gets a direction**: an implicit energy, sampled instead of
  voxelized, with a quasi-Monte Carlo domain and a fixed seed; the analytic
  gradient stays, and JAX is a seam, not a dependency
  ([ideas/model/implicit-energy.md](ideas/model/implicit-energy.md)).
- **A published benchmark**: `just bench` writes
  `docs/benchmark/results.md` from four fixed situations, with the initial
  and final gain, the improvement and the time. The wall situation is the
  measured hot spot.
- **A command line**: `emitter-optimizer run` takes a density, a collision
  map, the laws, a seed and the parameters, and writes `positions.csv`,
  `history.csv`, `figure.png` and `summary.json`. `just demo` runs it on the
  demo map; `emitter-optimizer window` opens the window.
- **The engine is NumPy.** The gain, its value map and its gradient are
  arrays; the descent is a projected Adam step with a best-seen safeguard.
  TensorFlow and Keras are gone, with 600 MB and a release candidate.
- **The gradient is exact**, tested against a central difference; a law
  without a derivative falls back to one. A law is a plain NumPy function.
- **A wall test, a density test and a no-GUI/no-framework test** join the
  suite, which now runs in under a second.
- `engine/` splits into `maps/` and the rest; the engine imports no window.
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
