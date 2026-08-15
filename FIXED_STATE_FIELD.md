# Same local state machines, different coupling: a useful property of the released FCI discretization

**Status:** released-code observation. Not a biological claim.  
**Date:** 2026-08-15.

## 0. A small but clarifying fact

The four complete released FCI examples are discretized to roughly the same number of dendritic segments (~1040).

For every dendritic segment, `create_synapses()` creates:

```text
one excitatory AMPA+NMDA point process
one inhibitory GABAA/B point process
```

The excitatory `AMPANMDA_EMS` mechanism contains four conductance state variables:

```text
A_AMPA
B_AMPA
A_NMDA
B_NMDA
```

The inhibitory `GABAAB_EMS` mechanism contains four analogous state variables, although the released parameter sets use `GABAB_ratio = 0`, so the GABAB branch is inactive under the standard conditions.

Each cable segment also carries membrane voltage state.

Therefore the released model does **not** give the larger human trees an arbitrarily larger number of explicit local synaptic state machines.

It gives the cells roughly similar counts of local dynamical elements and changes the physical geometry/coupling represented by those elements.

---

## 1. Why this is useful for the “geometry” question

Under the common-rat-synapse condition, a crude schematic is

```text
same kind of local synaptic kernel at each segment
same approximate number of segment-level dynamical units
same passive membrane time constant

but

different lengths / diameters / branching / path relationships
and therefore different electrical coupling among those states.
```

That makes the FCI comparison closer to

```text
same local primitives
+ different coupling geometry
```

than to

```text
human model simply contains many more simulated units.
```

This does **not** prove that FCI measures geometry cleanly, because receiver scaling, segment physical size, source aggregation and other model choices still vary.

But it narrows the interpretation.

---

## 2. The same fact creates the discretization problem

Keeping the count near ~1040 requires different physical segment scales.

So the controlled state count is bought by changing

```text
how much physical dendrite one local state machine represents.
```

This is exactly why `DISCRETIZATION_NMDA_GATE.md` matters.

Two legitimate numerical comparison strategies now exist:

```text
A. matched state/channel count
    approximately the published FCI design

B. matched physical resolution
    same maximum segment length / electrotonic criterion across cells
```

If the species/layer ranking is stable under both, confidence rises.

If it changes, the question becomes whether the difference comes from cable discretization, synaptic co-location, or the TCN input representation.

---

## 3. A dynamical-systems way to say it

A linearized discretized cell can be written schematically as

```text
dx/dt = A x + B u
```

where `x` contains local membrane and synaptic states.

If two models have similar state dimension but different `A`, their behavior can still differ enormously because the **coupling operator** differs.

That is ordinary systems theory.

For Dig, this is preferable to saying vaguely that “the human neuron has more geometry.”

The sharper question is:

> **what changes in the coupling operator when the same class and approximate number of local stateful elements is embedded in a different morphology?**

---

## Source-code anchors

- `ido4848/FCI/simulating_neurons/neuron_models/model_utils.py` — one excitatory and one inhibitory point process per dendritic segment.
- `AMPANMDA_EMS.mod` — four AMPA/NMDA conductance state variables.
- `GABAAB_EMS.mod` — four GABA conductance state variables; standard `GABAB_ratio = 0`.
- released wrapper/properties files — approximately matched segment counts but morphology-specific physical segment lengths.

## Current sentence

> **In the released FCI representation, the headline morphology comparison is not simply “more human compartments equals more complexity.” It is closer to the same number of local dynamical primitives coupled through different physical trees — with the important caveat that equalizing state count changes the physical scale represented by each primitive.**
