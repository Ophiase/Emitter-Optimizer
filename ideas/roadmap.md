# Roadmap

**[sketch]** The ordered steps, one branch each. It is written so that an
agent starting a new session can pick the first unchecked step, read the files
the step names, and work without asking. A step is done when `just agent gate`
passes **and** its acceptance sentence is true.

## Current state

**[fact]** 2026-10-31. The application runs on the kernel; the old `engine/`,
the DearPyGui window, matplotlib and OpenCV are gone. JAX, optax, plotly,
scikit-image and Pillow are the stack; the face is a local FastAPI page. The
gate is green, 14 tests pass, and the next work is the model, not the
migration. The last release is v2.1.1; nothing is pushed.

## How to resume

1. Read [AGENTS.md](../AGENTS.md), then [ideas/README.md](README.md), then this
   file.
2. `git status`, `git branch --show-current`, `just agent gate`: the tree must
   be clean and the gate green before a step starts.
3. Take the first step that is not done. Its branch is named beside it; create
   it from `main` if it does not exist.
4. A step ends with a commit on its branch, a `CHANGELOG.md` entry under
   `## Unreleased`, and this file updated: checkbox, date, one line of result.
5. A question that belongs to the author goes to [open.md](open.md); it is not
   settled in code.

## Phase 0 — split the kernel before migrating — done

**[done]** 2026-10-31, `dev/refactor-stack`. A Python module holds one class;
when a concept needs several, it becomes a package with one module per class.
The kernel is `shapes/` (`Extent`, `GridShape`), `descent/` (settings, step,
result, progress, runner) and `occlusion/` (the `ABC`, hard, soft), and still
holds seven entries. The length rule is a flag, not a law: past 80 lines of
code a check prints a note, past 200 it fails; `scene.py` and `runner.py` are
the only notes, and each stays one concept.

## Phase 1 — `dev/engine`: M1, a headless engine

Done on 2026-10-30, in `dev/engine-numpy`.

- [x] **1.1 Remove the GUI from the import path.** (2026-10-30) The engine
  imports no `gui`, no `dearpygui`; a test imports it and checks that neither
  `dearpygui` nor `tensorflow` entered `sys.modules`.
- [x] **1.2 Replace TensorFlow by NumPy.** (2026-10-30) The gain, its value map
  and the obstacle test are arrays; `Field` exposes `gain`, `value_map`,
  `gradient` and `gain_and_gradient` ([gain](engine/gain.md)). TensorFlow and
  Keras left the dependencies.
- [x] **1.3 Exact gradient for the built-in laws.** (2026-10-30) The gradient is
  `-(1/P) sum_x psi'(r) phi'(d) (x - y)/d mu(x) pass_C(x, y)`, in one pass with
  the gain ([optimizer](engine/optimizer.md)). A test compares it to a central
  difference.
- [x] **1.4 A numeric gradient for any callable.** (2026-10-30) `Law.slope`
  returns the exact derivative when the law declares one, a central difference
  otherwise ([functions](engine/functions.md)).
- [x] **1.5 An optimizer with bounds.** (2026-10-30) Projected Adam on the
  ascent direction, the best positions kept so the gain never drops, `abort`
  and the update callback. *Restarts are not done*; multi-start is a later
  step.
- [x] **1.6 A headless command.** (2026-10-30) `emitter-optimizer run` takes a
  density, a collision map, the laws, a seed and the parameters, and writes
  `positions.csv`, `history.csv`, `figure.png` and `summary.json`; `just demo`
  runs it on the demo map. `emitter-optimizer window` opens the local page.
- [x] **1.7 A benchmark.** (2026-10-30) `just bench` runs four situations
  (uniform, density, walls, a wide non-square grid) and writes
  `docs/benchmark/results.md`: initial and final gain, improvement, seconds.
  *Measured*: the wall situation costs twenty times the same map without
  walls; the obstacle test is the hot spot, which is what Phase 3.1 attacks.
- [x] **1.8 DearPyGui calls the new engine.** (2026-10-30, superseded by the
  local page) The window builds a `Law` from the edited files and passes it to
  the solver; `just check` never imports `dearpygui`.

Dependencies: 1.2 before 1.3; 1.3 and 1.5 before 1.6; 1.6 before 1.7.

## Phase 2 — `dev/agent`: M2, agent-native

Done on 2026-10-30, in `dev/service`.

- [x] **2.1 A local service.** (2026-10-30) `emitter-optimizer serve` binds
  `127.0.0.1` and exposes `/api/state`, `/api/run`, `/api/place`, `/api/stop`,
  `/api/figure.png`, `/api/export` and `/api/health`. Requests and state are
  pydantic models; the router turns an invalid body into a `422` and an unknown
  route into a `404` ([agent-interop](architecture/agent-interop.md)).
- [x] **2.2 `agent.just`.** (2026-10-30) `just agent::serve`, `url`, `state`,
  `query`, `run`, `place`, `stop`, `figure`, `save`; every argument is
  validated and passed positionally.
- [x] **2.3 A skill.** (2026-10-30) `.claude/skills/place-emitters/SKILL.md`:
  start the service, place, run, figure, export, and what a good answer
  contains (gain before and after, seed, emitters, figure).
- [x] **2.4 Determinism.** (2026-10-30) The service takes a seed on `run` and
  `place`; two runs with the same seed give the same positions, tested.

## Phase 3 — `dev/model`: M3, a model worth publishing

- [ ] **3.1 Soft occlusion.** A smooth visibility replaces the binary
  segment test, with a temperature; `0` recovers the exact test
  ([occlusion](engine/occlusion.md)).
  *Accepts*: the gradient flows through a wall, and the position of an emitter
  near a corner changes continuously with the temperature.
- [ ] **3.2 Objectives.** Coverage, quantile, max-min, and a weighted sum of
  gain and cost ([objective](model/objective.md)).
  *Accepts*: each objective has a test on a hand-computed situation.
- [ ] **3.3 Emitter count.** A penalty that makes an emitter worth keeping, or
  a greedy addition with a stopping rule ([emitter-count](model/emitter-count.md)).
  *Accepts*: on the demo map the chosen count is stable across seeds.
- [ ] **3.4 Baselines.** k-center, k-median and greedy maximum coverage on the
  same grid ([baselines](model/baselines.md)).
  *Accepts*: the benchmark table shows our gain and theirs, per situation.
- [ ] **3.5 Physics.** Anisotropy, attenuation along the path, a noise floor
  ([physics](model/physics.md)).
  *Accepts*: a directional emitter is measurably better oriented towards its
  demand.
- [ ] **3.6 The piecewise-linear fast path.** The approximation of your
  Future Development, with its error measured ([piecewise-linear](model/piecewise-linear.md)).
  *Accepts*: a table error versus time, next to the exact run.
- [ ] **3.7 An implicit energy.** A `Domain` that returns a quasi-Monte Carlo
  sample and a continuous measure, a fixed seed across iterations, and a 3D
  case out of reach on a voxel grid ([implicit-energy](model/implicit-energy.md)).
  *Accepts*: the same seed gives the same answer, and the gain agrees with a
  fine grid on a case where the grid is affordable.

## Phase 4 — `dev/ui`: M4, a face

- [x] **4.1 A local page**, served by the same service, no build step, no CDN
  (2026-10-31, [zero-telemetry](architecture/zero-telemetry.md)).
- [x] **4.2 The page draws the state**, the map and the gain the service serves
  (2026-10-31); the DearPyGui window is deleted, never kept as a shim.

## Phase 5 — `dev/manifold`: the cases that justify the project

**[sketch]** After M3, and only if [open](open.md) says the direction is
worth it. Each step is a strategy behind the same gain, not a fork.

- [ ] **5.1 A `Domain` protocol.** `Plane` is the first implementation; the
  sum, the laws and the optimizer call it and nothing else
  ([manifolds](model/manifolds.md)).
  *Accepts*: the plane benchmark gives the same numbers as before.
- [ ] **5.2 A volume.** A 3D grid, a voxel density, 3D walls; a figure is a
  slice ([three-dimensional](model/three-dimensional.md)).
  *Accepts*: a 64³ situation runs in the benchmark, with its time.
- [ ] **5.3 A surface.** A mesh, a geodesic distance, emitters on vertices
  ([distance](engine/distance.md)).
  *Accepts*: the distance error is measured against a fine reference.
- [ ] **5.4 A periodic cell.** A lattice, a truncated or Ewald lattice sum
  ([crystals](model/crystals.md)).
  *Accepts*: the truncated sum converges to the resummed one as the range
  grows.
- [ ] **5.5 Constraints.** A rigid body, then torsions; a projection or a
  parameterization ([constraints](model/constraints.md)).
  *Accepts*: the gain is invariant to the choice of parameterization for
  the same physical position.
- [ ] **5.6 A pairwise term.** Repulsion or interference, `O(E²)`, with a
  cutoff ([circuits](model/circuits.md)).
  *Accepts*: two emitters pushed apart stay apart, and the gain matches a
  hand-computed case.
- [ ] **5.7 One real case.** A crystal question from the crystallography
  project, or a circuit layout, measured; the other stays a sketch.
  *Accepts*: a figure and a table a physicist or an engineer can read.

## Later

- Distance strategies: Euclidean, then geodesic on a chart
  ([distance](engine/distance.md)).
- Multi-start and global search on several seeds.
- A Typst report and a published benchmark.
