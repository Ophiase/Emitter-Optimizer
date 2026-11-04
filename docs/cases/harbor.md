# Harbor: a quay is lit or it is not

Fourteen lamps along the quays and the car park of Skopelos, with the house
fronts casting the shadow. **A threshold law is the hardest shape to climb, and
the map shows it edge to edge.**

<p align="center">
  <img src="../figures/cases/harbor.webp" alt="Lamps moving over the photograph of the harbor case" width="85%">
</p>

*Blue demand is not served yet, yellow is. White lines are the descent, orange
lines the [jumps](../local-minima.md). One start, seed 0.*

## The decision

- **Who decides**: whoever fits out a ferry port.
- **The cost of a mistake**: a dark stretch of quay where a ramp comes down.

## What goes in

<p align="center">
  <img src="../../resources/cases/harbor/source.jpg" alt="The aerial photograph of the harbor case" width="45%">
  <img src="../figures/layers_harbor.jpg" alt="The painted layers: attraction in yellow, collision in red" width="45%">
</p>

*The photograph, then the two layers painted over it: attraction in yellow,
collision in red.*

## Why it is hard

```mermaid
graph TD
    subgraph law[The law]
        lit[Lit above a target] --> flat[Flat on both sides]
    end
    subgraph descent[The descent]
        none[Slope only at edges] --> stops[Stops early]
    end
    subgraph limit[The limit of a jump]
        two[Lamps act together] --> refused[Single jumps refused]
    end
    flat --> none
    stops --> two
    class lit,flat data
    class none,stops engine
    class two,refused trap
    classDef data fill:#2e7d32,stroke:#1b5e20,color:#ffffff
    classDef engine fill:#2a6db5,stroke:#1d4d80,color:#ffffff
    classDef trap fill:#c8553d,stroke:#8f3a28,color:#ffffff
```

- **Flat, steep, flat.** Fully lit and fully dark cells both have no slope, so
  only the edges of the light pull a lamp.
- **A dark quay may need two lamps at once**, which a single jump cannot try:
  the likely reason why one start finds no jump.

## The two laws

- **Emitter**: $\varphi(d) = (1 + (d/20)^2)^{-3/2}$ — the illuminance under a
  pole.
- **Sensor**: $\psi(s) = \sigma((s - 0.15)/0.03)$ — a quay is lit or not; more
  light adds nothing.

![The two laws of this case](../figures/cases/harbor_laws.png)

## What it found

| Emitters | Random | Greedy | Descent | Relocation | Spread alone | Spread relocated |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 14 | 0.1572 | 0.2202 | 0.2237 | **0.2252** | 3.5% | 0.8% |

- **+43% above random, +2.3% above greedy**: the widest margin over greedy of
  the five.
- **The start of this animation makes no jump at all**: the spread only falls to
  0.8%.

![The gain as emitters are added, with this case's count marked](../figures/cases/harbor_count.png)

**It flattens past 14**: the second half of the budget adds about 15%.

## Limits

- A pole's height and a lamp's power are folded into two constants.
- One start of four ends 0.8% below the best: see [local
  minima](../local-minima.md).

## Run it

```sh
just case harbor --relocate --iterations 300
```

[All the cases](README.md) · [Local minima](../local-minima.md) ·
[Benchmark](../benchmark/results.md)
