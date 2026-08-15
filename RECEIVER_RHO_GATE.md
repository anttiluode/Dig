# Receiver gate: rho scaling means FCI is measured after morphology-dependent output compensation

**Status:** paper/code interpretation + control experiment. Not an accusation of confounding.  
**Date:** 2026-08-15.

## 0. Why the receiver deserves its own box

Aizenbud et al. do not attach an identical soma/axon spike generator to every dendritic morphology.

They explicitly compensate the somatic and axonal Na/K conductances for the electrical load imposed by each dendritic tree using `rho_soma` and `rho_axon`.

That is described in the Methods and implemented in every released model wrapper.

It is a sensible normalization: a huge dendritic tree should not trivially make a fixed spike generator harder to drive just because it presents a larger electrical load.

But it also means the published FCI is a property of

```text
dendritic morphology
+
rho-compensated receiver
+
input-rate normalization
+
fixed TCN probe
```

not of morphology attached to one identical receiver.

---

## 1. Exact four-model numbers

The released `properties.json` values are:

```text
cell                  rho_soma      rho_axon
rat L2 BBP              30.95        127.00
rat L5 Hay              32.59        247.23
human L2/3 Eyal         72.76        658.88
human L5 BBP            48.18        462.94
```

The Hay rat L5 model is the reference in the wrappers.

Therefore the scaling factors relative to Hay are approximately:

```text
cell                  soma factor   axon factor
rat L2 BBP                0.950        0.514
rat L5 Hay                1.000        1.000
human L2/3 Eyal           2.233        2.665
human L5 BBP              1.479        1.873
```

So one tempting statement needs correction:

> human L2/3 is not ~5x the Hay axonal reference.

It is about **2.67x Hay**. It is about **5.19x rat L2**, because rat L2 itself is scaled to about half of Hay at the axon.

---

## 2. What the code does

The common HOC model supplies reference soma/axon Na/K conductances.

Each wrapper computes

```text
scale_factor      = rho_test      / rho_exemplar
scale_factor_axon = rho_axon_test / rho_axon_exemplar
```

and multiplies both Na and K maximal conductances in the corresponding soma/axon sections by those factors.

So morphology changes the dendritic load and the experiment deliberately adjusts the receiver to compensate for that load.

The paper then separately chooses E/I input-rate regimes that yield ~1 spike/s output.

These are two distinct normalizations:

```text
receiver conductance scaling
and
operating-point / firing-rate selection.
```

---

## 3. This does not invalidate FCI; it defines its question

The normalized experiment asks roughly:

> after compensating gross dendritic load so the cells remain in comparable output regimes, how complicated is the remaining dendrite-to-spike transformation for the fixed TCN?

That is arguably the more interesting biological comparison.

But our mechanistic decomposition should make the normalization explicit because the final FCI score is based on spike prediction.

A dendritic mechanism could be partly hidden or amplified by the morphology-specific receiver compensation.

---

## 4. Cheap receiver controls before full FCI

On a fixed morphology/input ensemble compare:

```text
RHO     published rho-scaled soma/axon conductances
FIXED   identical Hay-reference soma/axon conductances
```

For both conditions record direct detailed-neuron quantities before training a TCN:

```text
subthreshold somatic voltage
spike threshold crossings
spike disagreement rate
F-I curve
input rate required for 1 sp/s
```

Then do a third readout that avoids the spike generator as much as possible:

```text
SUBTHRESHOLD
    clamp/omit spikes and compare dendrite -> soma voltage transformation
```

This separates

```text
dendritic transformation
from
receiver compensation
from
binary spike readout.
```

---

## 5. The useful FCI experiment if the cheap gate matters

Only if RHO vs FIXED materially changes the I/O mapping, estimate FCI under both definitions while independently matching output rate.

Then ask whether morphology rankings are preserved.

```text
rank stable:
    FCI morphology conclusion is receiver-normalization robust

rank changes:
    part of the published ordering is conditional on the chosen load compensation
```

Neither outcome makes the original analysis wrong. They answer different controlled questions.

---

## 6. Relation to the AIS / extracellular thread

The axon initial segment can dominate the high-frequency extracellular action-potential landscape.

Therefore any later comparison of extracellular spike fields across these models must remember that axonal conductances have already been rescaled with morphology.

For extracellular work, keep two source regimes separate:

```text
subthreshold dendritic field
spike/AIS field
```

Otherwise a morphology-dependent dendritic field effect can be mixed with a deliberately morphology-dependent spike-generator scaling.

## Source anchors

- Aizenbud et al. PNAS 2026, Methods equations 2--3 — rho normalization of soma/axon active conductances.
- released FCI `properties.json` files — exact rho values.
- released `get_standard_model.py` wrappers — explicit soma/axon conductance scaling.

## Current sentence

> **The published FCI comparison is not “same receiver, different tree”; it is “different tree with gross electrical load compensated at the receiver.” That is a deliberate normalization. Keep it, but add a fixed-receiver control if we want to know which complexity belongs to the dendritic transform and which belongs to the compensated dendrite-to-spike system.**
