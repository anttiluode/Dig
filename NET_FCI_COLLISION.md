# Prior-art collision: NET already has the geometry; the open question is what FCI is measuring

**Status:** literature correction / sharper hypothesis.  
**Date:** 2026-08-15.

The first Green-function dig was useful, but the literature immediately removes several tempting novelty claims. That is good. It leaves a smaller and much more interesting external test.

## 1. What is already known — do not claim it

### Green functions and transfer kernels on dendritic trees

Wybo, Stiefel & Torben-Nielsen (2013), arXiv:1309.2382, already use Green's functions to encode the dendritic cable response between input and receiver locations. Wybo et al. (2015), arXiv:1504.03746, give a sparse tree-graph reformulation and exponential kernel expansion.

So these are established objects:

```text
location i -> location j transfer impedance Z_ij(omega)
location i -> location j impulse-response kernel z_ij(t)
```

They are not a new "time geometry" formalism.

### Electrical geometry / functional compartments

Wybo et al. (Cell Reports 2019), *Electrical Compartmentalization in Neurons*, goes much further. It builds the **Neural Evaluation Tree (NET)** from the dendritic impedance matrix and uses its topology to identify electrically independent functional subunits.

It defines the impedance-based independence index for two approximately symmetric regions as

```text
I_Z = (Z_1 + Z_2) / (2 Z_12) - 1
```

where `Z_1,Z_2` are input impedances and `Z_12` is transfer impedance. The paper finds that compartmentalization is **dynamic**: balanced input and shunting inhibition can alter the impedance-derived topology and the number/size of functional subunits.

Therefore these claims are prior art:

```text
impedance defines an effective dendritic geometry
that geometry reveals functional subunits
current synaptic state can re-compartmentalize the same anatomy
```

This is already remarkably close to the disciplined version of our `effectome` / state-dependent-causal-geometry language. We should cite it, not rename it.

The current NEAT software exposes this machinery directly: `SOVTree.construct_net`, `NET.calc_i_z_matrix`, and `NET.calc_compartmentalization`.

### An older "functional complexity index" already exists in this exact human-neuron lineage

This is the most important collision.

Eyal et al. (Frontiers in Cellular Neuroscience 2018), *Human Cortical Pyramidal Neurons: From Spines to Spikes via Models*, explicitly proposed a functional-complexity index based on the **maximal number of independent simultaneous NMDA spikes** a modeled neuron could support.

Crucially, independence was not equated with raw branch count. They used cable interaction/transfer resistance between dendritic regions. Their human L2/3 models supported about `24.8 +/- 4.4` simultaneous independent NMDA spikes versus about `13.7 +/- 2.1` for rat L2/3 models.

Aizenbud et al. 2026 cite this result and motivate their new deep-learning FCI partly by the same independent-subunit literature.

Therefore we must not claim:

```text
"we discovered that electrical independence determines dendritic complexity"
```

or

```text
"we discovered a complexity index based on independent nonlinear subunits"
```

Both are already in the lineage.

## 2. The question that survives

Aizenbud 2026 changes the definition of complexity.

The new FCI is not the 2018 count of independent NMDA subunits. It is the difficulty a **fixed temporal convolutional network** has in reproducing the detailed neuron's input/output transformation.

The 2026 paper shows that:

```text
morphology matters under common synapses
+ NMDA conductance/nonlinearity adds more complexity
```

and its morphology analysis uses conventional structural descriptors such as dendritic area, path/branch length and branch allocation.

The paper discusses electrical compartmentalization as a likely mechanism, but in the main paper it does not report a direct comparison between FCI and an impedance/NET-derived functional-compartment metric.

I have not yet found a paper that performs this exact comparison.

So the surviving question is:

> **Is Aizenbud's deep-learning FCI partly measuring the same cable-theoretic functional compartmentalization that Eyal 2018 and Wybo 2019 measured directly?**

That is a much better question than inventing a new geometry.

## 3. A sharper mechanistic decomposition

Do not assume additivity, but test two interventions separately.

### Morphology arm

Use the **common-rat-synapse FCI** from Aizenbud SI Fig. S5, where synaptic type is held fixed across morphologies.

For each morphology derive, before seeing the FCI target:

```text
A. ordinary structural baseline
   total dendritic area
   max/long bifurcation path or closest preregistered analogue

B. electrical/NET descriptors
   distribution of input/transfer resistances
   distribution or matrix of I_Z between matched dendritic sites
   maximal NET compartment count at one preregistered I_Z threshold
```

Then ask whether `B` adds held-out predictive value beyond `A`.

This is the core external gate.

### Nonlinearity arm

Green/impedance quantities are linear or linearized. They cannot by themselves explain NMDA's nonlinear expansion.

Use the passive/linear NET as the baseline geometry, then activate matched synaptic clusters in the released NEURON models and ask whether morphology's NET structure predicts:

```text
which clusters generate local NMDA spikes
which simultaneous spikes remain independent
where multi-site responses depart from linear superposition
```

Then compare those mechanistic quantities with the FCI change produced by synaptic interventions.

The question becomes whether the deep-learning FCI can be decomposed mechanistically into:

```text
morphology -> electrical compartmentalization / interaction structure
synaptic state -> nonlinear expansion or collapse of the available subunits
```

This is a hypothesis. FCI is nonlinear and architecture-dependent, so do not literally subtract these terms and call the residual a causal contribution without an intervention-based test.

## 4. One important correction to the first kernel-rank idea

A transfer-kernel dictionary is still worth plotting, but **effective rank of soma kernels is not automatically a lower bound on Aizenbud TCN complexity**.

The released FCI surrogate uses a first causal `Conv1d` layer with separate learned temporal weights for every input channel. With the current defaults:

```text
depth = 3
width = 128
first kernel = 54 ms
later kernels = 12 ms
```

so the nominal causal receptive field is about

```text
54 + 2*(12-1) = 76 ms.
```

A large family of passive source-to-soma kernels may still be represented efficiently by that architecture. Therefore `rank(H)` by itself is too loose a candidate explanation for FCI.

The **full intra-dendritic impedance/NET structure** is more promising because FCI's strongest biological nonlinearity arises from local NMDA interactions. The relevant complexity may live in which inputs can cooperate independently, not merely in how many distinct linear waveforms reach the soma.

A useful secondary diagnostic is nevertheless to test how much passive kernel energy or discriminative structure lies beyond the TCN's nominal ~76 ms receptive field. Do not predict the sign in advance.

## 5. The experiment I now want to run

### G0 — implementation sanity, exact author-released four

Use the four complete morphology/model folders currently exposed in `ido4848/FCI` only to validate the pipeline:

```text
rat L2
rat L5
human L2/3
human L5
```

No species statistics from n=4.

Run both:

```text
CODE_EXACT
  released FCI passive implementation

PAPER_NOMINAL
  Cm=1 uF/cm2, Rm=20k ohm cm2, Ra=150 ohm cm
```

because the common released HOC implementation uses doubled dendritic `cm` and leak relative to soma while the paper states common passive values. Do not guess why; test sensitivity.

### G1 — matched electrical atlas

At a frozen, equal number of locations per morphology:

```text
Z(0)              steady resistance matrix
Z(omega)          selected frequency-dependent matrices
z(t)              selected impulse-response kernels
I_Z               pairwise independence matrix
NET                impedance hierarchy
C_NET(theta)       compartment count at fixed independence threshold theta
```

The 2019 paper reports `I_Z >= ~10` as an empirically useful independence regime in its tested settings. For our confirmatory analysis, choose a threshold from prior literature **before** viewing FCI correlations, and include threshold sensitivity as secondary analysis rather than optimizing it on FCI.

### G2 — ordinary-geometry kill test

Before touching FCI, determine how much of the NET/electrical descriptors is already explained by:

```text
area
path distance
branch allocation
local diameter / electrotonic distance
```

If the electrical descriptors collapse almost deterministically onto these quantities in this panel, there may be no new mechanism to explain.

### G3 — common-synapse FCI gate

Primary model comparison:

```text
B2:       area + path/branch-allocation baseline
B2+NET:   B2 + a tiny preregistered set of electrical descriptors
```

Use leave-one-cell-out / strict cross-validation, report MAE as well as R2, and perform label-shuffle/permutation controls. No feature fishing on 16 cells.

The resolved 16-cell V22 panel is exploratory because eight exact mappings remain unresolved. The real confirmatory panel remains blocked until provenance is complete or the authors supply the missing mappings/data.

### G4 — 2018-index bridge

Where the models permit it, reproduce the Eyal-style maximal independent-NMDA-subunit count or a faithful automated version of it.

Then directly compare three notions:

```text
structural morphology complexity
Eyal-style cable/nonlinear subunit complexity
Aizenbud deep-learning FCI
```

This is the experiment that now interests me most.

If FCI tracks the old mechanistic index after size/path controls, we learn **what the DNN-based complexity measure is physically seeing**.

If it does not, that is equally interesting: the new FCI contains a different kind of I/O difficulty than independent-subunit count.

## 6. Why this is a better Dig result

The noise led into a region that already has names:

```text
Green function
transfer impedance
Neural Evaluation Tree
impedance-based independence index
functional dendritic subunit
```

That does not make the path a failure. It gives us mature mathematics, code and experimental validation instead of a home-made vocabulary.

The remaining candidate contribution is now small enough to test:

> **Connect an externally defined, deep-learning-based neuron complexity measure (Aizenbud FCI) to an established electrical-mechanistic description of dendritic functional subunits (transfer impedance / NET / Eyal-style independent NMDA events), under controls that already killed V22's crude global spectral features.**

If that link exists, it is useful because it turns an opaque surrogate-model score into a mechanistic cable-theory explanation.

If it does not, write the null down and keep digging.

## Primary sources

- Wybo W.A.M., Stiefel K.M., Torben-Nielsen B. (2013). *The Green's function formalism as a bridge between single and multi-compartmental modeling*. arXiv:1309.2382.
- Wybo W.A.M. et al. (2015). *A sparse reformulation of the Green's function formalism allows efficient simulations of partial differential equations on tree graphs*. arXiv:1504.03746.
- Eyal G. et al. (2018). *Human Cortical Pyramidal Neurons: From Spines to Spikes via Models*. Frontiers in Cellular Neuroscience 12:181. DOI 10.3389/fncel.2018.00181.
- Wybo W.A.M. et al. (2019). *Electrical Compartmentalization in Neurons*. Cell Reports 26:1759-1773.e7. DOI 10.1016/j.celrep.2019.01.074.
- Wybo W.A.M. et al. (2021). *Data-driven reduction of dendritic morphologies with preserved dendro-somatic responses*. eLife 10:e60936. DOI 10.7554/eLife.60936.
- Cuntz H. et al. (2021). *A general principle of dendritic constancy: A neuron's size- and shape-invariant excitability*. Neuron 109:3647-3662.e7. DOI 10.1016/j.neuron.2021.08.028.
- Aizenbud I. et al. (2026). *Dendritic morphology and synaptic nonlinearities enhance functional complexity in human cortical neurons*. PNAS 123:e2533168123. DOI 10.1073/pnas.2533168123.
- Wybo W.A.M. (2026). *The Neural Analysis Toolkit Unifies Semi-Analytical Techniques to Simplify, Understand, and Simulate Dendrites*. Neuroinformatics 24:21. DOI 10.1007/s12021-025-09766-x.
