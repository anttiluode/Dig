# Q1 receipt — fixed morphology, active-dendrite operator deformation

**Date:** 2026-08-15  
**Status:** executed preregistered gate. **Q1-B / near-isometry under the resting small-signal probe.**  
**Gate:** `STATE_DEFORMATION_Q1_GATE.md`  
**Executable:** `receiver_state_deformation_cell1.py`

## Provenance

Model code:

```text
SelfishGene/neuron_as_deep_net
commit 074c4666300a8ad246601dab179a97a6942f0f29
```

Morphology:

```text
L5PC_NEURON_simulation/morphologies/cell1.asc
```

This is the byte-identical `cell1.asc` already linked to the FCI bridge in `EXACT_L5_BRIDGE.md`.

The full active condition uses the released Hay/Beniaguev HOC biophysics. The matched ablation keeps morphology, passive cable, soma/axon mechanisms, source/receiver coordinates and probe fixed, while setting the maximal **dendritic** active conductances to zero.

This is our explicit mechanism ablation, not a claim to reproduce an author's named passive-dendrite dataset condition.

---

# Compatibility failure before biology — rejected

Initial Actions run:

```text
31887836808
```

failed before the experiment because NEURON 9.0.2 cannot compile the old probabilistic synapse MOD files without C++-migration changes. The generated code declares

```text
void* nrn_random_arg(int)
```

while current NEURON declares a typed `Rand*` return.

Q1 does not instantiate any synaptic point process; it uses `IClamp` only. Therefore the workflow was changed to compile only the twelve released membrane/state mechanisms actually required by `L5PCbiophys5b.hoc`:

```text
CaDynamics_E2
Ca_HVA
Ca_LVAst
Ih
Im
K_Pst
K_Tst
NaTa_t
NaTs2_t
Nap_Et2
SK_E2
SKv3_1
```

No model parameter, source, receiver, pulse, metric, or interpretation gate was changed.

---

# Valid run

Actions run:

```text
31887917574
```

Dig commit:

```text
19db42ff20d6f58d04341cdc5dc815cd7e9e4028
```

The selected membrane mechanisms compiled under NEURON 9.0.2 and the full preregistered ACTIVE and DENDRITE_ABLATED conditions completed successfully.

## Ablation audit

The ablation set zeroed the intended attributes over the released dendritic segments:

```text
gSK_E2bar_SK_E2          377 segment values
gCa_LVAstbar_Ca_LVAst    377
gCa_HVAbar_Ca_HVA        377
gSKv3_1bar_SKv3_1        377
gNaTs2_tbar_NaTs2_t      377
gImbar_Im                 377
gIhbar_Ih                 639
```

Both preregistered safety guards passed:

```text
no somatic spike                         YES
no >20 mV perturbation-induced event     YES
```

The largest perturbation-relative local response was ~3.19 mV, from the already-known source/receiver-nearby `dend[67]` case.

---

# Result

## Soma-only source geometry

```text
                                      ACTIVE        DENDRITE_ABLATED
entropy effective rank                3.50545          3.40031
participation rank                    1.40234          1.41278
median pairwise cosine distance       0.12473          0.12008
```

ACTIVE versus DENDRITE_ABLATED pairwise source-distance matrix:

```text
Pearson correlation                  0.995834
Spearman correlation                 0.996840
relative Frobenius distance          0.072657
median |pair-distance change|        0.008974
90th percentile |change|             0.031743
max |change|                         0.072033
nearest-neighbour changes            0 / 16
```

## Six-port source geometry

```text
                                      ACTIVE        DENDRITE_ABLATED
entropy effective rank                7.96945          7.53119
participation rank                    2.33171          2.16363
median pairwise cosine distance       0.41161          0.33430
```

ACTIVE versus DENDRITE_ABLATED pairwise source-distance matrix:

```text
Pearson correlation                  0.995571
Spearman correlation                 0.991604
relative Frobenius distance          0.104012
median |pair-distance change|        0.032524
90th percentile |change|             0.096238
max |change|                         0.121695
nearest-neighbour changes            0 / 16
```

Rank ratios:

```text
ACTIVE / ABLATED soma entropy rank   1.03092
ACTIVE / ABLATED multi entropy rank  1.05819
```

---

# Verdict

The preregistered Q1-B branch says:

> If normalized source-distance matrices remain highly concordant and neighbour identities are mostly preserved, call the stronger `state/operator -> geometry deformation` reading weak under this protocol.

That is the observed result.

> **Q1-B: RESTING SMALL-SIGNAL SOURCE GEOMETRY IS CLOSE TO AN ISOMETRY UNDER DENDRITIC-ACTIVE-CONDUCTANCE ABLATION.**

The full released dendritic conductance set changes amplitudes and modestly expands the distributed receiver signature space, but it does **not** materially reorder the source geometry under this tiny rest-state perturbation. All sixteen nearest-neighbour identities are preserved, and the pairwise-distance matrices remain correlated at ~0.996 (Pearson) / ~0.992 (Spearman) for the multi-receiver view.

So do not write:

```text
active dendrites bend the causal geometry dramatically
```

from Q1.

A more accurate statement is:

```text
at the resting small-signal operating point,
active dendritic conductances deform the metric modestly
while preserving the source-neighbour topology almost exactly.
```

---

# Why this is useful

The result cleanly separates two claims that were being blurred in the earlier Clockfield / V23 language.

Q0 established:

```text
receiver choice strongly changes how much spatial transfer structure is visible.
```

Q1 says:

```text
removing the released dendritic active conductances at rest
changes that visible geometry far less than changing the receiver projection.
```

For the six-port view:

```text
Q0 receiver change:
    soma entropy rank 3.84 -> multi 8.52   (~2.22x)

Q1 mechanism change:
    ablated multi 7.53 -> active 7.97      (~1.06x)
```

These are different comparisons/models, so the ratios are not a formal effect-size contest. But they point in a useful direction: **receiver projection is currently the stronger measured lever than rest-state dendritic conductance removal.**

---

# Relation to established literature

This does not challenge the established result that active conductances and membrane potential can strongly alter dendritic transfer impedance, resonance, nonlinear events, and task computation. Q1 probes one deliberately tiny perturbation around one resting operating regime and then normalizes source signatures before comparing geometry.

That narrowness matters.

The null is only:

> **No strong topological reorganization of the normalized source-response geometry under this resting small-signal active-versus-ablated comparison.**

---

# What not to do next

Do not tune:

```text
pulse amplitude
pulse duration
source set
receiver set
normalization
```

until this gate becomes positive.

Do not call a larger nonlinear pulse a rerun of Q1. It would be a different experiment.

---

# The next sharper distinction

Q1 changed the **mechanism set** and therefore the operator family. It did not isolate the stronger Clockfield-like sentence:

```text
same anatomy + same mechanisms
but different current operating state
-> different realized transfer geometry
```

That question is already known in transfer-impedance/resonance literature to have voltage dependence, so it is not a novelty claim either.

If pursued, it should be a separately preregistered Q2:

```text
full active Hay cell only
same morphology
same mechanisms
same source / receiver set
same tiny probe

hold the system at two or more controlled subthreshold operating points
measure the same normalized source-distance matrices
```

The important comparison would again be topology / neighbour reordering versus smooth metric deformation.

If even large subthreshold state shifts preserve the source-neighbour geometry, then the broad phrase `state bends geometry` should be demoted further to a gain/time-constant statement for this cell.

## One-line handoff

> **Q0: receiver choice changes the visible source geometry strongly. Q1: deleting the released dendritic active conductances at rest changes it only modestly and preserves every source's nearest neighbour. The next honest test, if desired, is same mechanisms at different controlled operating states—not a bigger pulse.**
