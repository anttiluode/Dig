# Q2 — same morphology, same mechanisms, different operating state

**Status:** preregistered before execution. **Not a novelty claim.**  
**Date:** 2026-08-15.

## Why Q2 exists

The executed sequence is now:

```text
Q0  receiver projection
    soma only vs soma + dendritic ports
    -> strong change in visible source geometry

Q1  mechanism/operator ablation at rest
    full active dendrites vs dendritic active conductances zeroed
    -> modest metric deformation, almost exact neighbour topology
```

Q1 therefore did **not** test the stronger old Clockfield-like intuition:

```text
same anatomy
same mechanisms
same structural parameters
but different current state
-> different realized transfer geometry
```

Voltage-dependent local and transfer impedance in active dendrites is established literature. Q2 is not an attempt to rediscover that fact. It asks whether the **same receiver-relative source-distance measurement used throughout Dig/V23** detects a mere smooth metric change or an actual reordering of source relations on the exact Hay morphology.

---

# Fixed model

Use the same public model and exact commit as Q1:

```text
SelfishGene/neuron_as_deep_net
commit 074c4666300a8ad246601dab179a97a6942f0f29
```

Use the released full active Hay/Beniaguev model unchanged:

```text
L5PC_NEURON_simulation/morphologies/cell1.asc
L5PCbiophys5b.hoc
L5PCtemplate_2.hoc
```

No conductance is ablated or rescaled in Q2.

---

# Frozen source and receiver coordinates

Reuse the exact Q0/Q1 sites.

Sources:

```text
dend[7]  0.1666666667
dend[12] 0.5
dend[82] 0.2272727273
dend[49] 0.5
dend[62] 0.0555555556
dend[38] 0.9
dend[67] 0.9444444444
dend[70] 0.9666666667

apic[0]  0.1666666667
apic[13] 0.1153846154
apic[10] 0.9285714286
apic[18] 0.8333333333
apic[60] 0.2894736842
apic[68] 0.8333333333
apic[67] 0.3
apic[63] 0.9615384615
```

Receivers:

```text
soma[0]  0.5

dend[54] 0.1666666667
dend[67] 0.7222222222
apic[14] 0.9
apic[37] 0.2826086957
apic[71] 0.5
```

Do not reselect sites after seeing Q2.

---

# Operating-state intervention

Use a persistent **somatic DC IClamp**, not a voltage clamp, so the cell retains its normal finite input impedance and dendritic coupling.

Two target somatic operating points are frozen now:

```text
HYPER   -85 mV
DEPOL   -65 mV
```

These are target somatic voltages, not claims that the whole arbor is isopotential. The actual no-stimulus baseline voltage at every receiver must be recorded and reported.

## Hold-current calibration

For each target, on a fresh full-active cell:

1. apply a constant somatic IClamp from t=0 through the end of the run;
2. simulate a 200 ms settling interval;
3. measure mean somatic voltage over the final 20 ms of that interval;
4. choose the hold current by deterministic bisection to place that mean within **0.2 mV** of the target;
5. use that frozen hold current for the matched no-probe control and all 16 source trials in that condition.

Initial current bracket:

```text
-2 nA .. +2 nA
```

If the target is not bracketed, fail the gate rather than silently expanding the current range.

Maximum calibration iterations:

```text
24
```

This calibration is part of the intervention, not a fitted source-geometry parameter.

---

# Probe

The small source perturbation is unchanged from Q1:

```text
IClamp amplitude       0.02 nA
pulse duration         0.5 ms
```

Timing:

```text
hold starts            0 ms
state settling         200 ms
source pulse begins    220 ms
simulation end         360 ms
dt                     0.025 ms
initial voltage        -76 mV
```

The 20 ms interval between calibration window and source pulse is intentional and fixed.

Within each state condition, compute an exact matched no-source control under the same hold current:

```text
delta_v_i(t) = v_hold+source_i(t) - v_hold_control(t)
```

Use only the post-source interval for source signatures.

---

# Geometry and metrics

For every source `i`, receiver set `R`, and operating state `x`, concatenate receiver traces and L2-normalize:

```text
S_x(i | R,T)
```

Build cosine-distance matrices:

```text
D_x[i,j] = 1 - cos(S_x(i), S_x(j))
```

for:

```text
soma only
all 6 receivers
```

Compare HYPER and DEPOL using exactly the Q1 metrics:

```text
Pearson correlation of pairwise distances
Spearman correlation of pairwise distances
relative Frobenius distance
median absolute pairwise-distance change
90th percentile absolute pairwise-distance change
max absolute pairwise-distance change
nearest-neighbour identity changes
entropy effective rank
participation rank
```

Also report:

```text
calibrated hold current
achieved soma voltage
baseline voltage at each receiver
maximum absolute voltage under control and source trials
```

No class threshold is fitted.

---

# Safety / interpretation gates

## Q2-A — state-conditioned source geometry

A strong operational state effect requires more than gain scaling.

Evidence should include reproducible normalized distance-matrix deformation **and** some source-neighbour reordering and/or a material rank restructuring.

A merely lower Pearson correlation by itself is not enough if source neighbourhoods remain the same.

## Q2-B — smooth deformation / topology preserved

If pairwise distances shift but nearest-neighbour identities remain mostly or entirely fixed, conclude:

```text
operating state smoothly deforms the metric
without strongly changing the source-neighbour topology
```

This would be consistent with voltage-dependent transfer impedance but weaker than the broad phrase `state rewires causal geometry`.

## Q2-C — near-isometry null

If normalized distance matrices remain as concordant as Q1 and neighbour identity remains fixed, demote the broad state-deformation idea further for this cell/protocol.

## Q2-D — suprathreshold failure

If either no-source control or the tiny source probe produces a somatic action potential or a large regenerative event that violates the small-signal regime, report Q2 as **not interpretable as a small-signal state comparison**.

Do not change the targets or probe after seeing the result.

A future nonlinear-event experiment would require a new gate.

---

# Prior-art boundary

Voltage-dependent transfer impedance, resonance, and dendro-somatic coupling are established. Relevant primary work includes Das & Narayanan 2018 and the active-dendrite literature it builds on; other studies directly report voltage-dependent dendrite-to-soma transfer resistance.

Q2's purpose is only to put that known phenomenon into the **same source-signature / receiver-relative coordinate system** now used across Dig and V23.

---

# What Q2 can and cannot earn

A positive Q2 can support this modest engineering sentence:

> **On one fixed nonlinear morphology, the current operating state changes the receiver-relative transfer metric among source locations.**

It cannot support:

```text
time is a field
neurons have spacetime metrics
Clockfield is physics
novel voltage-dependent dendritic transfer
```

If Q2 is positive while Q1 is near-isometric, that would be especially interesting conceptually: **the same mechanism set changing state would alter transfer geometry more than deleting the mechanism set around rest.** But that comparison must be made cautiously because the interventions differ.

## One-line preregistration

> **Full active Hay cell, same anatomy/mechanisms/sources/receivers/probe; hold soma at -85 versus -65 mV with calibrated DC current and ask whether normalized source-distance topology changes.**
