# Dendro-plexing closes the Green-function loop — and exposes a TwinProp ablation gap

**Status:** primary-literature synthesis + proposed experiment. Not a result.  
**Date:** 2026-08-15.

## 0. The surprise

The passive Green-function direction is not merely plausible. A peer-reviewed 2026 paper from the same Segev/London/Beniaguev research line has already demonstrated a closely related mechanism directly:

> D. Beniaguev, S. Shapira, I. Segev, M. London, **“Dendro-plexing of Single Input Spikes via Multiple Synaptic Contacts Can Enhance Cortical Neuron Computation and Reduce Axonal Wiring”**, *Journal of Neuroscience* 46(17), 2026. DOI: `10.1523/JNEUROSCI.0839-24.2026`.

The central observation is cable-theoretic:

- proximal dendritic contacts generate relatively brief somatic PSPs;
- distal contacts generate broader somatic PSPs;
- therefore one presynaptic spike, when the same axon makes several contacts at different dendritic locations, arrives at the soma as a **mixture of several temporal filters**.

They call this **dendro-plexing** and build a Filter-and-Fire (F&F) model from it. In their reported tasks, the F&F neuron has about a threefold larger memory capacity than an ordinary integrate-and-fire model and can learn spatiotemporal tasks where the I&F model fails.

This means that the object we were about to call a morphology-defined local Green-kernel dictionary already has a very concrete computational incarnation in current neuroscience.

Do not claim discovery of the principle.

What is interesting is its relation to FCI and TwinProp.

---

## 1. Passive morphology is a learnable temporal filter dictionary

Let `h_i(t)` be the passive source-to-soma impulse response from dendritic location `i`.

For presynaptic axon `a` with contacts `c=1...m_a` at dendritic locations `i_ac`, with contact strengths `w_ac`, the effective somatic filter for that axon is

```text
g_a(t) = sum_c w_ac * h_iac(t)
```

and the passive somatic response is

```text
v_soma(t) = sum_a (g_a * x_a)(t)
```

where `x_a(t)` is the presynaptic spike train.

So a multiple-contact axon is not only a scalar weight.

It is a **learned temporal filter assembled from morphology-defined Green kernels**.

Changing contact strengths changes the mixture coefficients. Changing dendritic contact locations changes which basis filters are available in the mixture.

This gives a clean interpretation of structural plasticity in the passive limit:

```text
morphology        -> filter dictionary {h_i}
contact location  -> basis selection
contact strength  -> basis coefficient
axon              -> composite temporal filter g_a
```

No nonlinear dendritic event is required for this level of computation.

---

## 2. TwinProp already contains dendro-plexing in its optimization space

Aizenbud et al. 2026, **“What can a neuron compute?”**, allow on average about **20 synaptic contacts per input axon**, distributed across apical and basal dendrites. Synaptic strengths and dendritic locations are optimized. For abstract tasks, total synaptic contact count is held at roughly **8,000** (4,000 excitatory and 4,000 inhibitory).

Therefore a TwinProp solution can exploit at least three distinct mechanisms simultaneously:

```text
A. passive multi-contact temporal filtering       [dendro-plexing]
B. local voltage-dependent NMDA nonlinearity
C. voltage-gated active dendritic dynamics
```

The present TwinProp mechanism analysis strongly establishes that B and C matter for hard parity tasks, but its published ablations do **not** isolate A cleanly.

That is the opening.

---

## 3. The missing condition

TwinProp reports four relevant 4-bit parity models:

```text
intact L5PC                        ~99.4%
passive dendrites, NMDA retained   ~78.1%
soma-only, channels + NMDA kept   ~76.9%
no NMDA, active dendrites kept     ~73.8%
LIF                                ~68.8%
```

The crucial absent morphology-preserving condition is:

```text
FULL MORPHOLOGY
+ passive dendritic membrane
+ AMPA/GABAA
- NMDA
- dendritic voltage-gated channels
```

Call it `M+ N- V-`.

That condition is the **pure cable / Green / dendro-plexing gate**.

Without it, the existing ablation set cannot answer:

> How much of TwinProp's computational gain comes from multiple-contact morphology-defined temporal filtering before local dendritic nonlinearities are added?

The recent JNeurosci F&F result gives a strong reason to measure this rather than assuming it is small.

---

## 4. Run the full factorial, not another one-off ablation

Define three binary factors:

```text
M = full dendritic morphology / matched collapsed control
N = NMDA on / off
V = dendritic voltage-gated conductances on / off
```

The full 2 x 2 x 2 design is:

```text
M- N- V-    matched point/collapsed passive baseline
M- N+ V-    collapsed + NMDA
M- N- V+    collapsed + active channels
M- N+ V+    collapsed + both nonlinear mechanisms

M+ N- V-    PURE DENDRO-PLEXING / GREEN condition
M+ N+ V-    morphology + NMDA
M+ N- V+    morphology + active channels
M+ N+ V+    intact detailed neuron
```

The collapsed controls should preserve as much as possible of:

- total contact count;
- input axon identities;
- decision rule;
- somatic resting potential;
- input resistance / membrane time constant;
- total admissible conductance budget.

Otherwise `M` becomes a mixture of morphology and trivial gain/resource changes.

For each cell/task, fit a factorial model or use explicit contrasts rather than reading mechanism from adjacent bars:

```text
main effects: M, N, V
pair interactions: MxN, MxV, NxV
three-way interaction: MxNxV
```

The three-way term asks whether full morphology creates extra capacity specifically when **both** nonlinear mechanisms are available.

---

## 5. Separate strength learning from address learning

TwinProp optimizes both strength and dendritic location. That is biologically interesting, but it mixes two resources.

For every factorial condition run two optimization regimes:

```text
W-only
    freeze a matched contact-location assignment
    optimize conductance strengths only

W+LOC
    optimize strengths and dendritic locations
```

Define

```text
Delta_address = capacity(W+LOC) - capacity(W-only)
```

In the `M+ N- V-` condition this quantity has a particularly clean meaning:

> the capacity gain from choosing morphology-defined temporal filters, with no dendritic nonlinearity available.

This is the most direct bridge between Green functions and TwinProp.

---

## 6. Measure the actual filter bank

For a passive morphology, compute source-to-soma kernels at a frozen set of locations using NEAT/SOV/Green machinery:

```text
H = [h_1(t), h_2(t), ..., h_K(t)]
```

For a learned TwinProp/F&F contact map, construct each axon's composite filter

```text
g_a(t) = sum_i W[a,i] h_i(t)
```

and stack them:

```text
G = [g_1(t), g_2(t), ..., g_A(t)]
```

Useful diagnostics:

```text
effective rank(G)
singular-value entropy(G)
pairwise filter distance
peak-latency distribution
rise/decay-time distribution
frequency-response diversity
```

Then ask whether the task benefit of `W+LOC` scales with the increase in **composite-filter diversity**, not merely with anatomical distance.

This is not proposed as a new general capacity theorem. It is a mechanistic diagnostic.

---

## 7. A second correction: active dendrites may REDUCE soma-level location diversity

A naive version of our earlier idea predicts:

```text
more active dynamics -> more distinct location-to-soma responses
```

That is not generally true.

Classical work by Cook & Johnston (1997) showed that active dendrites can reduce location-dependent variability of synaptic responses at the soma. Synaptic-democracy work similarly shows that biological scaling mechanisms can compensate passive attenuation so distal and proximal inputs have more equal somatic impact.

This creates a very useful conceptual distinction:

```text
LOCAL SEPARATION
    can different dendritic regions maintain partially independent states?

GLOBAL READABILITY
    can each such region still influence the output effectively?
```

The computational sweet spot may be neither maximal coupling nor maximal isolation.

It may be:

> **many locally independent nonlinear subunits, each with sufficiently democratic access to the global readout.**

This is close to what Eyal-style independent NMDA-subunit measurements operationalize, but it suggests measuring the two ingredients separately.

Candidate diagnostics:

```text
S_local = electrical / dynamic separation among candidate subunits
R_soma  = equality and sufficiency of their influence at the soma
```

A useful neuron needs both.

Do not define `S_local * R_soma` as a new metric until the components and nulls are validated.

---

## 8. This resolves an apparent tension in the literature

Several established results can coexist:

```text
passive morphology
    -> location-dependent temporal filters
    -> useful dendro-plexing

local NMDA / active channels
    -> branch-specific nonlinear events
    -> independent subunit computation

active conductances / synaptic scaling
    -> partial normalization of soma-level location bias
    -> more democratic readout
```

So computational power need not arise because every location becomes maximally different at the soma.

A better architecture is:

```text
rich local internal geometry
            +
controlled global projection
```

That is a more precise descendant of the old GeometricNeuron intuition than "geometry creates many transfer functions" by itself.

---

## 9. Why this matters for FCI

FCI may be high for at least two mechanistically distinct reasons:

```text
1. many temporal filters / long memory kernels that the fixed TCN must emulate
2. many interacting nonlinear local states whose combinations affect spiking
```

The 2026 dendro-plexing paper makes (1) a serious candidate rather than a nuisance baseline.

Therefore the proposed ladder is:

```text
L0  point / LIF
L1  passive morphology + multi-contact dendro-plexing
L2  L1 + NMDA
L3  L1 + active dendritic conductances
L4  full morphology + NMDA + active conductances
```

For each rung measure both:

```text
emulation difficulty (FCI or matched cheaper proxy)
actual task capacity (TwinProp-style optimization)
```

The central empirical question becomes:

> Which physical mechanism raises emulation difficulty, which raises usable task capacity, and which raises both?

That comparison can falsify the assumption that FCI and computational power are the same thing.

---

## 10. Immediate experiment on the exact Hay `cell1.asc`

We already verified that the FCI rat-L5 morphology `cell1.asc` is byte-identical to the morphology used in the released Beniaguev 2021 deep-neuron code.

That makes it the obvious first test bed.

Before attempting the full 24-cell panel:

1. compute passive source-to-soma Green kernels on the exact Hay morphology;
2. generate matched single-contact and multi-contact axon layouts;
3. measure composite-filter diversity;
4. run a simple temporal classification/memory task in the pure passive `M+N-V-` model;
5. then add NMDA and active conductances one factor at a time;
6. only after the mechanism ladder behaves sensibly, connect the result to the FCI target and larger morphology panel.

This is not a species claim. It is a mechanism calibration.

---

## Primary-source anchors

- Beniaguev, Shapira, Segev & London (2026), *J Neurosci*, `10.1523/JNEUROSCI.0839-24.2026` — dendro-plexing / Filter-and-Fire.
- Aizenbud et al. (2026), bioRxiv `10.64898/2026.06.08.730984` — TwinProp.
- Cook & Johnston (1997), *J Neurophysiol* 78:2116–2128, `10.1152/jn.1997.78.4.2116` — active dendrites reduce location-dependent variability.
- Magee & Cook (2000), *Nature* 406:951–956, `10.1038/35023044` — somatic EPSP amplitude can be normalized across synaptic location by distance-dependent synaptic scaling.
- Gidon & Segev (2009), *J Neurophysiol* 101:3226–3234, `10.1152/jn.91349.2008` — STDP and synaptic democracy.
- Nicholson et al. (2014), *Neuron* 81:379–390, `10.1016/j.neuron.2013.09.027` — local dendritic integration and global synaptic impact can be jointly normalized.
- Wybo et al. (2019), *Cell Reports* 26:1759–1773.e7 — impedance-derived functional compartments / NET.

## Current Dig sentence

> **Morphology supplies both addresses and temporal filters. Multiple contacts can combine those filters even before dendritic nonlinearities act. NMDA and voltage-gated channels then create local state-dependent computation, while active and plastic mechanisms may simultaneously normalize access to the global readout. The experiment is to separate these resources rather than call all of them "geometry."**
