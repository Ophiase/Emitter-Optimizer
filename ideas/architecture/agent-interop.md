# Agent interop

**[sketch]** The engine answers an agent the way it answers the window: over
localhost, in JSON, with a picture at the end.

## The contract

| Route | Effect |
| --- | --- |
| `GET /api/state` | map, density, obstacles, emitters, gain, history, seed |
| `POST /api/place` | replace the emitters, or draw them from the density |
| `POST /api/run` | run `n` iterations, with a seed; returns the gain curve |
| `POST /api/stop` | abort the running descent |
| `GET /api/figure.png` | the current value map and the emitters |
| `GET /api/export` | positions, history, parameters, as JSON and CSV |

## The recipes

`agent.just` imports the portable harness and wraps the routes:

```text
just agent::state | jq '.gain'
just agent::place '{"positions": [[10, 20], [40, 60]]}'
just agent::run 200 --seed 0
just agent::figure out.png
```

Every argument is passed positionally and validated, never spliced into a
shell string; the service binds `127.0.0.1` only.

## What a good answer contains

A gain, the seed that produced it, the number of emitters, the figure, and the
limits of the run. An agent that reports only "done" has not done the work.
