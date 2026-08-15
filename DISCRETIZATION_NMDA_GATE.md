# FCI discretization x NMDA: separate cable resolution from synapse co-location

**Status:** released-code audit + convergence experiment. Not a finding about FCI yet.  
**Date:** 2026-08-15.

## 0. Why this gate exists

Aizenbud et al. describe the input as one excitatory AMPA+NMDA synapse and one inhibitory GABAA synapse per 1 um of dendritic length. The released implementation preserves roughly that number of *initial input sources*, but does not instantiate one point process at every micrometre.

Instead it deliberately keeps the number of dendritic simulation segments near ~1040 per morphology, creates one excitatory and one inhibitory point process per segment, and collapses the sources belonging to that segment into the event weight delivered at that one point.

That is a reasonable numerical approximation if it is converged.

Because NMDA current is locally voltage dependent, however, convergence must be demonstrated rather than assumed.

The important word is **convergence**. This note does not call the released result an artefact.

---

## 1. The released HOC rule

At FCI commit

```text
55826436751c03a32dfd39e91a48894869e1db57
```

`passive_dends_simple_soma_model.hoc` sets

```hoc
nseg = 1 + 2*int(L/chunkSize)
```

and the four complete released wrappers use different `chunkSize` values chosen to land at about the same segment count.

The corresponding released `properties.json` files give:

```text
cell                  chunk (um)   avg segment (um)   rho_soma   rho_axon
rat L2 BBP               9.195          4.595          30.95      127.00
rat L5 Hay              24.30          12.079          32.59      247.23
human L2/3 Eyal         40.00          19.839          72.76      658.88
human L5 BBP            53.10          25.976          48.18      462.94
```

So the average physical length represented by one dendritic input channel differs by about

```text
25.976 / 4.595 ~= 5.65 x
```

between these two endpoints.

Equal channel count therefore removes the trivial `bigger tree -> more TCN input channels` confound, but it creates a different numerical question: **does one channel represent the same spatial scale across cells?**

---

## 2. What is collapsed onto a segment

In `simulate_neuron.py` the default source count is

```python
count_exc_initial_synapses_per_super_synapse = ceil(seg_len)
```

(and likewise for inhibition).

The initial spike trains assigned to successive segments are disjoint. For one segment, their spikes are multiplied by random scalar weights and summed into a single `weighted_spikes` vector.

During the NEURON run, each nonzero weighted event is delivered to the one point process at that segment with

```text
NetCon weight = original synaptic weight * aggregate weighted event
```

Thus the approximation is schematically

```text
~1 source / um along a piece of dendrite
          |
          | collect all sources belonging to segment i
          v
one AMPA+NMDA point process at segment i
```

This preserves input-source count much better than a literal one-synapse-per-segment model would.

But it also concentrates all conductance assigned to that segment at one electrical location.

For a voltage-independent linear membrane this can converge rapidly as segments are refined. With NMDA it is potentially more delicate because local depolarization changes the conductance itself.

---

## 3. Correction to a tempting interpretation

The simulator contains the option

```text
--force_multiply_count_spikes_per_synapse_per_100ms_range_by_average_segment_length
```

but its declared default is `False`.

Therefore do **not** state that the production FCI simulations compensated mean firing rate with this option unless the exact production command/configuration is recovered.

The ordinary source-count scaling already occurs through `ceil(seg_len)`.

Production command-line arguments may override defaults; the released code inspected so far does not establish whether this particular flag was enabled in the paper runs.

---

## 4. Why NMDA makes this worth testing

The paper reports a steep local NMDA transition for the modeled human synapse around roughly 35 simultaneously activated synapses in its Fig. 4 experiment.

Earlier Eyal work likewise places independent NMDA events on a local dendritic spatial scale rather than treating the entire tree as one lumped nonlinearity.

A segment representing ~20--26 um is therefore not obviously infinitesimal relative to the spatial scale of the nonlinear event.

That observation is **not enough to diagnose bias**. It only says the numerical approximation sits close enough to the mechanism's spatial scale that a refinement test is justified.

Related reduction work by Wybo et al. (eLife 2021, DOI `10.7554/eLife.60936`) also shows that relocating/grouping nonlinear synaptic input can change NMDA-spike behavior unless the reduced model is specifically fitted to preserve it.

---

## 5. Do not run one naive chunk sweep and call it solved

Changing `chunkSize` in the released model changes two things at once:

```text
A. numerical resolution of the cable equation
B. spatial aggregation of synaptic input
```

If the result changes, a naive sweep cannot tell which one caused it.

The gate therefore has two stages.

### D0 — joint refinement screen

On one fixed morphology (start with exact Hay `cell1.asc`), rerun the same local input experiment with

```text
chunk = native
chunk = native / 2
chunk = native / 4
chunk = native / 8
```

while preserving the same physical input window, total conductance per micrometre and event times.

Run both

```text
AMPA_ONLY
RAT_NMDA
```

If both are already stable, the discretization concern largely dies for that test.

If NMDA changes strongly while AMPA is stable, continue to D1/D2.

### D1 — cable-resolution control

Use a sufficiently fine cable grid for all conditions, then keep the physical synaptic locations fixed.

This tests cable-equation discretization without changing contact aggregation.

### D2 — contact-aggregation control

Keep the fine cable grid fixed, but bin the same underlying 1/um input sources into point processes at progressively coarser spatial scales.

For example

```text
1--3 um bins
6 um bins
12 um bins
24 um bins
```

Preserve exactly:

```text
underlying source spike trains
total conductance
physical branch/window
gamma and kinetics
```

Only the spatial co-location approximation changes.

This is the gate that directly tests whether coarse grouping artificially helps or hurts local NMDA recruitment.

---

## 6. The most informative plot

For a fixed branch/window plot local and somatic response versus equivalent simultaneously activated synaptic length/count:

```text
AMPA_ONLY: fine vs coarse aggregation
RAT_NMDA: fine vs coarse aggregation
```

Extract a knee only after defining a rule independent of the condition, for example maximum curvature or a predeclared supralinearity ratio.

Then report

```text
Delta_knee(chunk/bin size)
Delta_local_peak
Delta_soma_peak
```

The desired result for the published approximation is convergence, not a particular direction.

---

## 7. If the local gate is sensitive, then test the actual FCI input statistics

A Fig. 4-style synchronous cluster is deliberately adversarial. FCI uses stochastic input.

If D0--D2 show sensitivity, replay the actual FCI-like stochastic drive on the same morphology with the *same underlying source spike trains* under fine versus native aggregation.

Measure before training any DNN:

```text
local NMDA current distribution
local plateau / supralinearity frequency
somatic voltage difference
spike disagreement rate
```

Only if those differ materially is it worth paying for a fixed-TCN FCI retraining.

---

## 8. A separate but related scale: the TCN does not rescue bad physics

The FCI TCN sees approximately matched segment-level channels, which is good experimental hygiene for the surrogate.

But a fixed TCN can only emulate the simulated neuron it is given. If spatial aggregation changes the simulated neuron's nonlinear I/O map, equal TCN input dimensionality does not remove that difference.

Conversely, if refinement leaves the detailed-neuron I/O map unchanged, then the matched ~1040-channel design has done its job and this concern should be retired.

---

## 9. Kill conditions

Drop the discretization branch if:

```text
1. local AMPA and NMDA curves are stable under >=4x refinement;
2. fixed-cable contact aggregation is likewise stable;
3. stochastic FCI-like replay shows negligible spike/voltage disagreement.
```

Escalate only if the effect is both nonlinear-specific and large enough to alter the simulated I/O function.

## Source-code anchors

- `ido4848/FCI`, `passive_dends_simple_soma_model.hoc` — segmentation rule.
- four released `properties.json` files — native chunk and average segment lengths, rho values.
- `simulating_neurons/neuron_models/model_utils.py` — one excitatory/inhibitory point process per dendritic segment.
- `simulating_neurons/simulate_neuron.py` — `ceil(seg_len)` initial sources, aggregation to segment-level weighted events, runtime NetCon weights.
- Aizenbud et al. PNAS 2026, DOI `10.1073/pnas.2533168123` — one synapse/um description and Fig. 4 nonlinear synapse experiment.
- Wybo et al. eLife 2021, DOI `10.7554/eLife.60936` — reduced morphology / NMDA-spike preservation.

## Current sentence

> **The FCI code equalizes input-channel count by changing physical segment scale. That is not automatically a flaw. Because the same segmentation also sets the spatial binning of a voltage-dependent NMDA mechanism, the right question is numerical convergence: first refine the cable, then separately refine the contact aggregation, and only call it biology if both are stable.**
