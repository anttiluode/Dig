# Dig — CURRENT HANDOFF

**Updated:** 2026-08-15  
**Status:** the romantic `state bends geometry` branch has been heavily narrowed. The strongest surviving object is a finite-horizon receiver-relative discrimination matrix.

## Read first

1. `MONOTONE_DISCRIMINATION_RECEIPT.md` — current endpoint: monotone pairwise discrimination, wait/readout frontier.
2. `SPACE_TIME_OBSERVABILITY_RECEIPT.md` — useful exploratory normalized-shape result plus the metric caveat that forced the monotone gate.
3. `RECEIVER_DIMENSION_CONTROL_RECEIPT.md` — kills the claim that soma is a uniquely collapsing one-dimensional receiver.
4. `OPERATING_STATE_Q2_RECEIPT.md` — -85 vs -65 mV on the same full-active Hay cell: near-isometric normalized source geometry.
5. `STATE_DEFORMATION_Q1_RECEIPT.md` — full active versus explicit dendritic-active-conductance ablation: modest deformation, source-neighbour topology preserved.
6. `RECEIVER_COLLAPSE_CELL1_Q0_RECEIPT.md` — initial soma vs six-port result; must be read together with the dimension control.
7. `EXACT_L5_BRIDGE.md` — exact `cell1.asc` provenance across FCI and Beniaguev/Hay code.
8. `MULTIPORT_NEURON.md` — earlier literature/idea collision; historical, not the current claim.

Cross-repo:

- `anttiluode/GeometricNeuronV23/HANDOFF_CURRENT.md`
- `anttiluode/GeometricNeuronV23/HANDOFF_RECEIVER_RELATIVE_Q0.md`
- `anttiluode/WidePresent/docs/RECEIVER_OBSERVABILITY_MATURITY.md`

---

# What was being tested

The working sentence entering this pass was:

> **Different morphologies support different modes. Different local states deform those modes. Different receivers see different subsets of them. Computation may consist partly in controlling that deformation.**

The point of today's work was to try to kill it rather than decorate it.

That largely succeeded.

---

# 1. Exact local temporal-state ↔ exact dendritic-address binding: still null

The GeometricNeuronV23 passive and balanced address × STP gates were already null.

The new local smooth regenerative nonlinearity did make the toy task dramatically easier, but strict post-training reassignment of learned STP tuples among their addresses still did not matter:

```text
tree nonlinear
joint baseline loss        0.00087783398
shuffle mean loss          0.00087751875
shuffle loss ratio         0.9996408992
baseline/shuffle accuracy  1.0 / 1.0
```

Verdict remains:

> **No evidence in these synthetic regimes that the identity of a learned temporal synapse state must stay attached to its exact dendritic segment.**

Do not tune thresholds/beta/tasks to manufacture that effect.

---

# 2. Receiver-relative transfer structure exists, but the soma is not special

Q0 on the exact FCI Hay `cell1.asc` initially found:

```text
normalized entropy effective rank

soma only                     3.8384
soma + 5 dendritic ports      8.5159
```

A leave-one-port-out jackknife showed no single dendritic receiver carried the six-port effect.

However the equal-dimensional kill control then showed:

```text
soma one-channel entropy rank       3.8384
random 1-D projection median        4.0118
soma percentile in random 1-D       36.9%
```

Only one of five individual dendritic ports had higher one-channel rank than the soma.

Therefore:

```text
soma is a uniquely destructive projection        NOT SUPPORTED
more distributed output dimensions preserve
more of the source-transfer dictionary            SUPPORTED / ORDINARY
```

The dimension curve further showed random mixed low-dimensional readouts outperform physical coordinate subsets of the same dimension in this fixed six-port set.

That belongs to observability / projection / sensor-compression territory, not special dendritic mysticism.

---

# 3. The strong small-signal state-deformation story mostly died

Using byte-identical Hay `cell1.asc` in the public Beniaguev model:

## Q1 — remove released dendritic active conductances

Six-port normalized source-distance geometry:

```text
Pearson ACTIVE vs ABLATED       0.99557
Spearman                        0.99160
nearest-neighbour changes       0 / 16
entropy rank                    7.969 -> 7.531
```

## Q2 — same full-active cell, -85 vs -65 mV somatic operating state

The distributed receiver voltages changed substantially and nonuniformly, but source geometry barely moved:

```text
Pearson DEPOL vs HYPER          0.999742
Spearman                        0.999062
relative Frobenius              0.0199
nearest-neighbour changes       0 / 16
```

So do **not** write:

```text
state dynamically rewires/bends the dendrite's small-signal source geometry
```

from these tests.

A fair statement is:

```text
active/state changes alter gains and metric details,
but the tested source-neighbour topology is extremely stable.
```

---

# 4. The normalized space-time rank experiment was useful but not the final metric

A fixed-horizon sweep showed:

```text
six-port normalized entropy rank
0.5 ms   8.38
1 ms     9.38
2 ms     9.77
...
120 ms   8.52
```

and early source-neighbour relationships appeared before most aggregate response energy had arrived.

But the rank was non-monotone because source rows were L2-normalized and late shared response could align them.

That is not literal observability capacity: retaining more samples cannot erase earlier evidence an ideal decoder could ignore.

Therefore `normalized entropy rank` is now an exploratory shape descriptor only.

Do not use it as the primary evidence-accumulation metric.

---

# 5. Current strongest object: finite-horizon discrimination matrix

The replacement gate used:

```text
D_C,T^2(i,j)
    = integral_0^T || h_i(t) - h_j(t) ||^2 dt
```

for candidate source responses `h_i,h_j` under readout `C`.

Properties earned by construction / guard:

```text
receiver-relative          YES
horizon-dependent          YES
pair-specific              YES
monotone in T              YES
threshold-free             YES
```

Hard monotonicity guard over all physical/random readouts and all 120 source pairs:

```text
minimum increment = +8.64e-24 mV^2 ms
```

Six-dimensional orthonormal readout invariance:

```text
max relative error = 2.61e-12
```

Both pass.

---

# 6. Pairwise discrimination maturity is not aggregate signal arrival

At six ports, earlier response-energy analysis said:

```text
10 ms   98.23% of aggregate response energy arrived
20 ms   99.47%
```

But pair-specific discrimination maturity was:

```text
10 ms
    median pair maturity            94.45%
    10th-percentile pair maturity   50.43%
    pairs >=90% mature              53.3%

20 ms
    median pair maturity            99.70%
    10th-percentile pair maturity   80.39%
    pairs >=90% mature              80.0%
```

So almost all aggregate response energy can be present while some candidate causes remain much less separated than they eventually become.

This is the cleanest numerical result of the pass.

The object should therefore **not** be one scalar:

```text
maturity(event)
```

but something like:

```text
D_C,T[i,j]
```

or within-readout maturity:

```text
M_C,T[i,j]
    = D_C,T^2(i,j) / D_C,120^2(i,j).
```

That is an ordinary finite-horizon geometry over alternatives, not a new time dimension.

---

# 7. WAIT versus ROUTE is now cleanly separated

Using 128 fixed random orthonormal readouts per output dimension `k=1..6`:

At 120 ms, median pairwise discrimination energy as a fraction of the physical six-port 120 ms reference saturated around:

```text
k=1     12.8%
k=2     29.7%
k=3     45.9%
k=4     64.4%
k=5     88.7%
k=6    100.0%
```

Therefore:

```text
WAIT
    increase T under current C
    -> D_C,T only grows
    -> cannot exceed the asymptotic ceiling of that readout

ROUTE
    change C
    -> changes what output subspace is observed
    -> can change / raise the attainable discrimination ceiling
```

This is the most useful current bridge to PivotPoint.

Example frozen frontier:

```text
k=1 reaches 10% of six-port reference at 20 ms
    never reaches 25%

k=2 reaches 25% at 40 ms
    never reaches 50%

k=4 reaches 50% at 20 ms
    never reaches 75%

k=6 reaches 50% at 10 ms
    75% at 20 ms
    90% at 40 ms
```

So waiting and readout width are partially substitutable, but not fully.

This is standard observability/sensor-bandwidth logic measured on the fixed medium.

---

# 8. Updated project synthesis

The original sentence should now be rewritten as:

> **A distributed dynamical medium induces receiver- and horizon-dependent distinguishability between possible causes. Waiting can accumulate evidence under a fixed readout; changing the readout can expose distinctions that waiting alone cannot recover.**

That sentence is much less romantic and much better supported.

The following earlier clauses are demoted:

```text
state strongly deforms the small-signal geometry      weak / near-null here
soma uniquely collapses morphology                    killed by equal-dim control
exact STP state binds to exact segment                 null in tested gates
computation = controlling geometric deformation       not earned
```

What remains interesting:

```text
finite-horizon discrimination under a readout
pair-specific evidence maturity
readout ceilings
wait versus route/probe/act decisions
```

---

# 9. Relation to existing repos

## WidePresent

`docs/RECEIVER_OBSERVABILITY_MATURITY.md` now separates:

```text
event/world age
transport frontier
aggregate response arrival
receiver-relative discrimination matrix
```

Do not add the last item to the runtime until an agent benchmark actually needs it.

## PivotPoint

The clean systems mapping is:

```text
WAIT      -> increase T
ROUTE     -> change C
PROBE     -> inject discriminating input
ACT       -> change controlled state/world
MODULATE  -> potentially change internal dynamics A
```

Only some interventions change `A`. Stop calling every action geometry deformation.

## GeometricNeuronV23

The strict exact-address × temporal-state nulls remain null.

If a future biological address test is attempted, the relevant address coordinate should be defined independently through measured receiver-visible transfer/discrimination, not post-hoc task performance.

---

# 10. Next fork

Do **not** immediately build another neuron.

The next useful question is no longer biological morphology by default.

Take the abstract object:

```text
D_C,T(i,j)
```

and ask where it buys something operational.

### Fork A — PivotPoint decision gate

Construct the smallest deterministic toy where a task supplies:

```text
required discrimination threshold
deadline
current readout C
estimated discrimination-growth curve D_C,T
available alternative routes/readouts C'
```

Then compare actions:

```text
WAIT
ROUTE
PROBE
ACT
```

The decisive case is where waiting under current `C` provably cannot reach the task threshold before the deadline / ever, while another route can.

**Baseline first:** deterministic resolver. If it solves the task, do not pretend an LLM architecture is required.

### Fork B — literature collision

Before implementing A as a project claim, collide the exact decision problem with:

```text
active sensing
sensor scheduling
POMDP information gathering
sequential probability ratio tests
optimal stopping
observability-aware control
```

The math is almost certainly occupied. The only possible value may be the way the existing project family uses the same measurement object.

### Fork C — biological nonlinear event

Only if returning to dendrites for a clearly separate reason, use a newly preregistered NMDA/active-event gate. Do not call it a continuation of Q1/Q2.

---

## Current one-line state

> **Today's kill gates mostly removed the glamorous geometry story. The sturdy object left behind is `D_C,T`: a receiver-relative finite-horizon discrimination matrix. Waiting grows it within a fixed readout ceiling; routing changes the ceiling. Now test whether that distinction solves an actual decision problem before building more machinery.**
