# Extracellular side dig: where the “different material, different oscillation” intuition survives

**Status:** side branch / literature-grounded screening plan. Not an explanation of FCI.  
**Date:** 2026-08-15.

## 0. Translate the intuition before testing it

The naive picture was:

> electricity travels through membrane / fluid / different material, so perhaps each material has its own oscillation and morphology interacts with that.

For the Aizenbud models, that is not the clean physical description.

A better translation is:

> **the same transmembrane current participates in several electrical domains whose transfer impedances have different spatial and frequency dependence.**

In the standard single-neuron cable model:

```text
intracellular axial medium -> resistive cable path
membrane                  -> capacitance + leak + voltage/synapse dynamics
extracellular potential   -> effectively fixed reference unless modeled explicitly
```

The strong biological frequency dependence in Aizenbud therefore already comes from membrane capacitance, synaptic kinetics and voltage-dependent conductances.

A separate frequency-dependent “CSF resonance” is not needed and is not what their model contains.

The local extracellular environment of a dendrite is interstitial/extracellular space, not literally a dendrite suspended in a ventricle full of CSF.

---

## 1. What the released FCI neuron omits

The released FCI HOC inserts passive membrane into dendrites and active spike conductances into soma/axon. It does not insert NEURON's `extracellular` mechanism or otherwise solve a nonuniform extracellular potential.

So the modeled transmembrane voltage is effectively calculated relative to a common extracellular reference.

That is a standard cable-model assumption, not a hidden error.

NEURON can solve nonzero extracellular potentials when the `extracellular` mechanism is inserted, but the FCI model does not use that machinery.

Thus the present FCI question is an **intracellular/cable + membrane** computation question.

---

## 2. Forward field is not the same as feedback

A neuron with morphology generates extracellular voltage because its transmembrane currents form spatial sinks and sources.

Morphology therefore absolutely matters to the extracellular field observed around a cell.

But this alone does not alter the FCI computation.

There are two arrows:

```text
A. intracellular/membrane currents
      -> extracellular potential

B. extracellular potential
      -> change in transmembrane voltage
      -> changed neuron dynamics
```

Standard extracellular/LFP forward models often compute A after the neuron simulation.

To change FCI, we need B as well: **ephaptic feedback** or some imposed extracellular field.

Do not mistake a morphology-dependent extracellular recording for a morphology-dependent computational feedback effect.

---

## 3. Ephaptic feedback is real but usually small for one cortical neuron

Anastassiou et al. (Nature Neuroscience 2011, DOI `10.1038/nn.2727`) measured physiological extracellular-field effects on cortical pyramidal neurons. Subthreshold somatic changes were less than about 0.5 mV, although slow fields below ~8 Hz could strongly influence spike timing/entrainment.

Goldwyn & Rinzel's cable framework (J Neurophysiol 2016, PMID 26823512) likewise shows that endogenous extracellular coupling can perturb nearby cables and depends strongly on extracellular resistance and packing geometry.

So the effect is not zero.

But for an isolated single-cell comparison it should be treated as a **second-order extension until its magnitude is demonstrated**. Population alignment, synchrony and tight packing can amplify ephaptic fields far beyond the field from one isolated dendritic event.

This makes extracellular feedback more naturally a bridge from single-cell morphology to network context than the first explanation of the Aizenbud species FCI gap.

---

## 4. Do not hang the branch on “the fluid has a resonance”

Measurements of extracellular/tissue impedance remain nuanced.

Two important primary results point in different-looking directions because they probe different geometries:

- Logothetis et al. (Neuron 2007, DOI `10.1016/j.neuron.2007.07.027`) found in-vivo cortical gray-matter impedance essentially frequency-independent and well described by a purely resistive conductor.
- Miceli et al. (eNeuro 2017, DOI `10.1523/ENEURO.0291-16.2016`) found at most weak frequency dependence from 5--500 Hz at microscopic physiological scales.
- Bédard et al. (Biophysical Journal 2022, PMID 35182541) found strong frequency dependence when current traversed cell membranes and argued that membrane-associated ionic/Debye-layer effects contribute importantly to measured tissue impedance.

These are not interchangeable experiments.

For Dig, the safe move is:

```text
do not assume a special extracellular oscillation band;
measure or bracket the transfer impedance appropriate to the model.
```

The membrane/synapse dynamics are the first-order spectral structure we already know is present.

---

## 5. Does extracellular space break the tree?

Yes in principle, but phrase it carefully.

A pure dendritic cable has a tree topology: current between dendritic locations follows intracellular branches and the membrane leak paths represented by the cable operator.

A nonuniform shared extracellular potential introduces an additional spatial field. Two dendritic pieces that are far apart along the tree but physically close in 3D can experience related extracellular voltage.

That means the fully coupled intracellular-membrane-extracellular system is no longer described by the intracellular tree alone.

Modern fully coupled EMI formulations explicitly solve these domains together; a 2026 finite-element EMI study (Jæger & Tveito, *Frontiers in Computational Neuroscience*, DOI `10.3389/fncom.2026.1755548`) emphasizes that conventional approaches often decouple extracellular field and membrane/intracellular dynamics.

But this does **not** justify the stronger sentence:

> “the NET-independent pairs are exactly the pairs most strongly ephaptically coupled.”

Tree-far / Euclidean-near pairs are only **candidates**. Actual coupling also depends on transmembrane source strength, conductivity, orientation, boundaries, packing and activity in surrounding cells.

---

## 6. A cheap morphology-only screening map is still useful

For each released morphology, compare pairs of dendritic locations using two coordinates:

```text
D_tree(i,j)   = cable/path/electrical separation
D_xyz(i,j)    = Euclidean 3D separation
```

Flag pairs satisfying something like

```text
large D_tree
small D_xyz
```

or, better, use impedance-derived electrical separation instead of raw path length once NEAT is running.

This yields a **shortcut-candidate map**:

> places that the intracellular tree regards as far apart but that share nearby extracellular space.

Do not interpret the count as ephaptic coupling strength.

It is only a queue of pairs worth testing in a field model.

A species difference in this map would show that the *opportunity* for non-tree coupling is morphology-dependent. It would still not show that it changes FCI.

---

## 7. The actual next extracellular experiment

If the geometry screen is interesting, use the detailed simulation's transmembrane currents to compute a forward extracellular field with a standard volume-conductor/line-source method.

For the exact same input event measure at the candidate partner branch:

```text
V_e(t)
```

and compare it to the intracellular/local membrane response.

Gate:

```text
if |V_e| is tiny relative to the voltage scale needed to alter NMDA recruitment,
stop the branch.
```

Only if the forward field is large enough should it be fed back through an extracellular/EMI model and the local NMDA / spike response rerun.

This keeps the expensive self-consistent problem behind a magnitude test.

---

## 8. There is one place the extracellular thought may intersect FCI more directly: slow state bias

The strongest cortical ephaptic sensitivity reported by Anastassiou et al. was for slow extracellular fluctuations.

A small slow bias can alter the operating voltage at a dendritic site. In our Green/NMDA language that changes

```text
K(v*)
```

because the NMDA Mg-block slope is voltage dependent.

So an extracellular field does not need to carry a new high-frequency resonance to matter. It can simply shift the operating point and thereby change local nonlinear susceptibility.

That gives a cleaner hypothesis:

```text
external/collective field
      -> small local voltage bias
      -> changed K(v*)
      -> changed ZK susceptibility
      -> changed probability of local regenerative events
```

This is still speculative for the Aizenbud isolated-cell comparison, but it is mechanistically testable.

---

## 9. Relation to the rho-scaled receiver

Aizenbud explicitly rescales somatic and axonal Na/K conductances by the dendritic electrical load (`rho_soma`, `rho_axon`). The four released examples differ substantially, with human L2/3 having particularly large `rho_axon`.

This is a deliberate normalization of spike-generation load, described in the paper.

It also means a forward extracellular **action-potential** field comparison cannot be interpreted as dendritic morphology alone: the receiver/spike generator has been rescaled across cells.

If extracellular spike fields are ever compared, separate

```text
subthreshold dendritic field
from
spike/AIS field.
```

The axon initial segment can dominate the extracellular action-potential landscape, so these are different source regimes.

---

## 10. Priority

This branch is scientifically real but currently lower priority than:

```text
1. FCI segmentation/contact-aggregation convergence
2. AMPA-only vs common-NMDA intervention
3. direct validation of Green/NMDA susceptibility
4. FCI/capacity bridge
```

Extracellular feedback moves up only if a cheap forward-field calculation says the magnitude is large enough to matter.

## Primary anchors

- Anastassiou et al. 2011, *Nature Neuroscience*, DOI `10.1038/nn.2727` — measured cortical ephaptic coupling.
- Goldwyn & Rinzel 2016, *Journal of Neurophysiology*, PMID `26823512` — cable theory with endogenous extracellular feedback.
- Logothetis et al. 2007, *Neuron*, DOI `10.1016/j.neuron.2007.07.027` — in-vivo cortical impedance approximately resistive.
- Miceli et al. 2017, *eNeuro*, DOI `10.1523/ENEURO.0291-16.2016` — weak microscopic frequency dependence 5--500 Hz.
- Bédard et al. 2022, *Biophysical Journal*, PMID `35182541` — membrane-crossing current and frequency-dependent tissue impedance.
- Jæger & Tveito 2026, *Frontiers in Computational Neuroscience*, DOI `10.3389/fncom.2026.1755548` — fully coupled extracellular-membrane-intracellular modeling.
- NEURON documentation for `extracellular` — nonzero `vext` must be represented explicitly.

## Current sentence

> **The useful descendant of “different material, different oscillation” is not a CSF resonance story. It is a multi-domain transfer problem: membrane dynamics provide strong frequency dependence, morphology shapes both intracellular and extracellular fields, and ephaptic feedback can add a non-tree coupling route. First measure its magnitude; only then let it into the FCI mechanism story.**
