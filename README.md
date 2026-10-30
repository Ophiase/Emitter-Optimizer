# Emitter Optimizer 📡

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.14+](https://img.shields.io/badge/Python-3.14%2B-yellow.svg)](https://www.python.org/)
[![just](https://img.shields.io/badge/just-ready-blue.svg)](https://github.com/casey/just)
[![uv](https://img.shields.io/badge/uv-managed-blueviolet.svg)](https://github.com/astral-sh/uv)
[![The Kanon](https://img.shields.io/badge/%3C%3E-Kanon-6f42c1)](.agents/kanon.md)

**Where do I put my emitters?** Antennas on a building, drippers on a farm, a
shop that captures a neighbourhood, sensors in a room: anything that covers a
map around itself and loses reach with distance. Give the tool a map, a weight
per place, obstacles, and the law of your emitter; it returns the positions
that capture the most.

The model has been the same since 2023: a **differentiable gain**, climbed by
gradient descent, with the emitter law and the sensor law written by the user.
It is the baseline every newer model is compared against. The plan and the open
questions live in [ideas/](ideas/README.md).

## Who it is for

- **Field engineering**: irrigation, lighting, sensors, Wi-Fi, radio — a
  density of need, a budget of devices, walls in between.
- **Retail and logistics**: where a set of points captures the most demand.
- **Research and teaching**: a differentiable placement problem with arbitrary
  user functions, not a black box.
- **Agents**: the engine is headless and speaks JSON, so an assistant can
  propose a layout, weigh candidates and show a figure
  ([ideas/architecture/agent-interop.md](ideas/architecture/agent-interop.md)).

## Quick start

```sh
just install   # uv sync: Python 3.14 and the dependencies
just run       # open the window
```

Load `resources/map/value_001.png` as the density, optionally
`resources/map/collide_001.png` as the collision map, choose the number of
emitters, press **Process**. The window shows the value map, the emitters and
the gain curve; **Save** writes the positions.

`just` alone lists every recipe. `just lint`, `just test` and `just check` are
the local checks; `just agent gate` is the whole gate.

## The model

Maximize the gain $\mathcal G$ over the emitter positions $U$:

- Emitter law $\varphi : \mathbb{R}^+ \to \mathbb{R}$ — the signal received at
  a distance.
- Sensor law $\psi : \mathbb{R} \to \mathbb{R}$ — the score of a received sum.
- $U$: the positions of the emitters.
- Parameters $P := (E, \mu, C)$
  - $E$: the map.
  - $\mu$: a density measure over $E$.
  - $C$: segments that block the signal.
- $pass_C : (x, y) \to 1 - \prod_{s \in C} (1 - \mathbb{1}_{[x; y] \cap s})$ —
  $0$ if the segment $[x; y]$ meets $C$, $1$ otherwise.
- $dist : (x, y) \to ||x - y||_2$.
- Received signal
  $r_{U,C} : x \to \sum_{y \in U} \varphi(dist(x, y)) \cdot pass_C(x, y)$.
- Gain
  $\mathcal G_P : U \to \int_E \psi \circ r_{U,C}(x) \, d\mu(x)$.

The integral is a mean over the grid. $\mathcal G$ is differentiable in $U$
away from the walls, and the engine computes the exact gradient: a NumPy
sum over the cells, climbed by a projected Adam step that keeps every
emitter on the map. No deep-learning framework is involved.

## What you can change

- $\varphi$ and $\psi$: two Python files in `settings/`, editable in the
  window and plotted live.
- $\mu$: a density image, one weight per cell.
- $C$: a collision image (turned into segments) or a list of segments.
- The number of emitters, the map scale, the grid size, the step and the
  number of iterations.

## Demo

- ![Density map](https://raw.githubusercontent.com/Ophiase/Emitter-Optimizer/main/resources/map/value_001.png) — `resources/map/value_001.png`
- ![Collision map](https://raw.githubusercontent.com/Ophiase/Emitter-Optimizer/main/resources/map/collide_001.png) — `resources/map/collide_001.png`
  (the `.numpy` file is the same map, already segmented; solving without
  colliders is often enough).
- Before and after, with the gain curve:
  <img src="https://raw.githubusercontent.com/Ophiase/Emitter-Optimizer/main/resources/demo/render_000.png" height=150 alt="before">
  <img src="https://raw.githubusercontent.com/Ophiase/Emitter-Optimizer/main/resources/demo/render_199.png" height=150 alt="after">
  <img src="https://raw.githubusercontent.com/Ophiase/Emitter-Optimizer/main/resources/demo/loss.png" height=150 alt="gain curve">

## Status

The 2023 application, modernized in 2026: Python 3.14, uv, `just`, ruff, ty,
a NumPy engine with an exact gradient, ten property tests, one gate. The next
steps, in order, are in [ideas/roadmap.md](ideas/roadmap.md): a command line,
a benchmark, an agent protocol, a richer objective, then the 3D, manifold and
constrained cases.

## Credits

The project was started in 2023 by **Ophiase**, by hand, as a personal
project; the 2026 modernization (Kanon agent layer, uv, Python 3.14, tests) was
carried out with **Cline**, an AI coding agent. See
[CONTRIBUTORS.md](CONTRIBUTORS.md).

## License

Apache-2.0, see [LICENSE](LICENSE).
