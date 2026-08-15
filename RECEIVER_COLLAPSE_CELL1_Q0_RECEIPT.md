# Receiver collapse on fixed Hay `cell1.asc` — Q0 receipt

**Date:** 2026-08-15  
**Status:** executed baseline measurement. **Not a novelty claim.**  
**Executable:** `receiver_collapse_cell1.py`  
**Preregistration / interpretation gate:** `RECEIVER_COLLAPSE_GATE.md`

## Question

On one fixed reconstructed morphology, hold the source perturbation and membrane model fixed and ask:

> How much source-specific transfer structure is visible if the observer is the soma alone, versus a small distributed receiver set?

The measurement uses the exact author-released FCI rat Hay `cell1.asc` bridge documented in `EXACT_L5_BRIDGE.md`.

This is deliberately simpler than the state-deformation question. Q0 only establishes whether **receiver choice itself** materially changes the source-response geometry on this cell.

---

# Frozen protocol

Sources:

```text
8 basal sites
8 apical sites
spread by soma path-distance order
```

Receivers:

```text
R_soma:
    soma

R_multi:
    soma
    + 2 basal sites at predeclared path-order quantiles
    + 3 apical sites at predeclared path-order quantiles
```

Stimulus:

```text
IClamp amplitude      0.02 nA
pulse duration        0.5 ms
stimulus delay        20 ms
simulation horizon    140 ms
dt                    0.05 ms
initial voltage       -70 mV
```

For source `i`, the response signature is the concatenated post-stimulus voltage response over the selected receivers. Each source signature is L2-normalized for the shape/rank analysis.

No receiver, source, pulse, metric, or threshold was optimized against the result.

---

# Two harness failures that were rejected before interpretation

## Run 1 — workflow harness failure

**Actions run:** `31887306807`

The public FCI model imported `matplotlib` through a plotting helper, but the workflow had not installed it. More importantly, the Python command was piped through `tee` without `pipefail`, so the failed Python process was incorrectly masked as a green workflow step.

Fix:

```text
install matplotlib
set -euo pipefail
```

No scientific result from run 1 was interpreted.

## Run 2 — scientific baseline contamination

**Actions run:** `31887355255`

The code ran, but every source from ~4.5 um to ~1294 um produced essentially the same reported somatic peak:

```text
~0.137108 mV
```

That is not credible as source-specific dendritic transfer. Inspection showed that the released model relaxes after `finitialize(-70)`, and the tiny perturbation had been measured on top of this common settling trajectory.

The superficially positive rank result from this run was therefore **discarded**.

Fix, without changing the frozen source/receiver/stimulus protocol:

```text
for the exact same initial state and integration settings:

    control(t) = no-stimulus trajectory
    trial_i(t) = source-i stimulus trajectory

    delta_i(t) = trial_i(t) - control(t)
```

Every IClamp is also explicitly zeroed after its run.

---

# Valid matched-control result

## Run 3

**Actions run:** `31887482755`  
**Commit:** `fb8a4925fbfdd788d258c380b020fffdb156dcd4`

After matched no-stimulus subtraction, the somatic peaks behaved like an actual dendritic transfer measurement.

Representative range:

```text
proximal apical  ~7.7 um      0.112432 mV
proximal basal   ~4.5 um      0.104140 mV
basal           ~276 um       0.015404 mV
apical          ~756 um       0.003781 mV
apical         ~1294 um       0.000916 mV
```

The discarded common settling transient itself was ~0.137141 mV at the soma, confirming why exact matched subtraction mattered.

### Soma-only versus six-port receiver set

```text
                                  SOMA ONLY       SOMA + 5 DENDRITIC PORTS
entropy effective rank             3.8384                8.5159
participation rank                 1.6211                2.6648
median pairwise cosine distance    0.2065                0.4988
median nearest cosine distance     0.00487               0.01626
```

Ratios:

```text
entropy-rank ratio          2.2186 x
participation-rank ratio    1.6439 x
```

Thus the fixed soma projection collapses source distinctions that are visible at a small distributed receiver set.

---

# Near-source receiver robustness check

Inspection found **one** source/receiver pair on the same named section:

```text
source:   dend[67](0.9444), soma path ~170.5 um
receiver: dend[67](0.7222), soma path ~146.7 um
```

That source produced a much larger local response at the multiport receiver set (~3.62 mV) than most other local traces. The main Q0 result could therefore have been carried by one lucky nearby port.

Instead of moving or replacing the receiver after seeing the data, the exact same traces were subjected to a frozen receiver jackknife.

## Run 4 — leave-one-receiver-out and soma+one controls

**Actions run:** `31887582840`  
**Commit:** `6dac8688994d42f0e83d88ef241d4a8132b67235`

For each of the five dendritic receivers:

```text
keep soma
remove exactly that receiver
recompute normalized source-signature geometry
```

Result:

```text
leave-one-out entropy-rank ratio vs soma-only:
    minimum   1.9309 x
    maximum   2.1179 x

soma + exactly one dendritic receiver:
    minimum entropy-rank ratio   1.1723 x
    maximum entropy-rank ratio   1.4406 x
```

So no single dendritic port is carrying the multi-receiver effect.

---

# Verdict

> **Q0 RECEIVER COLLAPSE: YES, FOR THIS FIXED CELL AND PROTOCOL.**

A soma-only readout and a small distributed receiver set do **not** see equivalent source-response geometry, even after source signatures are normalized so the result is not merely distal attenuation.

The effect survives removal of every individual dendritic receiver.

This does **not** mean:

```text
we discovered dendritic compartments               NO
we discovered multiport neurons                    NO
we discovered transfer impedance                   NO
more receivers automatically means more cognition  NO
this rescues exact STP-address binding              NO
```

Transfer impedance, electrical compartmentalization, branch functional subunits, and reduced models preserving selected dendritic transfer structure are established literature.

Useful anchors include:

- Wybo et al. 2021, eLife, data-driven reduction preserving dendro-somatic responses: https://doi.org/10.7554/eLife.60936
- Das & Narayanan 2018, state-dependent transfer impedance / resonance in L5 pyramidal neurons: https://doi.org/10.3389/fncom.2018.00029
- parallel functional architectures within one dendritic tree, Neuron 2023: https://doi.org/10.1016/j.neuron.2023.03.015
- Aizenbud et al. / TwinProp 2026, learned coarse apical/basal functional subunits and interaction of NMDA with active dendritic conductances: https://doi.org/10.64898/2026.06.08.730984

The value of Q0 is narrower: it validates the **receiver-relative source-signature measurement** on the exact morphology already shared across the FCI / Hay bridge.

---

# What Q0 changes

The V23 exact-address experiments treated anatomical segment identity as the candidate coordinate:

```text
STP tuple <-> exact dendritic address
```

Those tests were correctly null in passive and smooth-threshold regimes.

Q0 suggests a better *measurement coordinate* for future tests without rewriting those nulls:

```text
source location
    -> response signature under receiver set R and state x
    -> receiver-visible source geometry
```

Two micrometrically distinct addresses may be nearly equivalent to one receiver. Conversely, a distributed receiver set can separate addresses that the soma collapses.

This is an operational quotient induced by the observation map, not a claim that raw morphology disappears.

---

# Q1 is now earned

Keep **exactly the same anatomy, source set, receiver set, and response metric**.

Change only the realized membrane / synaptic state or mechanism stack.

The next question is:

> **Does the normalized receiver-visible source geometry itself deform when the cell's operating state / active mechanisms change?**

Schematically:

```text
d_x0(i,j | R,T)  ?=  d_x1(i,j | R,T)
```

The interesting result is not gain scaling. It requires source relationships to split, merge, rotate, or reorder.

A disciplined ladder is still:

```text
P0  current FCI passive-dendrite cell
P1  fixed morphology + common AMPA/NMDA operating regime
P2  one validated active dendritic mechanism / holding state
P3  full active Hay dendrite model on the same cell1.asc
```

Do not hand-write another arbitrary nonlinearity merely to make Q1 positive. Use author-released mechanisms / models where possible.

## One-line handoff

> **The soma is a severe but not total projection of this fixed morphology: a five-port distributed readout roughly doubles the entropy rank of normalized source transfer signatures, and the effect survives every single-receiver jackknife. Now freeze the geometry and ask whether biological state changes the receiver-visible source geometry itself.**
