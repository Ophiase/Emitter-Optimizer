---
name: place-emitters
description: Place emitters on a map with Emitter Optimizer, through its local service, and report the gain with a figure.
---

# Place emitters

## When

A person asks where to put antennas, drippers, shops, sensors or any emitter
that covers a map and loses reach with distance, and wants a placement, a gain
and a picture.

## Start the service

Run this in a background shell; it prints `http://127.0.0.1:8765`.

```sh
just agent::serve --density resources/map/value_001.png \
    --collisions resources/map/collide_001.png --emitters 15 --seed 0
```

`EMITTER_URL` overrides the address. Nothing leaves the machine.

## Work

```sh
just agent::state              # positions, gain, history, seed
just agent::place 12 0         # draw twelve emitters from seed 0
just agent::run 200 0          # climb for two hundred iterations from seed 0
just agent::figure out/plan.png
just agent::export out/plan.json
```

## Answer

Report the gain before and after, the seed, the number of emitters, and where
the figure is. A run is reproducible: the same seed and the same parameters
give the same positions.

Never answer "done" without the numbers. If the service refuses (a 4xx), read
the `error` field, fix the argument, and try again. If a run is long, call
`just agent::stop` rather than killing the shell.
