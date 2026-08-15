# The missing AMPA-only gate: Aizenbud's “morphology-only” FCI is not a pure cable experiment

**Status:** code/paper audit + proposed intervention. Not a result.  
**Date:** 2026-08-15.

## 0. The correction

Aizenbud et al. 2026 describe SI Fig. S5 as testing whether morphology alone contributes to FCI by assigning **rat-type synapses to all rat and human morphologies**.

That does hold the *synapse type* constant across morphologies.

But rat-type excitatory synapses are still **AMPA + voltage-dependent NMDA** synapses.

Therefore the S5 condition is not a pure passive-cable morphology test.

The dendritic membrane is passive, but the input mechanism remains locally voltage-dependent and nonlinear.

So the causal statement supported by S5 is narrower:

> with the same rat synaptic biophysics, different morphologies still produce different FCI values.

It does **not** by itself tell us whether the morphology contribution comes from:

```text
A. passive cable / temporal filtering
B. morphology-dependent organization of NMDA nonlinear interactions
C. both
```

That distinction is exactly the seam the Green-function dig needs.

---

## 1. The released code makes this explicit

The rat parameter set in `simulating_neurons/neuron_models/model_utils.py` uses:

```text
AMPA tau_r = 0.2 ms
AMPA tau_d = 1.7 ms
NMDA tau_r = 0.29 ms
NMDA tau_d = 43 ms
gamma = 0.062 /mV
NMDA_ratio = 0.0003 / 0.0004 = 0.75
AMPA peak conductance = 0.0004
```

`create_synapses()` installs the combined `AMPANMDA_EMS` mechanism at each dendritic segment and assigns that nonzero NMDA ratio.

The NMODL mechanism then computes

```text
weight_NMDA = weight * NMDA_ratio
```

and voltage-gates the NMDA conductance through the magnesium block.

Thus the common-rat-synapse target used by V22 and by the PNAS S5 analysis is explicitly **NMDA-on**.

---

## 2. I found no named AMPA-only condition in the released standard parameter sets

The released `PARAMETER_SETS` currently define:

```text
human
human_rat_gamma
rat
rat_human_gamma
```

All four contain nonzero NMDA conductance ratios.

A repository search for the standard NMDA-ratio assignments did not reveal a separate named AMPA-only parameter set.

Likewise, the main PNAS paper and the text-indexed supporting-material search I could perform do not expose an AMPA-only morphology-panel result.

This is **not proof that the authors never ran one privately or that no unindexed SI detail exists**. It is only an audit statement about the published/released material I could inspect.

---

## 3. The clean intervention

For every morphology, rerun the FCI pipeline with:

```text
same morphology
same dendritic passive parameters
same AMPA kinetics and conductance
same GABAA kinetics and conductance
NMDA_ratio = 0
same soma/axon spike machinery
```

Then redo the authors' firing-rate normalization so each model again operates near the matched ~1 spike/s output regime.

Call this target:

```text
FCI_AMPA
```

and retain their common-rat-synapse result as:

```text
FCI_RAT_NMDA
```

The paired within-cell difference

```text
Delta_NMDA = FCI_RAT_NMDA - FCI_AMPA
```

is not a formal additive causal decomposition of “complexity,” because FCI is a nonlinear transform of separately trained surrogate performance under re-normalized input regimes.

But it is a valid intervention contrast:

> how much does adding the same voltage-dependent NMDA mechanism change fixed-probe emulation difficulty on this exact morphology?

---

## 4. This creates two mechanistic targets instead of one muddy target

### Target A — pure cable / morphology contribution

```text
FCI_AMPA
```

Dendrites are passive and excitatory input is voltage-independent AMPA.

There is still a nonlinear soma/axon spike generator, so this is not a globally linear system. But the dendritic transformation before the spike mechanism is now much closer to the Green-function/filter-bank picture.

Question:

> Do cells with richer passive source-to-soma transfer structure have larger FCI_AMPA after ordinary area/path controls?

### Target B — morphology-dependent nonlinear increment

```text
Delta_NMDA
```

Question:

> Which properties of the morphology predict how much the same rat NMDA mechanism increases FCI?

This is where NET/electrical compartmentalization, local input impedance and dendritic subunit organization have a much stronger mechanistic claim than global graph spectrum.

---

## 5. The possible outcomes are all informative

### Outcome 1 — FCI_AMPA is tiny and nearly morphology-invariant

Then the PNAS morphology effect is not mainly “complicated passive filtering.”

The stronger interpretation becomes:

```text
morphology
    -> organizes local voltages / electrical separation
    -> changes how a common NMDA nonlinearity can interact
    -> changes FCI
```

That would be a strong win for the nonlinear-compartment interpretation and a loss for the simple Green-filter explanation of FCI.

### Outcome 2 — FCI_AMPA varies strongly across morphologies

Then passive cable dynamics alone make a substantial contribution to fixed-TCN emulation difficulty.

Now Green/SOV transfer descriptors become legitimate candidate mechanisms for that variation.

The right next test is whether they add held-out value beyond area/path/electrotonic-distance baselines.

### Outcome 3 — FCI_AMPA varies, but ranking changes dramatically when NMDA is restored

Then there are at least two different geometrical resources:

```text
passive temporal-filter geometry
and
nonlinear interaction / compartment geometry
```

That is probably the most interesting outcome scientifically because it says “morphology” is not one mechanism.

### Outcome 4 — area/path predicts both FCI_AMPA and Delta_NMDA almost perfectly

Then our operator/NET descriptors add little mechanistic compression and should be dropped.

This is a good kill condition.

---

## 6. This also reinterprets the V22 null correctly

V22's clean common-rat-synapse external target was already a useful negative result:

```text
area + path baseline > area + path + global spectral summaries
```

But because that target still has NMDA on, the null cannot distinguish whether the failed global spectral features were irrelevant to:

```text
passive cable filtering
or
morphology-dependent nonlinear interaction
```

The new split gives V22 two cleaner successor gates:

```text
G_passive:
    predict FCI_AMPA

G_nonlinear:
    predict Delta_NMDA
```

Do not reuse the same three V22 spectral scalars as the main features. The previous null already retired them.

For `G_passive`, use physically grounded local Green/SOV/transfer descriptors.

For `G_nonlinear`, use preregistered electrical-compartment / NET descriptors and eventually explicit local NMDA-subunit tests.

---

## 7. The exact four-cell pilot is enough to debug, not to infer

Before spending GPU-years recreating the full 24-cell FCI panel, use the four author-released complete models already collected by `fetch_aizenbud_exact4.py`:

```text
rat L2
rat L5 Hay cell1
human L2/3
human L5
```

Run short/cheap surrogate calibration or even direct descriptive simulations to verify:

```text
NMDA_ratio=0 really removes voltage-dependent excitatory current
output-rate normalization still finds a valid operating regime
passive transfer predictions agree with NEAT/Jaxley
restoring rat NMDA produces expected local supralinearity
```

No species statistics from n=4.

If this plumbing fails, stop there.

---

## 8. A cheaper first test may avoid retraining FCI entirely

Before training any surrogate, compare the detailed neuron directly under matched stimulus ensembles.

For each morphology run the identical input patterns twice:

```text
AMPA/GABAA only
rat AMPA+NMDA/GABAA
```

Record:

```text
local dendritic voltage trajectories
somatic voltage
spike output
pairwise deviations from linear superposition
```

Then ask whether the addition of NMDA creates morphology-specific growth in:

```text
local trajectory dimension
branchwise independence
cross-location interaction structure
history dependence
```

If all morphologies respond almost identically after basic size/path matching, there is little reason to spend money on the full FCI retraining.

---

## 9. The full mechanism ladder is now cleaner

```text
F0  collapsed/point matched baseline

F1  full morphology + AMPA/GABAA only
    -> passive cable / address / temporal-filter contribution

F2  F1 + common rat NMDA
    -> morphology x common local nonlinearity

F3  morphology + species/hybrid NMDA parameters
    -> synaptic-biophysics difference

F4  F3 + dendritic voltage-gated conductances
    -> active dendritic contribution
```

For each rung keep two outcome families separate:

```text
emulation difficulty (FCI-like)
actual optimized task capacity (Jaxley/TwinProp-style)
```

The experiment then asks which physical mechanisms raise one, the other, or both.

---

## 10. Why this is the most useful “dig” so far

The PNAS phrase “morphology alone” is scientifically reasonable in the comparison they intended: synapse **type is held fixed** across morphologies.

But for our mechanistic question it hides an interaction:

```text
fixed NMDA biophysics
x
different dendritic voltage fields
```

So the next useful question is not “does morphology matter?” — they already showed that.

It is:

> **What does morphology do before voltage-dependent dendritic nonlinearity is allowed to help, and what new computation appears when the same nonlinearity is switched back on?**

That is experimentally sharp, physically grounded and directly falsifiable.
