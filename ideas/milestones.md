# Milestones

**[sketch]** Four milestones; the first three make the project useful, the
fourth makes it pleasant. Each is a branch and a small version.

## M1 — A headless engine in NumPy

No TensorFlow, no Keras, no GUI in the path. `emitter_optimizer.engine` takes a
map, a density, obstacles, two functions and initial positions, and returns
positions, a gain history and a figure; a command prints the same as JSON.
Done when:

- `just bench` runs a fixed set of situations and writes a table;
- the gain never decreases on the benchmark, and the gradient matches a
  finite-difference reference;
- the test suite runs without importing TensorFlow;
- the GUI is either adapted or frozen, never required.

See [gain](engine/gain.md), [optimizer](engine/optimizer.md),
[stack](architecture/stack.md).

## M2 — An agent can drive it

A local service exposes the engine: state, run, place, figure, export. An
`agent.just` wraps it, and a skill tells an agent how to use the recipes.
Done when an agent, with nothing but the skill, places emitters on the demo
map and produces a figure and a JSON report.

See [agent-interop](architecture/agent-interop.md).

## M3 — A model worth publishing

The objective is richer than a mean, the emitter count is chosen, and every
claim is compared to a baseline. Done when the report has a table per
situation: our gain, the baseline gain, the number of emitters, the time.

See [objective](model/objective.md),
[emitter-count](model/emitter-count.md), [baselines](model/baselines.md).

## M4 — A face that does not get in the way

A thin local page, or a reduced DearPyGui window, showing the map, the
emitters, the gain history and the proposals of an agent. Done when a person
understands the result in the first ten seconds.

## Order and cost

| Milestone | Branch | Rough cost |
| --- | --- | --- |
| M1 | `dev/engine` | a few days |
| M2 | `dev/agent` | a few days |
| M3 | `dev/model` | weeks |
| M4 | `dev/ui` | a few days, after M2 |
