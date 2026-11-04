# Sphere: the regular solids, found by nothing but a gain

On a uniform sphere the emitters settle into a tetrahedron, an octahedron and an
icosahedron. **Nothing in the code knows a polyhedron**, and here the right
answer is known.

<p align="center">
  <img src="../figures/sphere_polyhedra.png" alt="Four, six and twelve emitters on a sphere" width="95%">
</p>

## Why it is here

```mermaid
graph TD
    subgraph gain[The gain]
        square[Quadratic sensor] --> pairs[A pair energy]
    end
    subgraph known[The known answer]
        optimal[Universally optimal sets] --> solids[Regular solids]
    end
    subgraph check[The check]
        angle[Smallest angle] --> tenth[Within a tenth of a degree]
    end
    pairs --> optimal
    solids --> angle
    class square,pairs engine
    class optimal,solids data
    classDef data fill:#2e7d32,stroke:#1b5e20,color:#ffffff
    classDef engine fill:#2a6db5,stroke:#1d4d80,color:#ffffff
    classDef trap fill:#c8553d,stroke:#8f3a28,color:#ffffff
```

- **Why it matters**: this is the one case with an exact answer to check the
  engine against ([the proof sketch](../../ideas/model/sphere.md)).
- **Expected angles**: 109.47°, 90.00° and 63.43°.

## Limits

- The grid discretizes the integral, so the angles hold within a tolerance.
- Another sensor law breaks the pair energy, and the answer is no longer known.

## Run it

```sh
just space thomson
```

[All the cases](README.md) · [Local minima](../local-minima.md)
