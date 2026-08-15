# Monotone finite-horizon discrimination gate

**Date:** 2026-08-15  
**Status:** preregistered before execution. **Control-theory measurement, not a novelty claim.**

## Why this gate is needed

`SPACE_TIME_OBSERVABILITY_RECEIPT.md` found a useful but methodologically dangerous result.

The normalized source-shape geometry showed a strong apparent space/time trade, but its entropy effective rank was non-monotone:

```text
six-port normalized entropy rank
0.5 ms   8.38
1 ms     9.38
2 ms     9.77
...
120 ms   8.52
```

That is allowed for row-normalized cosine geometry, but it is not a literal measure of finite-horizon observability capacity: appending samples cannot erase samples an ideal observer already has.

So this gate switches to a quantity that is mathematically monotone in the observation horizon.

---

# Core quantity

For source impulse responses `h_i(t)` and `h_j(t)` observed through receiver map `C`, define

```text
D_C,T^2(i,j)
    = integral_0^T || h_i(t) - h_j(t) ||_2^2 dt.
```

In the fixed-step simulation this is evaluated by a Riemann sum using the simulation `dt`.

Every integrand is nonnegative, therefore for a fixed receiver map:

```text
T2 >= T1
=>
D_C,T2^2(i,j) >= D_C,T1^2(i,j)
```

for every source pair.

For a local linear model this is the finite-horizon observability-Gramian quadratic form applied to the difference between two source/input directions.

If each measured output sample has equal independent additive Gaussian noise variance `sigma^2`, then

```text
D^2 / sigma^2
```

is proportional to squared pairwise discriminability. No `sigma` is chosen here, so the gate stays threshold-free.

---

# Frozen biological protocol

Pin exactly:

```text
ido4848/FCI
commit 55826436751c03a32dfd39e91a48894869e1db57
```

Use the exact Q0 impulse protocol:

```text
Rat_L5b_PC_2_Hay_passive_dends_simple_soma / cell1.asc
16 fixed source sites
6 fixed receivers
0.02 nA source IClamp
0.5 ms duration
20 ms delay
140.05 ms integration end
0.05 ms dt
-70 mV initialization
matched no-stimulus subtraction
```

The analyzed response horizon still ends at source-relative `120.00 ms`.

---

# Frozen horizons

```text
T = 0.5, 1, 2, 5, 10, 20, 40, 80, 120 ms
```

Every shorter horizon is a prefix of the same trajectory.

---

# Part A — physical soma and six-port discrimination maturation

For each horizon and receiver map:

```text
C_soma
C_six
```

compute `D_T^2(i,j)` for all `16 choose 2 = 120` source pairs.

Report raw threshold-free distributions in units of `mV^2 ms`:

```text
minimum
10th percentile
median
90th percentile
maximum
```

For each source pair also compute its within-map final-fraction maturity:

```text
M_T(i,j) = D_T^2(i,j) / D_120^2(i,j).
```

Report:

```text
minimum maturity
10th percentile maturity
median maturity
90th percentile maturity
fraction of pairs >= 0.50
fraction of pairs >= 0.90
fraction of pairs >= 0.99
```

Fixed reporting landmarks:

```text
first T where median pair maturity >= 0.50, 0.90, 0.99
first T where at least 90% of pairs have maturity >= 0.50, 0.90, 0.99
```

These are descriptive landmarks, not success thresholds.

---

# Part B — output-dimension / time frontier

For retained receiver dimension

```text
k = 1..6
```

use exactly `128` random orthonormal projections of the six physical receiver channels.

Fixed seed:

```text
20260818
```

For each `k`, generate the projection matrices once and reuse the exact same matrices at every temporal horizon.

For every projection and horizon compute the median pairwise discrimination energy.

Report the distribution over projections:

```text
5th percentile
median
95th percentile
```

Normalize the median frontier to one fixed external reference only for convenience:

```text
R(k,T)
 = median_pair_D2(k,T)
   / median_pair_D2(full six-port, 120 ms).
```

The raw `mV^2 ms` values remain primary.

Fixed frontier landmarks:

For each `k`, report the first T at which the **median over random projections** reaches

```text
10%
25%
50%
75%
90%
```

of the physical six-port 120 ms median pair discrimination energy.

Do not add thresholds after seeing the data.

---

# Part C — monotonicity guards

For every physical source pair and every random projection:

```text
D_T^2
```

must be nondecreasing across the horizon grid up to numerical tolerance.

Required guard:

```text
minimum increment >= -1e-12 mV^2 ms
```

At `k=6`, orthonormal receiver mixing must preserve every pairwise discrimination energy to numerical precision.

Required guard:

```text
max relative error < 1e-10
```

Failure of either guard is a harness failure, not a scientific result.

---

# Interpretation

## M-A — waiting genuinely accumulates discriminability

This should occur trivially in the mathematical sense because the metric is cumulative.

The interesting quantity is **how fast** different source pairs mature and whether the soma and six-port receiver maps have very different maturation distributions.

## M-B — route/readout width substitutes for waiting

If larger `k` at short `T` reaches the same absolute pairwise discrimination energy that smaller `k` reaches only later, then the modest operational statement is:

> **under a fixed measurement-noise scale, output width and waiting time are partially substitutable resources for source discrimination in this medium.**

This is not a new theorem.

## M-C — projection loss remains after waiting

If low `k` saturates far below full-six-port discrimination even by 120 ms, then some discrimination energy is destroyed by the output bottleneck rather than merely delayed.

## M-D — geometry-maturity story collapses to ordinary energy integration

If pairwise maturation curves simply mirror total response-energy fractions and source-pair variability is negligible, then the earlier `observability maturity` phrase adds little beyond ordinary signal integration.

---

# WidePresent / PivotPoint boundary

Only if this gate survives cleanly should we use the following engineering mapping:

```text
WAIT     -> increase finite horizon T
ROUTE    -> change receiver/readout C
PROBE    -> inject another discriminating input
ACT      -> change the controlled state/world
```

The mapping is standard systems language applied to the project, not a new architecture result.

## One-line preregistration

> **Measure cumulative pairwise response-separation energy on the exact Q0 tensor, with fixed source/receiver biology and fixed random readout maps, so `wait` can only add evidence and `route` can only change what evidence is observed.**
