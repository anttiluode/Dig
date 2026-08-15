# Space–time observability frontier — receipt

**Date:** 2026-08-15  
**Status:** executed preregistered measurement. **Useful synthesis result, not a novelty claim.**  
**Gate:** `SPACE_TIME_OBSERVABILITY_GATE.md`  
**Executable:** `space_time_observability_cell1.py`

## Provenance

Pinned public model:

```text
ido4848/FCI
commit 55826436751c03a32dfd39e91a48894869e1db57
```

Exact Q0 biology/probe:

```text
Rat_L5b_PC_2_Hay_passive_dends_simple_soma / cell1.asc
16 fixed source sites
6 fixed receivers
0.02 nA / 0.5 ms IClamp
matched no-stimulus subtraction
```

Temporal prefixes:

```text
0.5, 1, 2, 5, 10, 20, 40, 80, 120 ms
```

Random readout frontier:

```text
k = 1..6 retained output dimensions
128 fixed-seed random orthonormal projections per k
seed 20260817
same projection matrix reused at every time horizon
```

Valid GitHub Actions run:

```text
31888731090
```

Dig commit tested:

```text
f77029e2c1eb6ac62597322dca764b8621d959dd
```

A first run (`31888656501`) was rejected before analysis because fixed-step NEURON ended at source-relative 119.95 ms rather than recording the requested 120.00 ms endpoint. The workflow was changed only to integrate one extra `dt=0.05 ms` step while analysis still truncates at `<=120.00 ms`.

Six-dimensional orthonormal-remix invariance:

```text
max entropy-rank absolute error = 1.60e-14
preregistered guard < 1e-8      PASS
```

---

# Result 1 — geometry and response energy do not mature together

## Soma-only view

```text
T ms   entropy rank   energy fraction   Pearson to final   NN agreement

0.5       2.6033          0.0806             0.6728           0.375
1         3.1504          0.1793             0.8617           0.500
2         3.4656          0.3039             0.9059           0.625
5         3.7216          0.5386             0.9588           0.625
10        3.7202          0.7523             0.9775           0.8125
20        3.7264          0.9230             0.9919           0.9375
40        3.7880          0.9913             0.9992           1.000
80        3.8351          0.9999             ~1.000           1.000
120       3.8384          1.0000             1.0000           1.000
```

Landmarks:

```text
Pearson >= 0.90         2 ms
Pearson >= 0.99        20 ms
NN agreement >= 0.75  10 ms
all 16 NN identities   40 ms
```

At 2 ms only ~30% of eventual soma response energy has arrived, yet the pairwise source-distance matrix already correlates >0.90 with its 120 ms version.

## Six-port view

```text
T ms   entropy rank   energy fraction   Pearson to final   NN agreement

0.5       8.3812          0.2461             0.7435           0.875
1         9.3848          0.6350             0.8035           0.875
2         9.7676          0.8676             0.8747           0.875
5         9.3676          0.9622             0.9573           0.9375
10        8.9602          0.9823             0.9900           1.000
20        8.6409          0.9947             0.9987           1.000
40        8.5294          0.9995             ~1.000           1.000
80        8.5161          1.0000             ~1.000           1.000
120       8.5159          1.0000             1.0000           1.000
```

Landmarks:

```text
Pearson >= 0.90         5 ms
Pearson >= 0.99        10 ms
NN agreement >= 0.75   0.5 ms
all 16 NN identities   10 ms
```

The striking point is the 0.5 ms prefix:

```text
only 24.6% of eventual six-port response energy has arrived
but 14 / 16 source nearest-neighbour identities already match the 120 ms geometry
```

So `amount of signal arrived` and `how much of the eventual source relationship is already inferable` are not the same coordinate in this measurement.

This is the cleanest empirical bridge so far to the old PresentMoment phrase **partial causal maturity** — with an important caveat below.

---

# Result 2 — there is a space/time trade, but it is only partial

Median normalized entropy effective rank under the fixed random readout ensemble:

```text
T ms   k=1    k=2    k=3    k=4    k=5    k=6

0.5    2.282  4.061  5.432  6.637  7.608  8.381
1      2.770  4.847  6.392  7.684  8.654  9.385
2      3.282  5.546  7.118  8.332  9.173  9.768
5      3.570  5.834  7.259  8.315  8.908  9.368
10     3.747  5.946  7.099  8.042  8.559  8.960
20     3.844  6.031  7.055  7.850  8.276  8.641
40     4.008  6.087  7.054  7.784  8.178  8.529
80     4.087  6.110  7.051  7.776  8.167  8.516
120    4.090  6.111  7.050  7.776  8.167  8.516
```

A descriptive landmark frozen by the gate was the first horizon at which the median random readout reaches the physical soma's **final 120 ms entropy rank = 3.8384**:

```text
k=1    20 ms
k=2     0.5 ms
k=3     0.5 ms
k=4     0.5 ms
k=5     0.5 ms
k=6     0.5 ms
```

Thus additional receiver dimensions can substitute strongly for waiting **for this particular normalized-rank target**.

But the trade is not complete. At 120 ms:

```text
k=1 median rank   4.09
k=2               6.11
k=3               7.05
k=6               8.52
```

Waiting longer does not make a one- or two-dimensional projection recover the full six-dimensional source geometry.

So the measured statement is:

> **spatial output width and temporal observation width are partly substitutable, but projection can discard distinctions that additional waiting does not recover.**

This is a system-specific measurement, not a new control-theory theorem.

---

# Result 3 — the normalized shape rank is non-monotone

This is the most important methodological correction from the run.

For the six-port view:

```text
entropy rank
0.5 ms    8.38
1 ms      9.38
2 ms      9.77   <-- peak
5 ms      9.37
10 ms     8.96
20 ms     8.64
120 ms    8.52
```

For `k >= 3`, the random-projection median curves show the same general pattern: rank rises rapidly, peaks early, then declines toward a stable late value.

That does **not** mean literal finite-horizon observability is decreasing with more data.

The reason is our metric:

```text
append temporal samples
-> flatten source response
-> L2-normalize each source row
-> measure cosine geometry / entropy effective rank
```

Appending a large shared slow tail can make normalized source directions more aligned even though an optimal decoder still retains all earlier samples and could simply ignore the tail.

Therefore do **not** identify this normalized effective-rank curve with the observability Gramian itself.

The experiment is **observability-inspired source-shape geometry**, not a proof that physical information disappears as time passes.

This distinction matters enough that it should constrain the next experiment.

---

# Gate verdict

The preregistered branches were:

```text
S-A  genuine partial space/time trade
S-B  projection loses distinctions that waiting does not recover
S-C  geometry maturation is merely cumulative response-energy arrival
```

The result is a mixture of **S-A + S-B**, and rejects the simplest form of **S-C**.

- More temporal width helps low-dimensional readouts.
- More spatial/readout width can expose distinctions almost immediately that a one-dimensional readout needs tens of milliseconds to approach.
- Low-dimensional projections still saturate below the six-port source rank.
- Early source relationship can be predictive of the final relationship before most response energy has arrived.

But the non-monotone normalized-rank curve means the next rigorous step should use a **monotone finite-horizon discrimination quantity** rather than interpreting entropy rank as observability capacity.

---

# What this earns for WidePresent / PresentMoment

There is now a useful three-way distinction on one concrete dynamical system:

```text
WORLD AGE
    how long ago the source event occurred

TRANSPORT / RESPONSE ARRIVAL
    how much response energy has physically reached the observer

OBSERVATION MATURITY
    how much of the observer's eventual source-distinguishing relationship
    is already inferable from the response prefix
```

The last item is **receiver-relative and metric-relative**. It is not a new physical time and should not be stored as one magic scalar.

The cell result shows that response-energy maturity and source-relationship maturity need not coincide.

That is enough to justify a narrow bridge note into `WidePresent`, because its existing `receiver_present.py` already implements source/receiver path frontiers and signals in flight but does not represent this second-stage distinction.

---

# Next rigorous gate

Do not tune the current rank metric.

The next test should use a quantity that is monotone as the temporal prefix grows.

For source impulse responses `h_i(t)` and `h_j(t)`, a simple finite-horizon pairwise discrimination energy is

```text
D^2_T(i,j)
    = integral_0^T || h_i(t) - h_j(t) ||^2 dt.
```

For a linear system this is directly related to the finite-horizon observability Gramian applied to the difference between source directions.

Because the integrand is nonnegative:

```text
D^2_T(i,j)
```

cannot decrease with `T`.

A noise-aware version can then ask how many source pairs cross a fixed discriminability/SNR threshold as time accumulates, under identical receiver-dimension budgets.

That is the proper next place to test `wait` versus `route`.

## One-line handoff

> **Time and receiver width trade partially, and early source relationships can mature before most response energy arrives. But normalized shape rank is non-monotone, so stop calling it observability capacity. Next use monotone pairwise discrimination energy / a finite-horizon Gramian metric, then map `wait -> T` and `route -> C` only if that survives.**
