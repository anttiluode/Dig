# Receipt — discrimination clock, phase/magnitude, and receiver robustness

**Date:** 2026-08-15  
**Status:** completed. Primary gate and frozen post-hoc receiver jackknife both ran successfully.

Read with:

- `DISCRIMINATION_CLOCK_GATE.md`
- `DISCRIMINATION_CLOCK_ROBUSTNESS_GATE.md`
- `OBSERVABILITY_CLOCK_COLLISION.md`
- `MONOTONE_DISCRIMINATION_RECEIPT.md`

## Model / protocol

Exact upstream model and settings were unchanged from the preceding Dig receiver work:

```text
ido4848/FCI@55826436751c03a32dfd39e91a48894869e1db57
Rat_L5b_PC_2_Hay_passive_dends_simple_soma / cell1.asc
16 frozen source sites
0.02 nA, 0.5 ms IClamp
matched no-stimulus subtraction
dt = 0.05 ms
source-relative analysis window 0..120 ms
```

Physical readouts:

```text
soma only
soma + 2 basal + 3 apical ports
```

All frozen numerical guards passed:

```text
ordered contrast-eigenvalue PSD-growth guard        PASS
finite-window Parseval guard                        PASS
phase + magnitude decomposition identity            PASS
phase-component nonnegativity                       PASS
```

Workflow:

```text
Discrimination clock
run 31894768629
artifact 9249494234
```

Robustness workflow:

```text
Discrimination clock robustness
run 31894908885
artifact 9249532249
```

---

# 1. The pair-specific evidence-arrival profile is broad

For each source pair `(i,j)` under a fixed readout, define

```text
g_ij(t) = ||h_i(t)-h_j(t)||^2
p_ij(t) = g_ij(t) / integral_0^120ms g_ij(s) ds
```

and let `t90` be the time by which 90% of that pair's final measured separation energy has accumulated.

## Soma only

Across all 120 source pairs:

```text
t90 ms
min        0.50
q10        1.05
median     7.425
q90       19.735
max       33.55
mean       9.458
```

Other timing summaries:

```text
median t50     2.20 ms
median t99    17.30 ms
median mean evidence time   3.52 ms
median evidence-time std    3.44 ms
```

## Six physical ports

```text
t90 ms
min        1.00
q10        1.90
median     8.20
q90       26.055
max       29.25
mean      11.524
```

Other timing summaries:

```text
median t50     2.95 ms
median t99    15.80 ms
median mean evidence time   3.91 ms
median evidence-time std    3.24 ms
```

Therefore the previous slow-tail maturity result was not carried by one or two pathological pairs.

A fair descriptive statement is:

> **Under one objective simulation clock, different source contrasts have substantially different evidence-arrival profiles at a fixed receiver/readout.**

Do not translate this into different physical proper times.

---

# 2. Much of the timing heterogeneity is ordinary morphology/path geometry

Preregistered descriptive Spearman correlations:

```text
                         soma       six ports

t90 vs max path          0.888       0.802
t90 vs |path_i-path_j|   0.669       0.764
```

This is a large warning against mystical interpretation.

The first explanation for the heterogeneous discrimination times in this passive-dendrite model is ordinary cable/path filtering: contrasts involving farther locations generally mature later.

The model therefore supports the phrase

```text
heterogeneous discrimination time
```

only as a receiver/task-specific signal property, not as an intrinsic local clock field.

---

# 3. Phase and magnitude genuinely separate pairwise distinguishability

On the exact finite 120 ms DFT window, every source-pair difference obeys

```text
|H_i-H_j|^2
  = (|H_i|-|H_j|)^2
    + 2 (|H_i||H_j| - Re[H_i conj(H_j)]).
```

The first term was recorded as the magnitude contribution and the second as the phase contribution.

## Soma phase fraction

```text
min       0.04525
q10       0.07276
median    0.22574
q90       0.58265
max       0.90044
mean      0.29622
```

## Six-port phase fraction

```text
min       0.00109
q10       0.01667
median    0.14775
q90       0.45827
max       0.84363
mean      0.19049
```

Thus magnitude differences dominate the median pair, but phase contribution is emphatically not a fixed small correction. Some source pairs are almost entirely magnitude-separated while others are strongly phase-separated in the measured transfer responses.

This earns a narrow reuse of the old vocabulary:

> **phase and magnitude are two exact nonnegative contributions to source distinguishability in the transfer-response representation.**

It does **not** establish biological phase coding, Clockfield physics, or a special phase-computation mechanism.

---

# 4. Raw phase-versus-time correlation is confounded by path geometry

The preregistered raw correlations were

```text
t90 vs phase fraction
soma        -0.713
six ports   -0.301
```

But phase fraction itself strongly covaries with morphology/path in this source panel. Exploratory post-run checks show that the dramatic soma `t90`/phase relation largely collapses when conditioning only on the farther source's path rank.

Therefore do **not** claim:

```text
phase information intrinsically arrives earlier than magnitude information.
```

That would require a dedicated matched-path experiment.

The robust result is pair-dependent phase contribution, not an independent phase clock.

---

# 5. The raw six-port contrast spectrum had a known local-port confound

Frozen source 6:

```text
dend[67](0.9444), path 170.5 um
```

and receiver 2:

```text
dend[67](0.7222), path 146.7 um
```

lie on the same branch.

With all six receivers, several pairs involving source 6 obtain extremely large local separation energy. The final source-contrast Gramian is consequently dominated by one direction:

```text
all six ports
final top eigenvalue          9.7626 mV^2 ms
participation rank            1.0700
```

This does not invalidate a receiver-relative Gramian. It demonstrates exactly why its spectrum cannot be called an intrinsic morphology spectrum without controlling `C`.

---

# 6. Frozen receiver jackknife: timing and phase survive, spectrum changes drastically

The post-hoc gate dropped each dendritic receiver without moving any port.

Most important control: remove receiver 2, the same-branch `dend[67]` port.

```text
J2 = receivers [soma, r1, r3, r4, r5]
```

## Timing after removing same-branch receiver

```text
t90 ms
min        0.65
q10        2.705
median     6.975
q90       27.47
max       32.45
```

## Phase fraction after removing same-branch receiver

```text
min        0.01233
q10        0.04030
median     0.22893
q90        0.55088
max        0.84474
```

## Path relation

```text
Spearman(t90, max_path) = 0.892
```

So both broad timing heterogeneity and broad phase/magnitude mixing survive the local-port removal cleanly.

But the spectrum changes sharply:

```text
                         full six       drop r2

top eigenvalue             9.7626        0.2414
participation rank          1.0700        1.7198
```

This is an important correction:

> **The finite-horizon source spectrum is strongly receiver-relative. It is not an intrinsic morphology fingerprint under the present measurement.**

That is not a failure of the Gramian picture; `C` is explicitly part of the object.

---

# 7. Strongest mathematical object after the gate

For source basis `B_s`, output/readout `C`, and linear dynamics `A`, define

```text
Y(t) = C exp(A t) B_s

G_C,T = integral_0^T Y(t)^T Y(t) dt.
```

Then

```text
dG_C,T/dT = Y(T)^T Y(T) >= 0
rank(dG_C,T/dT) <= number_of_output_ports.
```

This is the exact conservative version of the old `one iota` intuition:

> every extra instant adds a positive-semidefinite information slice, whose direction and strength depend on the receiver.

For an observable continuous LTI system, however, exact algebraic rank need not grow one mode at a time with `T`; it can already be full for every `T>0`. The meaningful short-horizon phenomenon is conditioning/effective visibility under noise or finite precision.

The `m*k` counting belongs to the finite observability/Krylov stack

```text
[C; CA; ...; CA^(k-1)]
```

not to a theorem saying the exact Gramian rank increases by `m` per time step.

---

# 8. Clockfield / black-hole / Connes boundary

What carried over usefully:

```text
operator/readout -> spectrum
source contrasts -> metric/pseudometric
finite horizon -> growing information geometry
phase + magnitude -> exact response decomposition
null direction -> unobservable contrast
```

What did not:

```text
state bends the small-signal metric dramatically       NOT SEEN
proper-time field                                      NOT TESTED
black-hole/event horizon                               NO IDENTIFICATION
Connes spectral distance                               DIFFERENT CONSTRUCTION
thermodynamic/black-hole entropy                       NO IDENTIFICATION
```

The old projects can remain idea generators, but the present object is ordinary finite-horizon observability / signal discrimination.

---

# 9. Where this is immediately useful

A direct engineering reuse was found in `TransientWaveCompiler`.

TWC already distinguishes:

```text
raw response sensitivity
vs
candidate sensitivity that remains novel after fitted physical+nuisance compensation
vs
exact topology-gauge directions that no static response can label uniquely.
```

A finite-horizon sensitivity/Fisher matrix can add:

```text
when does a candidate become practically distinguishable?
which measured port/channel exposes it fastest?
when can waiting no longer help?
which known perturbation rotates a dark direction into view?
```

A prior-art-aware bridge was written to the active TWC branch:

```text
docs/FINITE_HORIZON_CAPABILITY_BRIDGE_2026-08-15.md
```

The proposed first gate uses the existing published-filter synthetic benchmark and asks whether the finite-horizon curve changes an actual measurement decision. If it merely restates the full-window ranking, the extension dies.

---

## One-line state

> **The reusable survivor is a receiver-relative finite-horizon information geometry. Its evidence-arrival times are broadly pair-specific but largely shaped by ordinary morphology; its phase/magnitude decomposition is exact and highly pair-dependent; and its spectrum changes strongly with the readout rather than belonging intrinsically to the neuron.**
