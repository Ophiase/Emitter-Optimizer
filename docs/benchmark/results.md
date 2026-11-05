# Benchmark

Every gain comes from the same scene, with sharp walls.

- **Random**: the mean of 32 placements drawn from the demand.
- **Greedy**: emitters added one by one on the grid.
- **Descent**: the better of 4 free starts and of a polish of greedy.
- **Relocation**: the same starts and greedy, each followed by
  [jumps](../local-minima.md) and a polish.
- **Spread**: how far the worst start ends below the best one.

What it says:

- **Greedy reaches most of the gain**; a relocation adds the rest.
- **A relocation makes the answer depend far less on the start.**
- A dot hides another when they tie.

`just bench` writes this page.

![The gain of each method above a random placement](methods.png)

![Each start, alone and relocated](starts.png)

| case | emitters | random | greedy | descent | relocation | spread alone | spread relocated | seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| garden | 24 | 0.0388 | 0.0611 | 0.0611 | 0.0622 | 5.9% | 0.9% | 443 |
| beach | 5 | 0.1174 | 0.1423 | 0.1424 | 0.1425 | 1.8% | 0.0% | 24 |
| marina | 8 | 0.2424 | 0.2752 | 0.2759 | 0.2781 | 2.5% | 0.1% | 26 |
| harbor | 14 | 0.1572 | 0.2202 | 0.2237 | 0.2252 | 3.5% | 0.8% | 34 |
| ramparts | 4 | 0.3403 | 0.3567 | 0.3573 | 0.3580 | 0.1% | 0.0% | 21 |

## Reproducibility

- **The gains of a relocation** reproduced to four decimals on a second machine.
- **The spread of the free starts did not**: beach went from 1.8% to 0.1%, marina
  from 2.5% to 4.3%, with the same seed. Read that column as an order of magnitude.
- **Twice on one machine**, beach gave the same numbers, so a seed repeats there.
- **The seconds** depend on the machine and on what else it runs.
