# Jaxley direct gate: remove the digital-twin confound

**Status:** implementation route from peer-reviewed differentiable-simulation work. Not a result.  
**Date:** 2026-08-15.

## 0. Why this changes the experiment

The FCI/TwinProp bridge had a serious calibration problem:

```text
biophysical neuron
      -> train digital twin
      -> optimize task through twin gradients
      -> replay solution in biophysical neuron
```

If two cell types differ in how difficult they are to emulate, then they may also differ in **gradient fidelity**. A higher-FCI neuron could appear harder to optimize merely because its digital twin supplies worse gradients.

Deistler et al. 2025 introduced **Jaxley**, a differentiable multicompartment biophysical simulator in JAX. The simulator itself supports automatic differentiation with respect to ion-channel, synaptic and morphological parameters and can be trained on computational tasks.

This suggests a cleaner route:

```text
optimizer
      -> differentiable biophysical simulator itself
      -> task loss
```

No learned surrogate is required for the first mechanism experiments.

That removes the largest conceptual confound in the cross-cell capacity test.

---

## 1. What Jaxley already demonstrates

The peer-reviewed Nature Methods paper reports that Jaxley:

- uses implicit-Euler multicompartment simulation inside JAX;
- computes gradients by backpropagation;
- can optimize channel, synaptic and morphological parameters;
- matched NEURON voltage traces in its benchmark at sub-millisecond and sub-millivolt resolution;
- optimized up to thousands/millions of biophysical parameters;
- trained single morphologically extended neurons on nonlinear tasks;
- trained morphologically detailed biophysical networks on behavioral/computer-vision tasks.

In one single-neuron demonstration the authors directly optimized each compartment's:

```text
Na conductance
K conductance
leak conductance
radius
length
axial resistivity
```

So direct optimization through morphology-dependent cable dynamics is not a speculative software feature; it is already part of the published method.

The current Jaxley tests also explicitly expose `radius`, `length`, `axial_resistivity`, channel conductances and synaptic conductances through `make_trainable()`.

---

## 2. The exact Hay morphology is reachable, with one conversion step

Our anchor morphology is the verified Hay `cell1.asc` shared byte-for-byte by the FCI repository and the 2021 Beniaguev deep-neuron repository.

Jaxley currently imports SWC reconstructions, not ASC directly.

This is not a conceptual blocker. The Jaxley authors' own experiment repository converts ASC morphologies to SWC using `morph_tool.convert(...)` before importing them. Our existing `fetch_aizenbud_exact4.py` already preserves the original ASC and can make a derived SWC copy.

The provenance rule should be:

```text
author-released ASC remains canonical
       |
       | deterministic documented conversion
       v
Jaxley SWC working copy
```

Record both hashes and never treat the converted SWC as a replacement for the source morphology.

---

## 3. Start with the part that can be made exact fastest

Do **not** begin by porting the entire active Hay 2011 channel set.

Start with the morphology-preserving passive condition from the missing TwinProp ablation:

```text
M+ N- V-

full dendritic morphology
passive dendritic cable
AMPA/GABAA input
no NMDA
no dendritic voltage-gated channels
active soma/axon output mechanism retained
```

Why first:

1. it isolates the Green/dendro-plexing contribution we actually want;
2. the passive cable is straightforward to cross-validate against NEURON and NEAT;
3. it avoids a large mechanism-porting project before we know whether the passive effect is worth anything;
4. it gives a direct task-capacity measurement with no digital twin.

The FCI released HOC provides a concrete `CODE_EXACT` passive target. It uses `Ra=150 Ohm cm`; soma/axon `cm=1` and `g_pas=1/20000`, while basal/apical dendrites use doubled `cm=2` and `g_pas=2/20000`. This preserves the same nominal passive membrane time constant while changing per-area load. The paper-nominal uniform passive parameters should remain a separate sensitivity condition rather than being silently substituted.

---

## 4. Cross-simulator Gate J0 — no optimization yet

Before training anything, the converted Hay morphology must reproduce passive transfer.

Choose a frozen set of dendritic locations spanning:

```text
basal / apical
proximal / middle / distal
thin / thick branches
branchpoint / terminal neighborhoods
```

At each source inject the same small current impulse or short pulse.

Record:

```text
local voltage
somatic voltage
selected other dendritic receivers
```

Compare three instruments where applicable:

```text
NEURON author-model passive simulation
NEAT Green/SOV impulse response
Jaxley passive simulation
```

Primary acceptance quantities:

```text
waveform RMSE
peak amplitude error
peak-time error
integral / DC transfer error
decay-time error
```

Do not optimize parameters to force agreement at this stage. The point is to validate the translation.

If the three disagree materially, stop before task training and debug morphology conversion, discretization, units and boundary conditions.

---

## 5. Direct capacity Gate J1 — strength learning only

Freeze contact locations first.

For each input identity create a matched set of physical contacts on the full morphology. Optimize only synaptic conductances using gradients through Jaxley.

Use a differentiable training objective based on somatic voltage margin / smooth readout during training, then score the final detailed simulation with the desired hard spike/task criterion.

This distinction matters because exact spike count/timing is discrete and can create poor gradients. It also mirrors the Jaxley paper's use of differentiable voltage-based task losses.

Conditions:

```text
point / collapsed matched control
single-contact passive morphology
multi-contact passive morphology
```

Keep fixed:

```text
input identities
physical contact budget
conductance budget
stimulus set
readout/scoring rule
```

The comparison

```text
single-contact -> multi-contact
```

measures passive dendro-plexing capacity directly in a detailed cable model.

---

## 6. Address learning without pretending discrete location is differentiable

Jaxley can differentiate continuous biophysical parameters, but current evidence does not establish that a synapse's discrete postsynaptic compartment index itself is a native trainable variable.

So do not write `make_trainable("location")` and pretend this problem is solved.

Instead use a candidate-site relaxation.

For each input axon `a`, preinstantiate contacts at a frozen candidate set `i=1...K` and learn non-negative gating/conductance variables:

```text
g_ai >= 0
```

with a fixed budget, e.g.

```text
sum_i g_ai <= G_a
```

or a softmax / sparse allocation parameterization.

This gives a differentiable relaxation of address selection:

```text
axon a
   -> candidate locations i
   -> learned conductance allocation g_ai
```

After optimization:

1. inspect the soft solution;
2. project to the allowed number of discrete contacts;
3. re-optimize strengths with locations frozen;
4. evaluate in the simulator.

Call this **candidate-address optimization**, not exact structural-plasticity gradients.

---

## 7. Now the FCI addressing correction becomes useful

The published FCI generator and TwinProp expose different input algebras:

```text
FCI:
    segment-addressed channels
    independent source groups are collapsed locally per segment

TwinProp / dendro-plexing:
    axon-addressed variables
    one source identity can occupy several dendritic locations
```

Jaxley lets us manufacture both protocols on the **same physical cell**.

Construct:

```text
S protocol: segment-local identities
D protocol: shared axon identity across multiple locations
```

Then cross:

```text
emulation difficulty
x
optimized task capacity
```

This asks whether the addressing scheme changes one quantity, the other, or both.

It also prevents us from interpreting a difference between FCI and TwinProp as purely a property of dendritic biophysics when part of the difference is actually the definition of an input variable.

---

## 8. Add NMDA second — this is already technically plausible

The base Jaxley repository does not contain a ready-made exact replica of the FCI/Hay synapse set.

However, the companion `jaxley-mech` repository already contains differentiable AMPA, GABAA and voltage-dependent **NMDA** synapse implementations, including an explicit magnesium-block factor.

That makes the next rung realistic:

```text
M+ N+ V-
```

but it must first be parameter-matched to the Aizenbud rat synapse model:

```text
AMPA rise/decay
NMDA rise/decay
NMDA/AMPA conductance ratio
voltage-dependence gamma / Mg-block curve
reversal potentials
```

Do not assume the Destexhe98 mechanism is equivalent merely because both are called NMDA.

Cross-validate unitary and paired PSPs against the released NEURON FCI implementation before using it mechanistically.

---

## 9. Active Hay comes last

The current core Jaxley channel library exposes generic HH/Pospischil-style mechanisms; the companion mechanism repository expands this, and Jaxley explicitly supports user-defined channels and synapses.

But I have not found an off-the-shelf exact port of the full Hay 2011 channel set in the current repositories.

Therefore:

```text
M+ N- V-   easy first target
M+ N+ V-   moderate: synapse matching
M+ N- V+   mechanism-porting work
M+ N+ V+   full target
```

Porting the active mechanisms only becomes worth the work if the first two gates yield a useful separation.

---

## 10. The direct 2 x 2 x 2 experiment survives

Once the mechanism ports validate, run the earlier factorial directly in the biophysical simulator:

```text
M = full morphology / matched collapsed control
N = NMDA off / on
V = dendritic voltage-gated mechanisms off / on
```

For each condition measure:

```text
task performance after direct optimization
local dendritic trajectory dimension
local independence / interaction
somatic readability
passive/linearized transfer structure
```

Then independently estimate emulation difficulty with an FCI-like fixed surrogate.

The most informative result is not necessarily `full > everything`.

It is the decomposition:

```text
which mechanism raises real task capacity?
which mechanism raises surrogate difficulty?
which does both?
```

---

## 11. A new measurement Jaxley makes almost embarrassingly natural

Because the simulator itself is differentiable, for current state/input `x` we can directly measure sensitivities such as

```text
d output(t+T) / d g_ai
```

for every candidate synaptic address `i`, or gradients with respect to channel parameters and morphology variables.

This is a concrete version of the PivotPoint / receiver-reachable-future language:

```text
current biophysical state
      -> local parameter/address perturbation
      -> future receiver effect
```

Do not call this a new geometry. It is a simulator Jacobian / sensitivity map.

But it gives an experimentally useful field over the dendritic tree:

> where, *in the current state and task*, can a tiny admissible intervention most change a future somatic decision?

Compare that map across passive, NMDA and active conditions. If the map reorganizes rather than simply rescales, that is a direct demonstration of **state/biophysics changing effective action accessibility on fixed anatomy**.

---

## 12. Immediate build order

```text
J0  exact ASC -> documented SWC conversion
J1  passive NEURON <-> NEAT <-> Jaxley transfer validation
J2  direct passive single-contact vs multi-contact task
J3  candidate-address optimization
J4  segment-local vs axon-shared addressing comparison
J5  matched AMPA/GABA/NMDA port and validation
J6  NMDA task factorial
J7  only then port active Hay mechanisms
J8  compare direct task capacity with FCI-like emulation difficulty
```

The first four gates already answer a real question without touching the speculative physics layer.

## Primary anchors

- Deistler et al. (2025), *Nature Methods*, `10.1038/s41592-025-02895-w` — Jaxley differentiable biophysical simulation.
- `jaxleyverse/jaxley` — current simulator implementation; SWC import and trainable morphology/channel/synapse parameters.
- `jaxleyverse/jaxley-mech` — mechanism library; includes AMPA/GABAA/NMDA implementation with Mg block.
- `mackelab/jaxley_experiments` — official experiment code; demonstrates ASC-to-SWC conversion with `morph_tool`.
- `ido4848/FCI` — target morphology, passive parameters, synaptic parameters and original input-addressing implementation.

## Current Dig sentence

> **We no longer need a learned digital twin to test the first capacity hypotheses. A differentiable biophysical simulator can make the morphology itself the trained object. The immediate target is the missing pure-cable condition on the exact Hay tree, with source identity and contact addressing controlled explicitly.**
