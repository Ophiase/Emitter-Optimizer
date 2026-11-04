# Globe: twelve stations for the world's cities

Twelve stations on the sphere, serving the 243 cities of Natural Earth weighted
by population. **Nothing in the engine changes: only the distance does.**

<p align="center">
  <img src="../figures/case_globe.gif" alt="Twelve stations on the rotating Earth" width="70%">
</p>

## Why it is here

```mermaid
graph TD
    subgraph data[The data]
        cities[243 cities] --> weight[Weighted by population]
    end
    subgraph space[The space]
        angle[Geodesic angle] --> project[Back on the sphere]
    end
    subgraph result[The result]
        stations[Twelve stations] --> crowds[Follow the crowds]
    end
    weight --> angle
    project --> stations
    class cities,weight data
    class angle,project engine
    classDef data fill:#2e7d32,stroke:#1b5e20,color:#ffffff
    classDef engine fill:#2a6db5,stroke:#1d4d80,color:#ffffff
    classDef trap fill:#c8553d,stroke:#8f3a28,color:#ffffff
```

- **Law**: $\varphi(\theta) = e^{30 (\cos \theta - 1)}$ over the geodesic angle,
  and $\psi(s) = 1 - e^{-s}$.
- **Gain**: 0.0102, against 0.0075 at random.

## Limits

- The density is a smoothed city list, not a measured demand.
- Orbits, ground stations and link budgets are not modelled.

## Run it

```sh
just space globe
```

[All the cases](README.md) · [Local minima](../local-minima.md)
