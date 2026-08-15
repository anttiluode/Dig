# Retina receiver gate: when the soma is the wrong answer to “what does the neuron compute?”

**Status:** primary-literature collision + open-model experiment. Not a result.  
**Date:** 2026-08-15.

## 0. Why the retina is unusually useful for Dig

Aizenbud FCI and TwinProp both look inside a complicated neuron but eventually judge it at a privileged scalar output:

```text
many dendritic inputs
       -> complicated internal dynamics
       -> soma / axon
       -> spike decision
```

That is a sensible question for cortical pyramidal cells.

It is not a universal definition of neuronal computation.

The mammalian starburst amacrine cell (SAC) is an unusually clean counterexample because it is **axonless** and its output synapses live on distal dendrites. Different dendritic sectors of the same cell can carry different direction-selective outputs.

Euler, Detwiler & Denk (Nature 2002) found the critical receiver dependence directly:

```text
local dendritic Ca signal      direction selective
somatic membrane voltage       not direction selective
```

So choosing the soma as the receiver can erase the computation that the cell is biologically used for.

This is not a philosophical objection to point neurons. It is an experimentally established case in which the relevant function is spatially distributed across one cell.

---

## 1. Replace one receiver with a receiver set

The current Dig notation often uses

```text
h[r <- i](t)
```

for one source `i` and one receiver `r`.

For a cell with multiple functional output sites, use a receiver set

```text
R = {r_1, r_2, ..., r_M}
```

and construct

```text
H_R<-S(t)
```

whose entries are source-to-receiver responses.

Then the same physical cell can look very different under different projections:

```text
soma projection:
    y_soma(t)

one local dendritic output:
    y_r(t)

all local outputs:
    Y_R(t) = [y_r1(t), ..., y_rM(t)]
```

A scalar soma trace is a projection of the internal dynamics, not automatically the complete output of the biological unit.

---

## 2. “Receiver collapse” is directly testable

Define the qualitative phenomenon before inventing any metric:

> **receiver collapse:** a biologically relevant distinction is present in local/output-site signals but weak or absent after projecting the same cell onto one privileged receiver.

For SAC direction selectivity, the literature already gives a ground-truth example.

A minimal experiment is therefore:

```text
same visual input
same cell

readout A: soma voltage
readout B: distal dendritic voltage / Ca
readout C: local transmitter-release proxy
```

For each receiver measure ordinary direction selectivity and, separately, the difficulty of emulating its input-output map with the same fixed surrogate architecture.

Do not assume that direction selectivity and emulation difficulty are the same quantity.

The important question is whether a scalar receiver systematically hides computations that remain obvious in the distributed outputs.

---

## 3. The 2024 SAC result is even closer to the Dig language

A 2024 Nature Communications study using subcellular voltage and calcium imaging found a striking division of labor:

```text
perisomatic region
    integrates motion over much of the dendritic field
    -> slower / low-pass global depolarization

local dendrite
    receives local synaptic drive
    + the global depolarization
    -> direction-selective local suprathreshold Ca event
```

This is almost a textbook example of

```text
recent distributed state
      + local present input
      -> local receiver-specific event
```

The soma is not merely the final answer. It can act as part of a **global context signal** that is fed back into local dendritic computations.

That is much closer to a “wide present” mechanism than a metaphysical present: a slowly varying global state overlaps in time with a local arriving input and changes what that local branch can do.

---

## 4. A second retina result: time constants can be painted onto geometry

Kim et al. / related SAC work and the 2022 eLife study of glutamatergic input kinetics found that bipolar-cell input dynamics vary along SAC dendrites.

In the 2022 study, proximal glutamate signals were more sustained while distal signals were more transient. A compartmental model showed that this spatial organization of input kinetics contributes to direction selectivity for some stimulus regimes.

That gives a concrete form to the phrase “time as geometry”:

```text
location i
    -> transfer path h_i(t)
    -> local synaptic kernel g_i(t)
```

The temporal kernel is not uniform across space.

The object is not just a tree with weights. It is a tree carrying a **field of local temporal kernels**.

---

## 5. This creates a clean shuffle experiment

Suppose a morphology has a fixed multiset of synaptic temporal kernels

```text
{g_1(t), g_2(t), ..., g_K(t)}.
```

Compare two conditions while preserving every marginal quantity:

```text
STRUCTURED
    assign kernels to their native / designed spatial locations

SHUFFLED
    randomly permute the exact same kernels across locations
```

Hold fixed:

```text
morphology
number of synapses
input spike/event trains
conductance distribution
the multiset of kinetic kernels
receiver set
```

Only the **correlation between spatial address and temporal kernel** changes.

In the linear limit,

```text
v_r(t) = sum_i h[r <- i](t) * g_i(t) * x_i(t)
```

so the shuffle tests whether the pairing between `h_i` and `g_i` matters.

With local nonlinearities, the same manipulation additionally changes where and when nonlinear operating states are reached.

This is a sharper test of “geometry + time” than adding another morphology scalar.

---

## 6. Why this matters for Aizenbud

The released Aizenbud FCI models assign one species-specific excitatory synapse parameter set uniformly across the dendritic tree.

So within a condition,

```text
g_i(t) = common species kernel
```

apart from event amplitudes / histories.

That is excellent for isolating morphology.

It also means the published FCI experiment does **not** test the additional resource seen in SACs:

```text
spatially structured heterogeneity of temporal kernels.
```

A synthetic cortical follow-up could add two matched kernel types to the exact same morphology and compare structured versus shuffled placement. This would test a principle, not claim that cortical pyramidal cells use the same SAC arrangement.

Start AMPA-only so the effect is not immediately confounded by NMDA feedback.

---

## 7. The synapse is not merely a narrow choke point

The phrase “the cleft is tiny, therefore all the information has to be carried in time” is too strong.

Ribbon synapses in retinal bipolar cells are a useful correction.

They are driven by graded presynaptic voltage rather than an all-or-none presynaptic spike, and experiments show that they can encode visual contrast through both the **frequency and amplitude** of release events.

Their vesicle pools also have state: depletion and replenishment create history dependence. Oesch & Diamond (Nature Neuroscience 2011) showed that depletion of the readily releasable pool helps a rod bipolar ribbon synapse compute temporal contrast while sustained release carries luminance information.

So a better abstraction is:

```text
synapse = local stateful transducer
```

not

```text
synapse = passive choke that forces a pure time code.
```

The synapse can itself implement filtering, gain control, adaptation and stochastic recoding.

---

## 8. An open model is already available for the receiver test

The model repository released with the 2022 SAC spatiotemporal-input paper is:

```text
geoffder/spatiotemporal-starburst-model
```

Its `sac_pair.py` is almost tailor-made for a first Dig experiment.

It constructs an axonless SAC-like soma + dendrite + terminal model with spatially separated bipolar inputs and different sustained/transient kinetics. The runner explicitly records at both:

```text
soma:
    voltage
    Ca current
    Ca concentration

terminal:
    voltage
    Ca current
    Ca concentration
```

and it has moving-bar direction/velocity sweeps plus conditions that homogenize sustained/transient inputs.

Therefore the first retina gate does not require building a new simulator.

---

## 9. Gate R0 — reproduce the receiver split before inventing anything

Using the authors' model and parameterization:

```text
R0a  run the published/native motion conditions

R0b  quantify direction selectivity at
     soma voltage
     terminal voltage
     terminal calcium

R0c  verify that receiver choice changes the functional signal
```

If the model does not reproduce the expected local-vs-global distinction under the authors' conditions, stop and debug rather than inventing a new complexity measure.

---

## 10. Gate R1 — structured time field versus shuffle

Once R0 works:

```text
native spatial kinetic arrangement
vs
permuted kinetic-to-location assignment
vs
all-fast / all-transient
vs
all-slow / all-sustained
```

Preserve input count and total conductance budget.

Measure at the same receiver set.

This asks:

> does the geometry become more computationally useful when different spatial addresses carry different temporal kernels?

That is one of the cleanest empirical descendants yet of the original “time as geometry” intuition.

---

## 11. Gate R2 — FCI-like receiver dependence

Only after R0/R1:

Train the **same constrained surrogate family** separately to predict

```text
soma voltage
terminal voltage
terminal calcium / release proxy
all receivers jointly
```

Then ask whether emulation difficulty is receiver-dependent and whether the multi-output map contains functionally important distinctions invisible at the soma.

Do not call this “FCI” without qualification because published FCI is defined from spike-prediction AUC in spiking cortical models.

Call it a receiver-dependent emulation test until the metric is specified.

---

## Primary-source anchors

- Euler, Detwiler & Denk (2002), *Nature*, DOI `10.1038/nature00931` — individual SAC dendritic branches act as independent direction-selective computational modules; dendritic Ca but not somatic voltage is direction selective.
- Wang et al. (2024), *Nature Communications*, DOI `10.1038/s41467-024-46234-7` — perisomatic global low-pass signal + local dendritic coincidence / suprathreshold Ca computation; axonless SAC with distal dendritic outputs.
- Kim et al. / Gaynes et al. (2022), *eLife* 11:e81533, DOI `10.7554/eLife.81533` — spatially varying bipolar input kinetics; proximal sustained versus distal transient components contribute to SAC direction selectivity.
- Oesch & Diamond (2011), *Nature Neuroscience*, DOI `10.1038/nn.2945` — ribbon-synapse vesicle depletion computes temporal contrast while sustained release encodes luminance.
- James et al. (2019), *Nature Neuroscience*, DOI `10.1038/s41593-019-0403-6` — retinal bipolar ribbon synapses encode contrast using both release-event frequency and amplitude.
- `geoffder/spatiotemporal-starburst-model` — open NEURON model from the 2022 eLife work; records soma and terminal voltage/Ca and exposes spatial input-kinetic manipulations.

## Current sentence

> **The soma is a receiver, not a universal definition of the neuron. In an axonless starburst cell, local dendritic receivers carry computations that disappear at the soma. The retina therefore gives Dig a ground-truth test of receiver-relative complexity, and its spatially structured input kinetics give a literal experiment in putting different temporal kernels at different geometric addresses.**
