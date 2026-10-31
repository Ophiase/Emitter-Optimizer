# The emitter count

**[sketch]** Today the person types a number. The interesting question is how
many emitters the map deserves.

## Why it is hard

More emitters always raise the mean gain, so the count is unbounded unless a
cost enters. With a cost, the problem is a cardinality constraint, which is
not differentiable as such.

## Candidates

1. **Greedy addition**: start from zero, add the emitter that raises `G` the
   most, stop when the marginal gain falls below its cost. Simple, reliable,
   `1 - 1/e`-flavoured reasoning from maximum coverage
   ([baselines](baselines.md)).
2. **A sparsity penalty**: `- lambda * n` in the objective, with emitters free
   to merge; a merge is a continuous operation, a new emitter is not.
3. **Relaxation**: start from many emitters, let a penalty push them together
   and away from the map; count what survives above a threshold.

## [question]

Is the optimum stable across seeds? On a map of demand peaks it may collapse
to one emitter per peak, which is a good answer and a suspicious one. Measure
before claiming ([open](../open.md)).
