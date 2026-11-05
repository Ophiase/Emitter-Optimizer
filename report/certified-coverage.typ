#let paper = rgb("#fbfaf6")
#let ink = rgb("#23242a")
#let muted = rgb("#6b6f7a")
#let accent = rgb("#2a6db5")
#let data = json("data/certified.json")

#set document(title: "A proved optimum for coverage with walls", author: "ophiase")
#set page(paper: "a4", margin: (x: 2.3cm, y: 2.4cm), fill: paper, numbering: "1")
#set text(size: 10.5pt, fill: ink)
#set par(justify: true)
#set heading(numbering: "1.1")
#show link: set text(fill: accent)
#show table: set par(justify: false)
#set table(stroke: 0.4pt + muted, inset: 5pt)

#let data-table(block, columns) = table(
  columns: columns,
  table.header(..block.header.map(cell => [*#cell*])),
  ..block.rows.flatten(),
)

#v(1.6cm)
#align(center)[
  #text(size: 24pt, weight: "bold")[A proved optimum for coverage with walls] \
  #v(6pt)
  #text(size: 12pt)[Emitter Optimizer, and how far its answers are from the best] \
  #v(6pt)
  #text(fill: muted)[ophiase, with an agent --- working notes --- November 2026]
]

#v(0.8cm)
#block(inset: (x: 0.8cm))[
  #set text(size: 10pt)
  *Abstract.* Where should $k$ emitters stand so that their disks cover the most
  weight, when walls block the line of sight? Solvers for this maximal covering
  problem pick among sites given in advance, and the work we read on continuous
  space with obstacles is heuristic. We extend Church's finite set to walls, solve
  the result exactly, and compare it with a separate scoring: on #data.proved of
  #data.total random instances the bounds meet. The gaps then become measurable:
  sites restricted to the demand points lose #data.demand_mean on average and up to
  #data.demand_worst. Our own gradient engine ends #data.engine_mean below the
  optimum, behind an exact solver on a fine grid, and we say so.
]

#v(0.6cm)
#block(width: 100%, inset: 10pt, radius: 4pt, stroke: 0.8pt + accent)[
  *Three lines.* (1) With walls and disks, a finite set of positions holds an
  optimum. (2) So any plan can be graded against a bound, not against another
  heuristic. (3) Graded this way, the discrete habit is costly, and for this
  problem a gradient is not the right tool.
]

= The problem

An instance has points $x_i$ with integer weights $w_i$, a radius $R$, disjoint
wall segments, and $k$ emitters in a rectangle. A point is covered when an emitter
lies within $R$ and no wall properly crosses their sight line. The score is the
covered weight.

Let $V_i$ be the region where an emitter covers $x_i$: the disk of radius $R$
around $x_i$, minus the shadows of the walls. It is closed and star-shaped around
$x_i$.

= A finite set is enough

*Theorem.* Let $D$ hold the points $x_i$, the wall ends, and all crossings between
the circles, the walls, the map edges and the shadow edges, each crossing lying on
a wall being taken once per side. Some optimal placement lies in $D$.

*Proof.* Take an optimal emitter $y$ and the set $S$ of points it covers, and let
$C$ be the connected component of $y$ in the intersection of the $V_i$, $i in S$.
The complement of each star-shaped $V_i$ is connected and unbounded, so $C$ has no
hole. Its boundary is made of arcs and segments of the curves above.

If that boundary has a corner, the corner is a crossing or a curve end, it lies in
$D$, and an emitter there still covers $S$. If it has none, it is a single full
circle, so $C$ is a disk around some $x_j$, and $x_j in D$ covers $S$. A point on a
wall is reached from one side only, which is why it is counted per side. Each
emitter is treated in turn, and the covered set never shrinks. $square$

Without walls this is Church's circle intersection result, as cited by Blanco and
Gázquez. *This proof is on paper, by the agent, and has not been reviewed*; the
attacks of @sec-trust test it and do not replace it.

= How the bounds meet

The solver lists $D$, computes who each position covers with a slack of $10^(-6)$,
removes dominated positions, and solves the integer program with HiGHS. The dual
bound is the *upper* bound, valid for any placement. The chosen placement is then
scored with a slack of $10^(-9)$, like anyone's, which gives the *lower* bound. The
proof of an instance is that the two are equal; it is measured, never assumed.

= Results

== The reference set

#data.total random instances: 100 to 400 points, half clustered; 3 to 20 emitters;
0 to 12 walls; 5 seeds each. Gap: $("optimum" - "covered") \/ "optimum"$.

#data-table(data.methods, (2.2fr, 1fr, 1fr, 1fr, 1fr, 1.2fr))

#figure(
  image("/docs/benchmark/certified.png", width: 100%),
  caption: [The same instance. Left: the best placement on the demand points.
    Right: the proved optimum. Green is covered, red is not.],
)

*What it says.* A grid must reach 64 by 64 to beat the engine. Against the optimum
the engine is a middling heuristic here: it needs a blurred law to have a gradient
at all, and takes longer than the proof on these sizes.

== Effect of the walls

#data-table(data.walls, (1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1.2fr))

== The published maps, as disks

Each map keeps its density and walls; its law is reduced to the disk one emitter
serves alone. These are not the laws of the main benchmark, so the two do not
compare.

#[
  #set text(size: 8.5pt)
  #data-table(data.cases, (1.2fr, 0.9fr, 0.8fr, 1.1fr, 1fr, 1.2fr, 1fr, 1fr, 1fr, 1.2fr))
]

== Scale

#data-table(data.scale, (1fr, 1fr, 1fr, 1.2fr, 1fr, 1.2fr, 1fr))

A run at 3200 points, 40 emitters and 12 walls did not finish: it was stopped by
hand after 22 minutes, before the integer program. The time limit binds the integer
program only, not the listing before it.

= What is trusted, and how much <sec-trust>

#table(
  columns: (2fr, 1fr, 2.4fr),
  table.header([*Claim*], [*Trust*], [*Evidence*]),
  [A finite set suffices], [Paper, unreviewed], [The proof above],
  [Equal bounds on the set], [Measured], [`just certify`, by comparison],
  [No search passes a bound], [Tested], [Grid of 301 by 301, 24 instances; every
    method on all #data.total],
  [The set is not too small], [Partly tested], [Removing circle crossings,
    circle-segment crossings or shadows: caught; removing segment-segment crossings:
    *not caught*],
  [Same coverage as the kernel], [Tested], [Under 0.1% of pairs disagree],
  [Upper bound under rounding], [Numerical], [HiGHS tolerances; integer weights give
    a margin; not exact arithmetic],
  [Useful to practitioners], [*Inferred*], [A gap in the tools we read; nobody was
    asked],
)

= Limits

- *Disks only.* A soft law, or signals that add up, is outside the proof.
- *Synthetic.* Instances are random; maps are painted; no field measurement.
- *Prior art.* We found no tool doing this; that does not prove none exists.
- *Scale.* Candidates grow fast with points and radius; see the table above.

= Sources

- Blanco, Gázquez (2020), citing Church. #link("https://arxiv.org/abs/2005.03274")
- spopt, maximal covering. #link("https://pysal.org/spopt/notebooks/mclp.html")
- Line-of-sight coverage, IJGIS (2023), abstract read.
  #link("https://doi.org/10.1080/13658816.2023.2193829")
