# ideas/ — map

The core of the project: **one concept per file**, short, informal first. Code,
README and figures are written from here; a choice that is not here yet is not
made yet ([AGENTS.md](../AGENTS.md)).

Tags: **[defined]** (fixed by the author), **[sketch]** (argued, unchecked),
**[guess]**, **[to check]** (claim about prior art), **[question]** (the author
decides), **[caution]** (known trap).

## Thesis

Placing emitters on a map is a differentiable optimization problem that nobody
exposes as a reusable engine: teams rebuild it for radio planning, irrigation,
retail siting or sensor networks, each with its own ad hoc script. The project
is **one small, typed, fast Python core** that maximizes a gain the user
defines, under obstacles, weighted by a density — and that an **agent can
drive** as easily as a person.

## The path

```text
  origin.md ── the 2021 demo, what survives and what goes
      │
  vision.md ── for whom, what it promises, what it is not
      │
  architecture/ ── engine, service, ui; Python and NumPy as the stack
      │
  engine/ ──── the gain, the occlusion, the maps, the optimizer
      │
  model/ ───── the objective, the emitter count, the baselines
      │
  milestones.md ── M1 engine, M2 agent, M3 model, M4 ui
      │
  roadmap.md ───── the ordered steps, one branch each
      │
  open.md ──── the questions still open
```

## Files

- [vision.md](vision.md) · [origin.md](origin.md) ·
  [milestones.md](milestones.md) · [roadmap.md](roadmap.md) ·
  [open.md](open.md) · [prior-art.md](prior-art.md) ·
  [crossover.md](crossover.md)
- **architecture/**: [README](architecture/README.md) —
  [stack](architecture/stack.md) · [layers](architecture/layers.md) ·
  [agent-interop](architecture/agent-interop.md) ·
  [zero-telemetry](architecture/zero-telemetry.md) ·
  [language](architecture/language.md)
- **engine/**: [README](engine/README.md) —
  [gain](engine/gain.md) · [occlusion](engine/occlusion.md) ·
  [map](engine/map.md) · [distance](engine/distance.md) ·
  [functions](engine/functions.md) · [optimizer](engine/optimizer.md) ·
  [autodiff](engine/autodiff.md)
- **model/**: [README](model/README.md) —
  [objective](model/objective.md) ·
  [emitter-count](model/emitter-count.md) ·
  [baselines](model/baselines.md) ·
  [piecewise-linear](model/piecewise-linear.md) ·
  [physics](model/physics.md) ·
  [three-dimensional](model/three-dimensional.md) ·
  [manifolds](model/manifolds.md) ·
  [constraints](model/constraints.md) ·
  [crystals](model/crystals.md) ·
  [circuits](model/circuits.md) ·
  [implicit-energy](model/implicit-energy.md)

## Where the code stands (v2.1, 2026-10-31)

**[defined]** v2.1 is the modernization: NumPy with an exact gradient, a
projected Adam descent, a command line, a local service an agent drives, five
named use cases, generated figures and a benchmark. The window is one client
of the engine, not its only face. What remains is Phase 3 of the roadmap: a
richer objective, the emitter count, the baselines, then the 3D and the
manifolds.
