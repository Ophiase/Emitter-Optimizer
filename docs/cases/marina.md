# Marina: Wi-Fi over yachts and an old town

Eight access points over the harbour of Saint-Tropez, with the harbour-front
blocks between the boats and the streets. **Here the gradient always feels
something, and it still gets stuck.**

<p align="center">
  <img src="../figures/cases/marina.webp" alt="Access points moving over the photograph of the marina case" width="85%">
</p>

*Blue demand is not served yet, yellow is. White lines are the descent, orange
lines the [jumps](../local-minima.md). One start, seed 0.*

## The decision

- **Who decides**: whoever installs a harbour network.
- **The cost of a mistake**: full bars on the quay, nothing one street behind.

## What goes in

<p align="center">
  <img src="../../resources/cases/marina/source.jpg" alt="The aerial photograph of the marina case" width="45%">
  <img src="../figures/layers_marina.jpg" alt="The painted layers: attraction in yellow, collision in red" width="45%">
</p>

*The photograph, then the two layers painted over it: attraction in yellow,
collision in red.*

## Why it is hard

```mermaid
graph TD
    subgraph law[The law]
        never[Never reaches zero] --> slope[Slope everywhere]
    end
    subgraph blocks[The blocks]
        front[Harbour front] --> shadow[A hard shadow]
    end
    subgraph result[The result]
        crossing[Crossing loses signal] --> side[Stays on its side]
    end
    slope --> front
    shadow --> crossing
    class never,slope engine
    class front,shadow data
    class side trap
    classDef data fill:#2e7d32,stroke:#1b5e20,color:#ffffff
    classDef engine fill:#2a6db5,stroke:#1d4d80,color:#ffffff
    classDef trap fill:#c8553d,stroke:#8f3a28,color:#ffffff
```

- **A wall is a cliff in the gain.** Crossing it loses a whole shadow before it
  wins the other side, so an access point stays where it is.
- **Diminishing returns** make a second antenna on the crowd worth less, but
  rarely worth nothing.

## The two laws

- **Emitter**: $\varphi(d) = 1 / (1 + (d/20)^2)$ — an inverse square that never
  reaches zero.
- **Sensor**: $\psi(s) = \log(1 + s/N) / \log(1 + 1/N)$ — Shannon throughput,
  diminishing returns.

![The two laws of this case](../figures/cases/marina_laws.png)

## What it found

| Emitters | Random | Greedy | Descent | Relocation | Spread alone | Spread relocated |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 8 | 0.2424 | 0.2752 | 0.2759 | **0.2781** | 2.5% | 0.1% |

- **+15% above random, +1.1% above greedy.**
- **The spread falls to 0.1%**, from 2.5% here and 4.3% on a second machine
  ([reproducibility](../benchmark/results.md#reproducibility)), so the start no
  longer decides the answer.

![The gain as emitters are added, with this case's count marked](../figures/cases/marina_count.png)

**It keeps rising**: doubling to 16 access points adds about a quarter.

## Limits

- Walls block fully here; real concrete attenuates (see
  [building](building.md)).
- Interference between access points is not in the gain.

## Run it

```sh
just case marina --relocate --iterations 300
```

[All the cases](README.md) · [Local minima](../local-minima.md) ·
[Benchmark](../benchmark/results.md)
