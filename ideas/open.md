# Open questions

## For the author

1. **[question] When does the window give way to one page?** The direction and
   the criteria are in [faces](architecture/faces.md).
2. **[question] How are user functions loaded?** Today `exec` on a Python file
   ([functions](engine/functions.md)); a plugin contract, or a restricted
   expression language, or both.
3. **[question] Which baselines deserve the benchmark?** k-center, k-median,
   greedy maximum coverage, or a facility-location solver from `scipy`.
4. **[question] Is a paper the goal, or a tool?** It changes how much of
   [model/](model/README.md) is measured versus shipped.
5. **[question] Is the 3D, manifold and constraint path worth it?** It is
   the only direction that makes the project different from a coverage demo
   ([manifolds](model/manifolds.md), [constraints](model/constraints.md)); it
   is also the most expensive.
6. **[question] What comes after the synthetic density?** [urea](model/urea.md)
   maximizes the overlap with a density; a measured map is the honest next step.
7. **[question] Is the circuit case the same project?** A pairwise term and
   complex phases make a different model ([circuits](model/circuits.md)).
8. **[question] Python or a Rust kernel?** The arguments and the triggers
   are in [language](architecture/language.md); none is true today.
9. **[question] Which implicit field first?** A Gaussian mixture, a
   coordinate network, or a signed distance field ([implicit-energy](model/implicit-energy.md)).
10. **[question] How many samples?** The benchmark has to pick the count
    where the Monte Carlo error is below the improvement being measured.

## Technical

1. **[to check]** When does a NumPy gain become too slow: 64×64, 256×256, a
   thousand emitters? The benchmark should answer with a number.
2. **[to check]** Is `scipy.optimize.minimize` with bounds enough, or does a
   hand-written projected step give a better gain per second?
3. **[to check]** Does a free-threaded Python 3.14 help, given NumPy releases
   the GIL?
4. **[question]** How is the initial placement drawn: uniformly, from the
   density, or from a k-means seeding?
5. **[question]** What is the unit of `epsilon` now: a learning rate, a step
   in map units, or both with a switch?
6. **[to check]** Does the density need interpolation between cells, or is the
   nearest cell enough at 32×32?
7. **[to check]** Which library for a mesh geodesic: heat method, exact
   polyhedral, or a chart the user provides?
8. **[to check]** Ewald summation against a truncated lattice sum: at which
   range do they agree, and at what cost?
9. **[to check]** Where does a 3D density come from: a voxel image, a point
   cloud, a mesh with a per-vertex weight?
10. **[to check]** Does `jax.jit` beat NumPy on the 3D gain, and at which
   sample count ([autodiff](engine/autodiff.md))?

## Scientific

1. **[guess]** Soft occlusion makes the landscape smoother but may create
   spurious minima at the temperature's scale; measure.
2. **[guess]** A max-min objective gives more evenly spread emitters and a
   lower mean; the trade-off is worth a curve.
3. **[question]** Does the emitter count have a stable optimum, or does it
   always collapse to one emitter per demand peak?
4. **[guess]** The piecewise-linear path is faster and close enough for maps
   above a size to determine ([piecewise-linear](model/piecewise-linear.md)).
