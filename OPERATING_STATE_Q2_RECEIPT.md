# Q2 receipt — same mechanisms, different operating state

**Date:** 2026-08-15  
**Status:** executed preregistered gate. **Q2-C / near-isometry under the somatically driven subthreshold state shift.**  
**Gate:** `OPERATING_STATE_Q2_GATE.md`  
**Executable:** `receiver_operating_state_cell1.py`

## Provenance

Same public full-active model as Q1:

```text
SelfishGene/neuron_as_deep_net
commit 074c4666300a8ad246601dab179a97a6942f0f29
```

Same morphology:

```text
L5PC_NEURON_simulation/morphologies/cell1.asc
```

Same released Hay/Beniaguev biophysics in both conditions.

No conductance, morphology, source coordinate, receiver coordinate, source pulse, normalization, or comparison metric differs between HYPER and DEPOL.

The only intervention is a persistent somatic DC `IClamp`, calibrated without reference to source-geometry outcomes.

---

# Valid run

GitHub Actions run:

```text
31888124244
```

Dig commit tested:

```text
0e1dacbb037d2900879c476bd2f9e4fbf2e107f4
```

Both target states calibrated within the preregistered 0.2 mV tolerance.

```text
HYPER target       -85 mV
hold current       -0.09375 nA
achieved soma      -85.14890 mV

DEPOL target       -65 mV
hold current       +0.3203125 nA
achieved soma      -64.88600 mV
```

Both small-signal guards passed:

```text
no somatic action potential            YES
no >20 mV perturbation event           YES
target-voltage tolerance               YES
```

---

# Important state audit

The intervention did not simply shift every compartment by one common voltage.

Mean no-source receiver voltages during the fixed 200-220 ms pre-probe baseline were:

## HYPER

```text
soma[0]            -85.1489 mV
dend[54]           -85.2561
dend[67]           -85.3044
apic[14]           -82.1928
apic[37]           -76.9043
apic[71]           -72.2549
```

## DEPOL

```text
soma[0]            -64.8860 mV
dend[54]           -66.1020
dend[67]           -66.6569
apic[14]           -68.3276
apic[37]           -70.5260
apic[71]           -71.0735
```

So the cell occupies genuinely different distributed operating states. The somatic shift is ~20.3 mV, proximal basal receivers move ~18-19 mV, apic[14] moves ~13.9 mV, apic[37] ~6.4 mV, and the very distal apic[71] receiver shifts only ~1.2 mV.

That spatially nonuniform state change is part of the result, not something corrected away.

---

# Source-geometry result

## Soma-only

```text
                                      HYPER           DEPOL
entropy effective rank                3.58865         3.47372
participation rank                    1.42561         1.42805
median pairwise cosine distance       0.13079         0.13251
```

DEPOL versus HYPER distance matrix:

```text
Pearson correlation                  0.999572
Spearman correlation                 0.999118
relative Frobenius distance          0.020136
median |pair-distance change|        0.002631
90th percentile |change|             0.009807
max |change|                         0.020042
nearest-neighbour changes            0 / 16
```

## Six-port receiver set

```text
                                      HYPER           DEPOL
entropy effective rank                8.02958         7.97180
participation rank                    2.36827         2.33866
median pairwise cosine distance       0.40987         0.40071
```

DEPOL versus HYPER distance matrix:

```text
Pearson correlation                  0.999742
Spearman correlation                 0.999062
relative Frobenius distance          0.019901
median |pair-distance change|        0.003981
90th percentile |change|             0.021947
max |change|                         0.031641
nearest-neighbour changes            0 / 16
```

Entropy-rank ratio:

```text
DEPOL / HYPER soma                   0.96797
DEPOL / HYPER multi                  0.99280
```

---

# Verdict

The preregistration distinguished:

```text
Q2-A  strong state-conditioned source geometry
Q2-B  smooth metric deformation with topology preserved
Q2-C  near-isometry
Q2-D  suprathreshold failure
```

This is **Q2-C**, or at most the very weakest edge of Q2-B.

> **A ~20 mV somatic operating-state shift in the full active Hay cell leaves the normalized source-response geometry almost unchanged under this tiny perturbation.**

The pairwise geometry remains correlated above 0.999, all sixteen nearest-neighbour identities are preserved, and multi-receiver effective rank changes by less than one percent.

This is substantially more rigid than the already-modest active-conductance ablation effect in Q1.

Do not write:

```text
current state rewires the dendrite's causal geometry
```

from these tests.

The strongest statement earned here is closer to:

```text
current operating state perturbs transfer metric details,
but the local source-neighbour topology is extremely stable
for this cell in the small-signal regime.
```

---

# The sentence we were trying to kill

An earlier working sentence was:

> Different morphologies support different modes. Different local states deform those modes. Different receivers see different subsets of them. Computation may consist partly in controlling that deformation.

The Q0-Q2 sequence now lets us edit that sentence empirically.

## Clause 1

```text
Different morphologies support different transfer structure / modes.
```

Established in the field; not tested as a between-morphology claim here.

## Clause 2

```text
Different local/current states deform those modes.
```

True in a broad biophysical sense and established by voltage-dependent impedance literature, but **weak as a topology-changing statement in our measured source-signature geometry**. Q1 and especially Q2 show near-isometry in the tested small-signal regimes.

## Clause 3

```text
Different receivers see different subsets / projections.
```

This is the clause that survived strongly in Q0. Soma-only versus six-port observation changed entropy effective rank from ~3.84 to ~8.52, and every leave-one-port-out control retained a large gain.

## Clause 4

```text
Computation may consist partly in controlling that deformation.
```

**Not earned. Demote it.**

The data point toward a different next hypothesis:

> **Computation may consist partly in controlling which receiver, route, or projection gets access to a comparatively stable distributed transfer structure.**

That is a new project hypothesis, not a biological discovery claim.

---

# Why this pivot is more interesting than tuning Q2

If we increased the pulse until calcium/NMDA spikes appeared, the geometry would almost certainly become more nonlinear. But that would answer a different and much easier question: can a nonlinear event alter transfer responses?

The current surprise is the opposite:

```text
large receiver change       -> strong source-geometry change
large operating-state shift -> almost no source-neighbour change
```

The asymmetry suggests the next discovery instrument should manipulate **readout/access** while holding the physical medium fixed, rather than search for a state where the medium finally deforms enough to satisfy the old story.

That connects naturally to:

```text
multiport dendritic computation
branch-specific output
PivotPoint / accessibility
attention and routing in AI
observability / controllability
```

All of those areas have extensive prior art. The potentially useful thing is the common falsifiable measurement, not the labels.

---

# Stop condition

Do not rerun Q2 with:

```text
stronger source pulse
new source sites
new receiver sites
more extreme voltages
```

as though it were the same test.

The small-signal state-deformation branch has done its job.

## One-line handoff

> **The state-bends-geometry story largely failed the small-signal kill attempt: even -85 vs -65 mV preserves all source neighbours. The strong surviving lever is receiver projection. Pivot next toward controlled receiver/access selection, not bigger nonlinear pulses.**
