# Monotone finite-horizon discrimination — receipt

**Date:** 2026-08-15  
**Status:** executed preregistered gate. **Clean positive measurement, not a novelty claim.**  
**Gate:** `MONOTONE_DISCRIMINATION_GATE.md`  
**Executable:** `finite_horizon_discrimination_cell1.py`

## Provenance

Pinned public model:

```text
ido4848/FCI
commit 55826436751c03a32dfd39e91a48894869e1db57
```

Exact Q0 impulse protocol:

```text
Rat_L5b_PC_2_Hay_passive_dends_simple_soma / cell1.asc
16 fixed source sites
6 fixed receivers
0.02 nA / 0.5 ms source IClamp
matched no-stimulus subtraction
0.05 ms dt
response horizon 0..120 ms
```

Valid GitHub Actions run:

```text
31888979498
```

Dig commit tested:

```text
60726a95b0db440303e646594037e664b9c6b091
```

---

# Metric

For each source pair `i,j` and fixed receiver map `C`:

```text
D_C,T^2(i,j)
    = integral_0^T || h_i(t) - h_j(t) ||_2^2 dt
```

Units in the simulation:

```text
mV^2 ms
```

No source-row normalization is applied.

For equal independent additive measurement-noise variance per output sample, this separation energy is proportional to squared pairwise discriminability up to the unspecified noise scale.

Pair-specific maturity is defined only relative to the same receiver's final 120 ms value:

```text
M_C,T(i,j)
    = D_C,T^2(i,j) / D_C,120^2(i,j).
```

This is receiver- and source-pair-specific. It is not a new physical time.

---

# Hard guards

Preregistered monotonicity requirement:

```text
minimum D^2 increment across the horizon grid >= -1e-12 mV^2 ms
```

Observed global minimum increment across:

```text
physical soma
physical six-port
all 6 x 128 random readout projections
all 120 source pairs
```

was:

```text
+8.64e-24 mV^2 ms
```

**PASS.**

Six-dimensional orthonormal readout remix must preserve pairwise discrimination energy.

Observed maximum pairwise relative error:

```text
2.61e-12
```

Required:

```text
< 1e-10
```

**PASS.**

So this gate has the monotone behavior the earlier normalized-rank proxy lacked.

---

# Final absolute discrimination differs strongly by receiver width

At 120 ms:

```text
median pair D^2

soma only     0.00273869 mV^2 ms
six-port      0.02463004 mV^2 ms
```

The six-port median pair separation energy is therefore about:

```text
9.0 x
```

the physical soma-only median under the same source perturbations.

This is not a claim that six ports are biologically better. More measured output dimensions contain more signal energy and, under an equal per-channel noise model, more discriminating evidence.

---

# Pairwise maturation — soma

```text
T ms   median M_T   10th-percentile M_T   fraction pairs >=90%   >=99%

0.5      0.0100          0.00000031               0.0083          0.000
1        0.1199          0.000158                 0.0917          0.025
2        0.4399          0.0119                   0.2417          0.100
5        0.7897          0.1928                   0.4083          0.225
10       0.9474          0.5609                   0.5583          0.375
20       0.9946          0.9042                   0.9000          0.533
40       0.99992         0.9956                   1.0000          0.950
80       ~1.0            0.999994                 1.0000          1.000
120      1.0             1.0                      1.0000          1.000
```

Preregistered landmarks:

```text
median pair >=50% maturity          5 ms
90% of pairs >=50%                 10 ms
median pair >=90%                  10 ms
90% of pairs >=90%                 20 ms
median pair >=99%                  20 ms
90% of pairs >=99%                 40 ms
```

---

# Pairwise maturation — six-port

```text
T ms   median M_T   10th-percentile M_T   fraction pairs >=90%   >=99%

0.5      0.0131          0.000135                 0.0000          0.000
1        0.0936          0.00629                  0.0167          0.000
2        0.3555          0.0667                   0.1667          0.000
5        0.7112          0.2963                   0.2917          0.150
10       0.9445          0.5043                   0.5333          0.300
20       0.9970          0.8039                   0.8000          0.583
40       0.99990         0.9835                   1.0000          0.800
80       ~1.0            0.999945                 1.0000          1.000
120      1.0             1.0                      1.0000          1.000
```

Landmarks:

```text
median pair >=50% maturity          5 ms
90% of pairs >=50%                 10 ms
median pair >=90%                  10 ms
90% of pairs >=90%                 40 ms
median pair >=99%                  20 ms
90% of pairs >=99%                 80 ms
```

The richer receiver set therefore does **not** simply give the same distinctions earlier. It exposes additional source-pair differences whose discriminating energy can continue accumulating on slower timescales.

That is why the tail maturity landmarks are later for six ports than for the soma.

---

# The strongest separation from ordinary response-energy arrival

The previous space-time run measured total six-port response energy accumulated by each horizon:

```text
T=10 ms   98.23% of final aggregate response energy
T=20 ms   99.47%
```

But the monotone discrimination gate says:

```text
T=10 ms
    median source pair discrimination maturity     94.45%
    10th-percentile pair maturity                  50.43%
    only 53.3% of source pairs >=90% mature

T=20 ms
    median source pair discrimination maturity     99.70%
    10th-percentile pair maturity                  80.39%
    only 80.0% of source pairs >=90% mature
```

Thus almost all **aggregate signal energy** can already be present while a nontrivial subset of alternative causes remains substantially less separated than it will become later.

This kills the simplest version of:

```text
maturity = fraction of signal energy arrived.
```

A receiver can have almost all of the response energy and still lack a substantial fraction of the eventual evidence for distinguishing particular source alternatives.

---

# The important correction: maturity is a matrix, not a scalar

The data argue against attaching one number like

```text
maturity(event) = 0.73
```

as though all causal alternatives become resolved together.

At a given horizon, different source pairs can have radically different maturities.

The natural object is closer to:

```text
D_C,T[i,j]
```

or its normalized within-receiver maturity form:

```text
M_C,T[i,j].
```

That is:

> **a receiver-relative finite-horizon geometry over candidate causes.**

This is ordinary systems / signal-detection mathematics, not a newly invented geometry.

But it is a much more faithful project object than a scalar `present width` or scalar `causal maturity`.

---

# Output-width versus waiting-time frontier

The gate used 128 fixed-seed random orthonormal readouts for every retained output dimension `k=1..6`, with the same projection reused at every temporal horizon.

Reference:

```text
physical six-port 120 ms median pair D^2
= 0.02463004 mV^2 ms
```

Median random-readout pair separation as a fraction of that fixed reference:

```text
T ms    k=1      k=2      k=3      k=4      k=5      k=6

0.5    0.0006   0.0020   0.0036   0.0067   0.0097   0.0126
1      0.0063   0.0190   0.0299   0.0424   0.0523   0.0624
2      0.0221   0.0626   0.1042   0.1537   0.1849   0.2305
5      0.0510   0.1335   0.2114   0.3116   0.3819   0.4563
10     0.0743   0.1867   0.3095   0.4385   0.5727   0.6748
20     0.1045   0.2490   0.4048   0.5756   0.7460   0.8909
40     0.1261   0.2936   0.4564   0.6408   0.8765   0.9986
80     0.1281   0.2965   0.4588   0.6441   0.8866   ~1.000
120    0.1281   0.2965   0.4588   0.6441   0.8866   1.000
```

This is the clean space/time result.

## Waiting helps

For a fixed `k`, discrimination energy accumulates with time.

## But waiting cannot replace missing readout dimensions

Long-time ceilings remain strongly dimension dependent:

```text
k=1    ~12.8% of six-port reference
k=2    ~29.7%
k=3    ~45.9%
k=4    ~64.4%
k=5    ~88.7%
k=6   100%
```

So under this fixed equal-per-output-noise interpretation, a low-dimensional projection destroys discrimination energy that more waiting cannot recover.

## Frozen frontier landmarks

```text
k=1
    reaches 10% at 20 ms
    never reaches 25%

k=2
    reaches 10% at 5 ms
    25% at 40 ms
    never reaches 50%

k=3
    reaches 10% at 2 ms
    25% at 10 ms
    never reaches 50%

k=4
    reaches 10% at 2 ms
    25% at 5 ms
    50% at 20 ms
    never reaches 75%

k=5
    reaches 10% at 2 ms
    25% at 5 ms
    50% at 10 ms
    75% at 40 ms
    never reaches 90%

k=6
    reaches 10% at 2 ms
    25% at 5 ms
    50% at 10 ms
    75% at 20 ms
    90% at 40 ms
```

This earns the modest operational statement:

> **Waiting and readout width are partially substitutable, but not fully substitutable. A narrow receiver can hit an information ceiling that additional waiting does not remove.**

Again: standard observability/sensor-bandwidth logic, measured here on the fixed dendritic medium.

---

# Connection to PivotPoint

This is the cleanest empirical interpretation of `wait` versus `route` we have found.

For a fixed observation map `C`:

```text
WAIT
    increases T
    -> D_C,T can only accumulate
    -> useful while relevant pairwise distinctions are still growing
```

Changing route/readout changes `C`:

```text
ROUTE
    changes which output subspace is observed
    -> can raise the asymptotic discrimination ceiling
    -> can expose distinctions that waiting under the old readout never recovers
```

That does **not** prove a PivotPoint architecture helps an AI agent.

But it gives a rigorous toy condition for when waiting is structurally futile:

```text
required discrimination > asymptotic capability of current readout C
```

Then more `T` cannot solve the problem; the system must change readout, probe, or act.

The actual task/noise threshold would have to come from a real downstream problem and must not be invented from this dataset.

---

# Connection to WidePresent / PresentMoment

The clean hierarchy is now:

```text
EVENT AGE
    when did it happen?

TRANSPORT FRONTIER
    could its consequence have arrived here yet?

RESPONSE ENERGY
    how much aggregate response has arrived?

PAIRWISE DISCRIMINATION MATURITY
    which alternative causes have become distinguishable to this receiver,
    and by how much?
```

The last object is not one extra clock.

It is a **matrix over alternatives**, conditional on receiver/readout and horizon.

That is a much better formal descendant of the old phrase `partial causal maturity` than a scalar present-width register.

---

# Current scientific boundary

Nothing here is a new observability theorem.

Finite-horizon observability Gramians, sensor placement, output selection, matched-filter discrimination and information accumulation are established.

The result matters internally because it replaces several vague project claims with one object that:

```text
is measurable
is receiver-relative
is horizon-dependent
obeys a monotonicity guard
has an explicit output-bottleneck ceiling
separates aggregate response arrival from pair-specific discrimination
```

That is enough to keep digging.

## One-line handoff

> **The strongest surviving object is not “geometry bends with state.” It is the finite-horizon discrimination matrix `D_C,T`: waiting grows distinctions within a fixed readout, routing changes the attainable ceiling, and almost-complete aggregate signal arrival does not mean all candidate causes are maturely distinguishable.**
