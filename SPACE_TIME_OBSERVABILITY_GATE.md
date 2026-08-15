# Space–time observability frontier on fixed `cell1.asc`

**Status:** preregistered measurement / synthesis test. **Not a novelty claim.**  
**Date:** 2026-08-15.

## Why this exists

The executed Dig/V23 sequence has now removed several stronger stories:

```text
exact learned STP tuple <-> exact dendritic segment     null
smooth local threshold rescue                           null
full active vs dendritic-active ablation at rest        near-isometry
-85 vs -65 mV full-active operating state              near-isometry
soma as uniquely collapsing one-channel receiver        not supported
```

One mundane but robust fact remains:

```text
more distributed output dimensions preserve more of the source-response dictionary.
```

That fact is standard measurement theory, not a discovery.

But it reconnects cleanly to an old recurring project idea:

```text
slider / Takens toys:
    trade recent time history for coordinates

Q0 / receiver controls:
    trade receiver coordinates for source distinguishability
```

The right mathematical language is finite-horizon observability.

For a local linearization

```text
xdot = A x + B u
y    = C x
```

and a finite observation horizon `T`, the observability Gramian is

```text
W_o(C,T) = integral_0^T exp(A^T t) C^T C exp(A t) dt.
```

For two source directions `b_i,b_j`, their output-energy separation is

```text
d^2_{C,T}(i,j)
    = (b_i-b_j)^T W_o(C,T) (b_i-b_j).
```

So **receiver projection `C` and retained time `T` jointly induce a distinguishability geometry on possible causes.**

This is established control theory. Sensor placement and empirical observability Gramian methods already optimize related quantities.

The only purpose of this gate is to measure that object on the exact impulse tensor already used in Dig and see whether it gives a useful common coordinate for `GeometricNeuron`, `PresentMoment`, `WidePresent`, and the old temporal visualizers.

---

# Frozen biological data generation

Pin exactly:

```text
ido4848/FCI
commit 55826436751c03a32dfd39e91a48894869e1db57
```

Use the exact Q0 protocol:

```text
Rat_L5b_PC_2_Hay_passive_dends_simple_soma / cell1.asc
16 source sites
6 receiver sites
0.02 nA source IClamp
0.5 ms duration
20 ms delay
140 ms tstop
0.05 ms dt
-70 mV initialization
matched no-stimulus subtraction
```

Let

```text
A[source, receiver, time]
```

be the matched-subtracted post-source response tensor.

No biological parameter changes in this gate.

---

# Frozen temporal horizons

Measure cumulative signatures from source onset through:

```text
T =
0.5,
1,
2,
5,
10,
20,
40,
80,
120 ms
```

Each shorter horizon is a literal prefix of the exact same trajectory.

No sliding or cherry-picked window is permitted.

---

# Part A — physical soma versus all six ports

For each horizon `T`, form:

```text
S_soma(i,T)  = soma response prefix for source i
S_6(i,T)     = flattened six-receiver response prefix for source i
```

As in previous Dig gates, compute the shape geometry after L2-normalizing each source row:

```text
entropy effective rank
participation rank
median pairwise cosine distance
median nearest-neighbour cosine distance
```

Also compute unnormalized cumulative response energy:

```text
E(T) / E(120 ms)
```

so an apparent early shape distinction can be seen alongside how much actual signal energy has arrived.

---

# Part B — geometric maturation

For each receiver condition independently, let the 120 ms normalized cosine-distance matrix be the final reference:

```text
D_final.
```

For each shorter `T`, compute:

```text
Pearson corr(upper(D_T), upper(D_final))
Spearman corr(upper(D_T), upper(D_final))
nearest-neighbour agreement with D_final
relative Frobenius distance to D_final
```

This asks:

> how quickly does the observer's eventual source geometry become available?

Report the first preregistered horizon, if any, at which:

```text
Pearson >= 0.90
Pearson >= 0.99
nearest-neighbour agreement >= 0.75
nearest-neighbour agreement == 1.0
```

These thresholds are reporting landmarks only, not success criteria.

---

# Part C — space–time frontier under an output-dimension budget

For each output dimension

```text
k = 1,2,3,4,5,6
```

and each temporal horizon above, use fixed-seed random orthonormal projections from the six physical receiver channels into `k` output channels.

Seed:

```text
20260817
```

Number of projections per `(k,T)`:

```text
128
```

The same projection matrices for a given `k` must be reused at **all** horizons, so temporal curves are not contaminated by changing readouts.

For each `(k,T)`, report the distribution of:

```text
entropy effective rank
participation rank
median pairwise cosine distance
```

The primary visualization/table is the median entropy-rank grid:

```text
rows    = temporal horizon T
columns = retained output dimension k
```

No optimization over random projections is used as the headline result; report medians and fixed quantiles.

At `k=6`, orthonormal receiver mixing must preserve the six-port geometry at each horizon to numerical precision. Treat failure as a harness error.

---

# Interpretation

## S-A — genuine space/time trade

If a lower-dimensional readout observed for longer reaches similar source-signature rank / mature geometry to a higher-dimensional readout observed briefly, then the experiment earns the modest sentence:

> **spatial receiver width and temporal observation width are partly substitutable resources for source observability in this fixed dynamical medium.**

That is not a new theorem. It is a measured property of this system and a clean bridge to the old `slider` / WidePresent intuition.

## S-B — spatial information not recoverable from more time

If low-`k` curves saturate far below high-`k` curves even at 120 ms, then extra temporal width cannot recover distinctions destroyed by projection.

This would be equally useful:

> **some source distinctions are lost under scalar/low-dimensional projection, not merely delayed.**

## S-C — only trivial energy arrival

If geometry maturation simply tracks cumulative response energy with no meaningful difference between soma and multiport views, then do not promote `causal maturity` language. Call it ordinary signal arrival.

---

# Relation to PresentMoment / WidePresent

Only after the numerical result, and only as a project-level synthesis:

```text
world age
    how long ago source event occurred

transport age
    how much of its consequence has reached the receiver

observability maturity
    how much of the final source-distinguishing output geometry is available
```

These are not new physical times.

The last quantity is explicitly receiver- and horizon-dependent and is standard finite-horizon observability in spirit.

If the experiment is useful, this gives `PresentMoment` a measurable version of "partial causal maturity" without inventing a master present-width parameter.

---

# Prior-art boundary

Do not claim invention of:

```text
finite-horizon observability
observability Gramians
empirical observability Gramians
sensor placement
random projections
space/time sampling tradeoffs
```

Relevant established lines include observability-Gramian sensor placement and empirical Gramian methods for nonlinear/PDE systems.

The project contribution, if any, is only the **common measurement lens across our existing artifacts**.

## One-line preregistration

> **Freeze the exact Q0 neuron and impulse tensor; vary only how many receiver dimensions are retained and how much post-event time is allowed to accumulate, then measure the finite-horizon source geometry without fitting either axis.**
