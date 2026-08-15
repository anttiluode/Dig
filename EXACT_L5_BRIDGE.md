# Exact L5 bridge: one morphology already connects two complexity programs

**Status:** provenance result + experiment opportunity.  
**Date:** 2026-08-15.

A useful concrete bridge fell out of the FCI/TwinProp dig.

## 1. The same `cell1.asc` exists in both released repositories

The Aizenbud et al. 2026 FCI repository contains the rat L5 Hay morphology at:

```text
ido4848/FCI
simulating_neurons/neuron_models/rat/hay/
Rat_L5b_PC_2_Hay_passive_dends_simple_soma/
morphologies/cell1.asc
```

Its Git blob SHA-1 is:

```text
2ba87cb91601c44a78a764646cf5abd01d5e1266
```

The official code repository for Beniaguev, Segev & London 2021, *Single Cortical Neurons as Deep Artificial Neural Networks*, loads:

```text
SelfishGene/neuron_as_deep_net
L5PC_NEURON_simulation/morphologies/cell1.asc
```

At commit:

```text
074c4666300a8ad246601dab179a97a6942f0f29
```

that file has the **same Git blob SHA-1**:

```text
2ba87cb91601c44a78a764646cf5abd01d5e1266
```

Therefore these are not merely two files both called `cell1.asc`: the public bytes are identical.

`verify_l5_bridge.py` re-downloads both files and checks byte equality plus the Git blob hash.

## 2. This cell already has a published FCI coordinate

The frozen V22 morphology mapping identifies this author-released Hay morphology as **order 7** in the Aizenbud Fig. 2 panel.

The published/digitized Fig. 2 FCI table gives:

```text
order 7 -> FCI = 0.2342
```

So a morphology that sits inside the 2021 deep-surrogate program is literally one of the 24 morphologies in the 2026 FCI program.

This does **not** mean the complete biophysical models are identical.

That distinction is crucial.

## 3. Same geometry, different dynamical regimes

The Beniaguev 2021 simulation code instantiates the Hay L5PC morphology with an actively conducting L5PC model. That work famously found that the realistic NMDA-equipped model required a deep temporal surrogate, while removing NMDA dramatically simplified the required artificial network.

The main Aizenbud 2026 FCI panel deliberately uses a much more standardized model family: dendrites are primarily passive, with spiking conductances in soma/axon and AMPA+NMDA / GABAA synapses distributed along the tree. A supplementary intervention adds the full active dendritic conductance set to the rat L5 model and reports a significant FCI increase.

This gives us an unusually clean conceptual decomposition on **the exact same morphology**:

```text
same cell1.asc
    |
    +-- standardized/passive-dendrite FCI regime
    |
    +-- full active Hay/Beniaguev regime
```

Geometry is held fixed while the local dynamical operator changes.

That is almost the ideal controlled version of the old Clockfield/`state changes the operator` intuition, without any new physics language.

## 4. What we can test before TwinProp code is released

The TwinProp preprint states that it uses the detailed Hay et al. 2011 rat L5PC and builds directly on the Beniaguev digital-twin line, but its code/data are promised only upon publication. Until those bytes are public, do **not** claim that TwinProp uses this exact file.

We nevertheless already have enough public material for an exact-geometry intervention series.

For `cell1.asc`, construct several progressively richer regimes:

```text
P0  passive cable only
P1  Aizenbud standardized passive dendrite + rat AMPA/NMDA/GABAA
P2  P1 + Ih only
P3  P1 + full Hay dendritic voltage-gated conductances
P4  Beniaguev/Hay active model under its original synaptic protocol
```

At each stage measure the same frozen set:

```text
linearized/holding-state impedance or Green kernels
NET compartment structure
state-dependent linearized kernels where defined
dendritic trajectory effective dimension under matched drive
somatic I/O surrogate difficulty under a common probe
```

The key is **matched drive**. Otherwise every model change also changes the stimulus ensemble.

## 5. A sharp question: what changes when geometry does not?

Suppose anatomy is fixed at `cell1.asc`.

Then any change in computational behavior must come from the operating equations, synapses, conductances, or input regime rather than gross morphology.

This lets us separate two kinds of 'geometry' that have been blurred in the older work:

```text
ANATOMICAL GEOMETRY
    fixed branch lengths, diameters, topology

OPERATIONAL / ELECTRICAL GEOMETRY
    state- and mechanism-dependent transfer between locations
```

Wybo's impedance/NET framework already gives respectable mathematics for the second in linear/linearized regimes.

So instead of asking whether Clockfield was right, ask something measurable:

> **How much can the effective interaction geometry of one fixed reconstructed neuron be deformed solely by changing its conductance/synaptic operating regime, and which deformations correspond to increased FCI or task capability?**

## 6. One especially strong experiment

Take a fixed set of dendritic source locations `i` and receiver locations `r` on `cell1.asc`.

For each regime `P0...P4`, around a matched operating state, estimate

```text
H_x(r,i,t)
```

or its frequency/impedance equivalent.

Then compare pairwise source distances defined only from their receiver signatures:

```text
d_x(i,j | R,T)
```

using the same receivers `R`, horizon `T`, normalization, and noise threshold in every condition.

Now ask whether adding active mechanisms:

```text
creates new distinguishable source classes,
collapses old source classes,
changes NET independence,
or only rescales existing responses.
```

This is a much sharper 'geometry bends' test than comparing unrelated morphologies.

It also has an immediate null:

> If the state/mechanism changes mostly rescale response amplitudes while the normalized source-response geometry remains stable, then the stronger Clockfield-like interpretation loses.

## 7. Why this bridge matters for FCI ↔ capacity

This exact shared morphology gives us a calibration point before attempting cross-cell correlations.

We can ask, on one anatomy:

```text
mechanism intervention
       -> change in electrical/local-transfer geometry
       -> change in task-evoked dynamics
       -> change in fixed-probe FCI
       -> change in realizable task capacity
```

The PNAS paper already establishes one arrow qualitatively: adding active dendritic conductances to rat L5 significantly raises FCI.

TwinProp establishes on an active Hay L5PC that active dendritic channels + NMDA + morphology are jointly required for near-ceiling parity performance.

What is missing is the **same-model intervention ladder measured with all quantities together**.

That is experimentally much cleaner than beginning with 24 different cells.

## 8. Guardrails

Do not claim:

```text
same morphology -> same neuron model
```

It does not.

Do not claim:

```text
TwinProp exact morphology verified
```

until its promised repository becomes public or the authors specify the exact file.

Do not interpret a change in a linearized impedance geometry as the full nonlinear computation.

Do not optimize a new geometry metric after looking at FCI/task outcomes.

The useful fact is narrower and solid:

> **The FCI and Beniaguev deep-neuron programs already share byte-identical Hay L5 anatomy, giving us a fixed-geometry laboratory in which to vary dynamics instead of morphology.**

That is enough to build on.