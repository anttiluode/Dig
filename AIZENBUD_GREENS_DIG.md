# Aizenbud × Green functions: the first serious dig

**Status:** research plan, not a result.  
**Rule:** use established cable theory first; invent terminology only after an external result forces it.

The `one_iota.py` toy established only a mathematical warning: global eigenvalues can agree while local time evolution differs. This note asks whether the same lesson matters in a real biological target: the morphologies used by Aizenbud et al. (PNAS 2026).

## 1. The unexpected collision with existing science

The proposed object already has a respectable name.

For a linear or linearized dendritic cable, inject current at dendritic location `i` and observe voltage at receiver `r` (initially the soma):

```text
Z[r <- i](omega) = V_r(omega) / I_i(omega)
```

`Z` is the **transfer impedance**. Its inverse Fourier transform

```text
h[r <- i](t) = F^-1 Z[r <- i](omega)
```

is the time-domain response kernel / Green-function kernel.

This is classical dendritic cable theory, not a new formalism.

Relevant primary literature:

- Wybo, Stiefel & Torben-Nielsen (2013), *The Green's function formalism as a bridge between single and multi-compartmental modeling*, arXiv:1309.2382.
- Wybo et al. (2015), *A sparse reformulation of the Green's function formalism allows efficient simulations of partial differential equations on tree graphs*, arXiv:1504.03746.
- Wybo et al. (2021), *Data-driven reduction of dendritic morphologies with preserved dendro-somatic responses*, eLife 10:e60936.
- Wybo (2026), *The Neural Analysis Toolkit Unifies Semi-Analytical Techniques to Simplify, Understand, and Simulate Dendrites*, Neuroinformatics 24:21, DOI 10.1007/s12021-025-09766-x.

The 2026 NEAT paper is especially important. It explicitly treats response kernels, input/transfer impedances and resistances as different expressions of the Green's function of the linearized neuron model. It implements Koch/Poggio impedance calculations, time-domain Green kernels, Major's separation-of-variables solution, arbitrary dendritic locations, and linearization around different membrane/channel states.

That means we should **not build a home-made Green-function solver first**. NEAT is almost exactly the microscope this question needs.

## 2. Why this is not just V22 with fancier graph features

V22 compressed each morphology into global modal statistics such as spectral entropy and root participation entropy. On the clean common-rat-synapse Aizenbud target, those features did not beat the ordinary area/path baseline. Preserve that null.

A transfer kernel is qualitatively different from another global graph scalar.

For every dendritic source location `i`, it preserves:

```text
source location
receiver location
attenuation
frequency response
phase
rise/decay structure
time scale mixture
```

A morphology therefore induces a **family** of local temporal filters rather than one spectrum.

For `K` matched source sites and soma receiver `s`:

```text
H = [ vec(h[s <- 1])  vec(h[s <- 2]) ... vec(h[s <- K]) ]
```

This is the object to study.

The working question is not:

> does a complex-looking tree have a complex spectrum?

It is:

> **with the same number of possible input addresses, how many materially distinguishable temporal consequences can this morphology deliver to the soma?**

That is directly compatible with V22's receiver-distinguishable-futures criterion, but now the measurement is standard cable theory.

## 3. Why Aizenbud is unusually well matched to this test

Aizenbud et al. do not score neurons by a purely static property. Their Functional Complexity Index is based on how difficult it is for a fixed **temporal convolutional network** to reproduce the neuron's input/output mapping at millisecond resolution.

The paper reports that morphology alone still contributes when the same rat-type synapses are used across rat and human morphologies. Its strongest simple morphological correlate is total dendritic area; long bifurcation-path structure adds explanatory power, while merely counting bifurcations is much weaker.

That makes transfer kernels more than arbitrary feature engineering: **they are the linear spatiotemporal transformation created by the morphology before the nonlinear synaptic/somatic machinery completes the I/O map the TCN is trying to emulate.**

There is also an important independent guardrail from Cuntz et al. (Neuron 2021, DOI 10.1016/j.neuron.2021.08.028): under distributed synaptic activation, spike counts can be remarkably insensitive to dendritic size/shape, while **spike timing still depends on morphology**. If our proposed effect is real, temporal kernel diversity is a more plausible place to find it than a generic "more branches = more computation" story.

Human data also point toward impedance/transfer as a meaningful level of description. Beaulieu-Laroche et al. (Cell 2018) directly measured stronger electrical compartmentalization in long human cortical dendrites; the distal human dendrites are more electrotonically remote from the soma even when distance-matched transfer can be similar.

## 4. The exact author-released foothold

The PNAS paper states that morphology/model data are deposited in the authors' FCI repository. The currently visible repository exposes four complete model folders with exact morphology files:

```text
Rat L2:
  mtC191200B_idA_diams_fixed.asc

Rat L5:
  cell1.asc

Human L2/3:
  2013_03_06_cell11_1125_H41_06.asc

Human L5:
  2057_H21_29_197_11_01_03_metcontour.asc
```

These four are enough for a **mechanism sanity check**, not a species-statistics claim.

V22 has additionally provenance-resolved/source-compatible morphologies for 16 of the 24 plotted cells. Those can become a second-stage exploratory panel, but the missing eight mappings still forbid pretending we have an exact 24-cell replication.

## 5. A model-parameter issue to resolve before calling anything exact

The PNAS Methods text reports common passive parameters:

```text
Cm = 1 uF/cm^2
Ra = 150 ohm cm
Rm = 20,000 ohm cm^2
```

The released common HOC model is more nuanced:

```text
soma/axon:
  cm = 1
  g_pas = 1/20000

apical/basal dendrites:
  cm = 2
  g_pas = 2/20000

all:
  Ra = 150
```

The doubled dendritic capacitance and leak preserve the local membrane time constant but change load/impedance. I am **not** assigning a biological explanation to that difference without a source.

Therefore the first analysis should keep two explicitly labelled arms:

```text
CODE_EXACT     = reproduce released FCI passive implementation
PAPER_NOMINAL  = uniform Cm=1, Rm=20k, Ra=150
```

If the qualitative result depends on this choice, that dependence is itself a result and we stop making broad claims.

## 6. Gate G0 — four-cell transfer atlas

### Sampling

Use the same number `K` of dendritic addresses for every morphology. A first value of `K=256` is large enough to map the tree but not tied to total dendritic length.

Do not sample uniformly by raw file point count. Stratify by:

```text
path-distance quantile
x
branch class (apical/basal when available)
```

and use a frozen RNG seed.

This deliberately removes the simple "larger tree = more addresses" explanation for the first test.

### Receiver

Start with the soma only. Later use sampled dendrite-to-dendrite pairs.

### Passive measurements

For each source site `i` compute:

```text
Z_i(omega) = Z[soma <- i](omega)
h_i(t)     = inverse transform of Z_i
```

Store both raw and normalized kernels.

Raw kernels contain attenuation + shape.

Normalized kernels ask the harder question:

> after removing simple gain, does location still create a different temporal filter?

### Minimal descriptive quantities

Do not generate fifty features.

1. **DC transfer resistance distribution** `Z_i(0)`.
2. **Kernel centroid / peak / decay-time distributions**.
3. **Raw transfer-dictionary effective rank**.
4. **Amplitude-normalized transfer-dictionary effective rank**.
5. **Pairwise normalized kernel Gram matrix**.

Let columns of `Hn` be unit-norm kernels. Then

```text
C = Hn.T @ Hn
```

`C[i,j] ~ 1` means two physical input locations are almost receiver-equivalent in temporal shape. Smaller similarity means morphology has made those addresses temporally distinguishable at the soma.

For singular values `sigma_j` of `H`, define only as a descriptive statistic:

```text
p_j = sigma_j^2 / sum_k sigma_k^2
r_eff = exp(-sum_j p_j log p_j)
```

This is **not** "the number of dendritic computations." It is the effective dimension of this particular sampled transfer dictionary under this particular receiver and time window.

## 7. Gate G1 — do ordinary morphology variables already explain it?

A Green-function result is uninteresting if it is simply path length in disguise.

For every source, compare kernel properties to:

```text
physical path distance to soma
electrotonic distance / DC attenuation
branch class
local diameter
```

At the cell level compare transfer-diversity measures to the Aizenbud variables that already work:

```text
total dendritic area
longest bifurcation branch / max path-like quantity
branch allocation
```

The desired result is **not** "human > rat" on four cells.

The useful sanity result would be something like:

> two morphologies matched reasonably on ordinary path/area summaries still organize their local temporal filters differently.

If we cannot find that under controlled morphologies later, stop.

## 8. Gate G2 — use the full impedance matrix, not just the soma projection

This may be more important than the soma-only test.

Aizenbud's nonlinear synapses interact locally inside the dendritic tree. Source-to-soma kernels see only the final projection. NEAT's own 2021/2026 reduction work emphasizes the **full resistance matrix** because it preserves intra-dendritic interactions that a dendrite-to-soma-only reduction can miss.

For the same `K` sites compute sampled matrices

```text
Z_ij(omega)
```

and their time-domain kernels.

Now morphology defines two related objects:

```text
READOUT GEOMETRY:
  source i -> soma

INTERACTION GEOMETRY:
  source i <-> source j
```

The second object is where compartmentalization and local NMDA cooperation actually live.

A potentially strong prediction follows:

> **FCI may relate more strongly to the diversity/organization of intra-dendritic transfer kernels than to global graph spectrum or source-to-soma attenuation alone.**

This is a hypothesis, not a result.

## 9. Gate G3 — the clean descendant of Clockfield: operating-point geometry

This is where the old state-dependent-time intuition meets established cable theory without importing the physics claim.

For an active dendrite, linearize around operating state `x`:

```text
Z_x(i,j,omega)
h_x(i,j,t)
```

NEAT explicitly supports quasi-active Green-function calculations around chosen voltage/channel-state expansion points. Its model-reduction machinery evaluates resistance matrices at multiple expansion points precisely because one fixed linearization does not span the nonlinear operating range.

Thus the same anatomical tree can legitimately have:

```text
anatomy fixed
state x0 -> transfer geometry G0
state x1 -> transfer geometry G1
```

No event horizon language is needed. The measurable question is:

> **does the set of receiver-distinguishable and mutually interacting dendritic addresses deform with operating state?**

A finite-horizon "accessibility boundary" can later be defined operationally by a noise/discrimination threshold, but only after the transfer measurements exist.

## 10. Gate G4 — NMDA: where linear Green functions must stop

Aizenbud's important nonlinearity is NMDA. A Green function describes a linear or linearized system, so it cannot by itself establish the nonlinear mechanism.

Use the Green atlas as the **passive/quasi-active baseline**.

Then, in the authors' NEURON model, activate matched pairs/sets of synapses and ask whether the nonlinear somatic or local response lies outside the span predicted from the single-site kernels:

```text
predicted_linear(t) = sum_i h_i * input_i
observed_NMDA(t)    = NEURON simulation
residual(t)         = observed - predicted
```

Then ask whether the residual/new response dimensions depend systematically on the interaction geometry `Z_ij`.

That is much closer to the Aizenbud mechanism than another morphology statistic.

## 11. The actual confirmatory test, if G0-G4 survive

Only after the mechanism sanity work:

```text
target:
  common-rat-synapse FCI

baseline B2:
  area + path/branch-allocation quantity

candidate additions (frozen small set):
  normalized soma-kernel diversity
  full-matrix interaction diversity
  one attenuation-sensitive kernel measure
```

Use strict cross-validation / leave-one-cell-out and a permutation or sign-flip test appropriate to the small panel.

The first result that matters is simply:

```text
B2 + Green metrics
    predicts held-out common-synapse FCI better than B2
```

If not, stop. The Green-function picture may still be a useful visualization, but it has not explained Aizenbud functional complexity.

## 12. What I think we may have found — carefully phrased

The literature already knows that dendrites are cables, that morphology shapes impedance, that Green functions capture dendritic filtering, and that functional subunits can be characterized electrically. None of that is ours.

The potentially useful synthesis is the **question being asked of those established objects**:

> **Treat a dendritic location not merely as an XYZ/path coordinate, but as a receiver-relative temporal transfer signature; treat morphology as the organization of those signatures; then ask whether the diversity and state-dependence of that transfer geometry explains externally measured single-neuron functional complexity beyond ordinary size/path summaries.**

That directly joins:

```text
Aizenbud        morphology -> functional complexity
Green/cable     location -> temporal transfer kernel
V22             local write -> distinguishable receiver future
PivotPoint      distinct futures, not nominal addresses, define useful DOF
PresentMoment   current state contains partially propagated causal history
```

But only the first two lines are established science. The latter synthesis earns anything only if the gates above survive.

## 13. Immediate build order

1. Use MorphIO to convert the four author `.asc` files to `.swc` without resampling geometry unnecessarily.
2. Load them in NEAT.
3. Reproduce the released passive parameters and separately the paper-nominal passive parameters.
4. Freeze a `K=256` address sampler.
5. Produce the four-cell soma transfer atlas.
6. Run path/electrotonic controls before looking for species stories.
7. Add sampled full impedance matrices.
8. Only then turn on operating-point / NMDA experiments.

No new neural architecture yet. No new physics. First make the dendrites answer the question.
