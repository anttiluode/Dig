# Q1 — fixed morphology, active-dendrite state/operator deformation

**Status:** preregistered before execution. **Not a novelty claim.**  
**Date:** 2026-08-15.

## Motivation

`RECEIVER_COLLAPSE_CELL1_Q0_RECEIPT.md` established a simple baseline on the exact Hay `cell1.asc` morphology:

```text
same anatomy + same source perturbations

soma-only normalized source signatures:
    entropy rank = 3.8384

soma + 5 dendritic receivers:
    entropy rank = 8.5159
```

The receiver effect survived every leave-one-dendritic-port-out control.

That does **not** establish state-dependent geometry. Q1 asks the second clause of the older V23 sentence:

> Different local states / dynamics deform the modes or transfer structure seen by a receiver.

The relevant prior art is broad: active/quasi-active membrane properties, transfer impedance, resonance, dendritic functional subunits, and Hay-model active dendritic nonlinearities are all established. The purpose here is only to build a controlled bridge across our own project family.

---

# Fixed anatomy / provenance

Use the official public code for Beniaguev, Segev & London 2021:

```text
SelfishGene/neuron_as_deep_net
commit 074c4666300a8ad246601dab179a97a6942f0f29
```

Its

```text
L5PC_NEURON_simulation/morphologies/cell1.asc
```

is byte-identical to the `cell1.asc` used in the FCI bridge already verified in `EXACT_L5_BRIDGE.md`.

Instantiate the released Hay biophysics using:

```text
L5PCbiophys5b.hoc
L5PCtemplate_2.hoc
```

The HOC model inserts active conductances in the apical tree and Ih in basal dendrites while retaining active soma/axon mechanisms.

---

# Conditions

This gate does **not** assume that the historical Python variable `useActiveDendrites` is a complete ablation implementation.

Instead define two auditable conditions inside the same released model family.

## ACTIVE

Use the released Hay/Beniaguev dendritic conductance values unchanged.

## DENDRITE_ABLATED

Keep fixed:

```text
morphology
dendritic Ra / cm / passive leak
soma and axon conductances
source locations
receiver locations
initial voltage
pulse
integration settings
```

Set only dendritic maximal active conductances to zero.

Apical:

```text
gSK_E2bar_SK_E2
gCa_LVAstbar_Ca_LVAst
gCa_HVAbar_Ca_HVA
gSKv3_1bar_SKv3_1
gNaTs2_tbar_NaTs2_t
gImbar_Im
gIhbar_Ih
```

Basal:

```text
gIhbar_Ih
```

`CaDynamics_E2` is a calcium-state mechanism rather than an independent membrane conductance; it may remain inserted because calcium current is zero when the dendritic Ca conductances are zero.

This is **our explicit ablation**, not a claim to reproduce an author's named passive-dendrite condition.

---

# Frozen source / receiver coordinates

Reuse exactly the Q0 named section/x coordinates.

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

Do not reselect these from the active model.

---

# Probe

Use a small fixed current perturbation, matched between conditions:

```text
IClamp amplitude      0.02 nA
pulse duration        0.5 ms
stimulus delay        20 ms
simulation horizon    160 ms
dt                    0.025 ms
initial voltage       -76 mV
```

For each condition compute a matched no-stimulus trajectory and use

```text
delta_v_i(t) = v_stim_i(t) - v_control(t).
```

The longer horizon / finer dt relative to Q0 are fixed now because this is a new model family with active channel kinetics. They are identical between ACTIVE and DENDRITE_ABLATED.

---

# Geometry

For every source `i`, receiver set `R`, condition `x`, concatenate the receiver traces and L2-normalize:

```text
S_x(i | R,T).
```

Construct cosine-distance matrices

```text
D_x[i,j] = 1 - cos(S_x(i), S_x(j)).
```

for:

```text
soma only
all 6 receivers
```

Do not define source classes with a fitted threshold.

---

# Primary comparison

Compare ACTIVE versus DENDRITE_ABLATED using the upper triangles of `D`.

Report:

```text
Pearson correlation of pairwise distances
Spearman correlation of pairwise distances
relative Frobenius distance between D matrices
median absolute pairwise-distance change
90th percentile absolute pairwise-distance change
nearest-neighbour identity changes across sources
entropy effective rank in each condition
participation rank in each condition
```

All metrics are fixed before execution.

---

# Interpretation gate

## Q1-A — state/operator deformation survives

A useful positive requires **more than amplitude or one source becoming locally large**.

Evidence must include at least qualitative structure such as:

```text
normalized D_active != D_ablated
AND
source neighbour order changes for multiple sources
AND/OR
rank structure changes materially
```

No numerical success threshold is fitted after the run. Report the continuous quantities.

## Q1-B — gain-only / near-isometry null

If normalized source-distance matrices remain highly concordant and neighbour identities are mostly preserved, then the active conductances mainly deform gain/time constants without strongly changing this receiver-visible source geometry under the small-signal rest-state probe.

Call that a null for the stronger `state -> geometry` reading under this protocol.

## Q1-C — active-event warning

If the 0.02 nA pulse itself triggers spikes or large regenerative dendritic events in ACTIVE but not in the ablation, this ceases to be a clean small-signal comparison. Report it and do not quietly reduce/increase the pulse after seeing the result.

A later nonlinear-event gate would need a separate preregistration.

---

# What this does not test

It does not test:

```text
NMDA history dependence
STP-address binding
FCI directly
task performance
growth/access geometry
consciousness
new physics
```

It asks only:

> **On byte-identical anatomy and frozen source/receiver coordinates, does removing the released dendritic active conductance set substantially change the normalized receiver-visible transfer geometry?**

That is the clean next experiment after Q0.
