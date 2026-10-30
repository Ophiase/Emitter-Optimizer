# Roadmap

**[sketch]** The ordered steps, one branch each. It is written so that an
agent starting a new session can pick the first unchecked step, read the files
the step names, and work without asking. A step is done when `just agent gate`
passes **and** its acceptance sentence is true.

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

## Phase 1 — `dev/engine`: M1, a headless engine

- [ ] **1.1 Remove the GUI from the import path.** `emitter_optimizer.engine`
  imports no `gui`, no `dearpygui`. A test imports the engine in a process
  where `dearpygui` is absent.
  *Accepts*: `uv run python -c "import emitter_optimizer.engine"` works in an
  environment without DearPyGui.
- [ ] **1.2 Replace TensorFlow by NumPy.** The gain, its value map and the
  obstacle test are NumPy arrays; `Field` exposes `gain(positions)` and
  `value_map(positions)` with the same meaning ([gain](engine/gain.md)).
  *Accepts*: the eight current tests pass, with TensorFlow uninstalled.
- [ ] **1.3 Exact gradient for the built-in laws.** A leaf module computes
  `dG/dpositions`: `sum_x psi'(r) phi'(d) grad(d) mu(x) pass_C(x, y)`, the
  obstacle term constant between two crossings ([optimizer](engine/optimizer.md)).
  *Accepts*: it matches a central finite-difference on a random map within
  1e-4 relative error.
- [ ] **1.4 A numeric gradient for any callable.** When the user supplies
  their own `phi` or `psi`, fall back to central differences on the
  `2 * n_emitters` coordinates ([functions](engine/functions.md)).
  *Accepts*: the same test as 1.3, with the laws loaded from `settings/`.
- [ ] **1.5 An optimizer with bounds and restarts.** Projection on the map,
  `epsilon` as a step or a learning rate, `n_iteration`, `abort`, and the
  update callback the GUI already uses ([optimizer](engine/optimizer.md)).
  *Accepts*: the gain is non-decreasing on every benchmark situation.
- [ ] **1.6 A headless command.** `emitter-optimizer run --map ... --density
  ... --emitters 12 --seed 0 --iterations 200 --out out/` writes
  `positions.csv`, `history.csv` and `figure.png`, and prints a JSON summary.
  *Accepts*: a person reproduces the README figure with one command.
- [ ] **1.7 A benchmark.** `just bench` runs fixed situations (no map, a
  density, a density with walls, a non-square grid) and writes
  `docs/benchmark/results.md`, sorted, with timings.
  *Accepts*: the table is generated, never hand-edited, and a reader can rerun
  it.
- [ ] **1.8 Freeze DearPyGui.** Either the window calls the new engine
  unchanged, or `gui/` is marked legacy in `AGENTS.md` and not tested.
  *Accepts*: `just check` never imports `dearpygui`.

Dependencies: 1.2 before 1.3; 1.3 and 1.5 before 1.6; 1.6 before 1.7.

## Phase 2 — `dev/agent`: M2, agent-native

- [ ] **2.1 A local service.** `emitter-optimizer serve` binds `127.0.0.1` and
  exposes `GET /api/state`, `POST /api/run`, `POST /api/place`,
  `GET /api/figure.png`, `GET /api/export` ([agent-interop](architecture/agent-interop.md)).
  *Accepts*: `curl` on the state returns the map, the emitters and the gain.
- [ ] **2.2 `agent.just`.** `just agent::state`, `run`, `place`, `figure`,
  `export`, `stop`, following the portable harness; every argument passed
  positionally.
  *Accepts*: from a fresh shell, `just agent::run` then `just agent::figure
  0 out.png` produces a picture.
- [ ] **2.3 A skill.** `.claude/skills/place-emitters/SKILL.md`: when to use
  it, the recipes, what a good answer contains (gain, seed, figure, limits).
  *Accepts*: an agent with only the skill completes 1.6's task and reports the
  gain it reached.
- [ ] **2.4 Determinism.** Every random draw takes a seed; the same seed gives
  the same positions and the same gain.
  *Accepts*: two runs with the same seed are identical byte for byte.

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

## Phase 4 — `dev/ui`: M4, a face

- [ ] **4.1 A thin local page**, served by the same service, no build step,
  no CDN ([zero-telemetry](architecture/zero-telemetry.md)).
- [ ] **4.2 Or a reduced DearPyGui window** that only draws the state the
  service serves. Decide in [open.md](open.md) before writing it.

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
