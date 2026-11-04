# Building: concrete absorbs, it does not block

Six access points across three storeys, where walls and floors absorb the signal
along each sight line. **Here the descent beats greedy clearly**: greedy only
has a coarse lattice of candidates, and the descent has none.

<p align="center">
  <img src="../figures/case_building.gif" alt="Six access points moving across three storeys" width="70%">
</p>

## Why it is here

```mermaid
graph TD
    subgraph volume[The volume]
        voxels[Voxel grid] --> absorption[Absorption field]
    end
    subgraph signal[The signal]
        line[Along each sight line] --> decay[Exponential decay]
    end
    subgraph answer[The answer]
        free[Free 3D positions] --> storeys[Any height]
    end
    absorption --> line
    decay --> free
    class voxels,absorption data
    class line,decay engine
    classDef data fill:#2e7d32,stroke:#1b5e20,color:#ffffff
    classDef engine fill:#2a6db5,stroke:#1d4d80,color:#ffffff
    classDef trap fill:#c8553d,stroke:#8f3a28,color:#ffffff
```

- **Law**: $\varphi(d) = 1 / (1 + (d/4)^2)$, times $e^{-\int \alpha}$ along the
  line.
- **Gain**: 0.1173, against 0.1109 for greedy and 0.0664 at random.

## Limits

- The building is invented: offices along a corridor, no window.
- Absorption values are illustrative, not measured materials.

## Run it

```sh
just space building
```

[All the cases](README.md) · [Local minima](../local-minima.md)
