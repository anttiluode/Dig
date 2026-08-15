# Mechanism candidate: FCI may measure nonlinear compartment capacity, not morphology spectrum

**Status:** derived hypothesis from primary literature + released FCI architecture. Not a result.

The Green-function direction became more precise after three literature collisions:

1. passive dendrites already have an exact linear transfer description (Green functions / impedance kernels);
2. the Neural Evaluation Tree already turns the impedance matrix into functional dendritic compartments;
3. local NMDA nonlinearities are known to be the main source of depth in DNN surrogates of detailed cortical neurons.

This suggests a cleaner mechanistic model for Aizenbud's FCI.

## 1. Passive morphology by itself is a linear spatiotemporal operator

For small signals in a passive or linearized dendrite, with synaptic input currents `u_i(t)` at locations `i`, somatic voltage can be written schematically as

```text
v_soma(t) = sum_i (h_soma<-i * u_i)(t)
```

where each `h` is a Green/transfer-impedance kernel.

Equivalently, at many dendritic locations,

```text
v_j(t) = sum_i (h_j<-i * u_i)(t).
```

Morphology matters strongly: it determines every kernel. But the operation is still linear convolution.

This creates an important prediction:

> **A large or morphologically elaborate passive tree need not imply a deep nonlinear surrogate. Its geometry may be complicated while its I/O law remains a linear filter bank plus the soma/axon output nonlinearity.**

This is consistent with the Beniaguev et al. 2021 result: when NMDA receptors were removed from a detailed L5 pyramidal-cell model, a much simpler artificial network could reproduce its I/O than was required for the full NMDA model.

It is also a warning against interpreting our earlier `kernel effective rank` as FCI itself. A convolutional surrogate is built precisely to represent temporal filters efficiently.

## 2. NMDA turns the transfer operator into a coupled nonlinear system

For an NMDA synapse, local current depends on local voltage. Schematically,

```text
I_i(t) = g_i(t) * B(v_i(t)) * (E_NMDA - v_i(t))
```

with voltage-dependent magnesium block represented by `B(v)`.

But local voltage is itself produced by the dendritic transfer system:

```text
v_j(t) = sum_i h_j<-i * I_i(t) + other currents.
```

Substitution closes the loop:

```text
morphology / cable kernels H
        +
local voltage-dependent synaptic functions N_i
        ->
coupled nonlinear spatiotemporal system.
```

Now morphology is not merely filtering inputs on the way to the soma. It determines **which local nonlinearities can influence one another**.

That is exactly where impedance-based compartmentalization becomes mechanistically relevant.

## 3. Two ingredients are required for many useful nonlinear subunits

A potential dendritic subunit needs at least two things:

```text
LOCAL NONLINEARITY
    clustered input can create a regenerative local event

ELECTRICAL INDEPENDENCE
    that event does not force other candidate regions into the same effective state
```

Strong local NMDA without compartmentalization gives a strongly nonlinear but globally coupled object.

Strong compartmentalization without local nonlinearity gives many electrically distinct but mostly linear filters.

The computationally rich regime may require **both**.

This reframes Eyal et al. 2018. Their maximal number of independent simultaneous NMDA spikes is already a direct operational measurement of this conjunction:

```text
nonlinear event possible locally
AND
events remain mutually independent through the cable tree.
```

The human L2/3 models in that work supported roughly 25 such simultaneous events versus roughly 14 in rat L2/3 models.

## 4. Candidate interpretation of the 2026 FCI

Aizenbud's FCI asks how difficult it is for a fixed TCN to emulate the full neuron.

Beniaguev et al. 2021 showed that NMDA-dependent dendritic dynamics are a main reason a deep temporal network is needed in the first place.

Therefore a more mechanistic hypothesis than "large morphology = high FCI" is:

> **H_NCC — Nonlinear Compartment Capacity:** FCI rises when morphology and local biophysics create a larger repertoire of partially independent, voltage-dependent dendritic computations that must be represented simultaneously by the surrogate network.

`NCC` is only a working label for the hypothesis, not a proposed standard metric.

The old Eyal simultaneous-NMDA-subunit count is one concrete estimator. NET/`I_Z` gives a linear electrical estimator of the independence side. Aizenbud's NMDA intervention provides the nonlinear side.

## 5. This makes a sharp prediction across cortical layers

Aizenbud 2026 reports a striking layer inversion:

```text
human: FCI highest in L2/3
rat:   FCI highest in L5
```

If nonlinear compartment capacity is a major mechanism, then an electrical/nonlinear subunit measure should show a related layer ordering.

This is a much stronger test than human-vs-rat average separation.

### Prediction P1

Under common synaptic parameters, impedance/NET-derived compartmentalization should predict the **morphology-only FCI** across cells better than simple branch count, and ideally add held-out value beyond area + path/branch-allocation baselines.

### Prediction P2

The cell/layer ordering of an Eyal-style independent-NMDA-subunit measure should correlate with the ordering of FCI. In particular, ask whether it reproduces the human L2/3 versus rat L5 peaks.

### Prediction P3

Changing NMDA parameters while holding morphology fixed should alter FCI without changing passive NET geometry. If an active/state-dependent NET or direct nonlinear independence measure changes in parallel, that identifies the missing state-dependent term.

### Prediction P4 — useful falsifier

If passive/NET compartment count predicts morphology-only FCI but fails to predict the additional complexity caused by human NMDA parameters, then morphology and synaptic nonlinearity are genuinely separable mechanisms rather than one generic "geometry" effect.

That would still be a useful result.

## 6. A possible reason the Aizenbud morphology regressions stop at area/path

The 2026 paper finds total dendritic area to be its strongest single structural predictor, with long bifurcation-path structure adding value and raw bifurcation count much weaker.

That pattern is compatible with several mechanisms, so it does not by itself establish NCC.

But it makes a specific alternative possible:

```text
area / long paths
     -> electrotonic separation + local input impedance
     -> organization of independent nonlinear regions
     -> more difficult global I/O map
     -> higher FCI
```

The existing paper tests the left and right ends of this chain.

The proposed Dig experiment tests the **middle**.

If the middle does not mediate or predict the relationship, drop the hypothesis.

## 7. The most interesting negative result is already imaginable

Cuntz et al. 2021 show that for distributed synaptic activation, overall spike counts/rates can be surprisingly invariant to dendritic size and shape even though **spike timing remains morphology-dependent**.

This suggests a competing possibility:

> Aizenbud FCI may be sensitive not mainly to a larger number of nonlinear subunits, but to the richer **temporal organization** of how those subunits influence the soma.

That brings Green kernels back in—but now in the right place.

If Eyal/NET compartment count alone fails, test whether adding temporal kernel structure between the candidate subunits and the soma explains the residual FCI.

The ladder becomes:

```text
1. static morphology
2. DC electrical compartmentalization (Z, I_Z, NET)
3. temporal electrical compartmentalization (z_ij(t))
4. nonlinear local events (NMDA)
5. full I/O complexity (FCI)
```

Each rung can be asked whether it explains variance left by the previous rung.

## 8. Why this is also the disciplined descendant of the "time as geometry" thought

There is no need to claim that dendrites instantiate spacetime.

The established mathematics already says:

```text
morphology + membrane state
        -> transfer kernels between locations
        -> electrical interaction / independence
        -> which local nonlinear events can coexist
        -> future somatic trajectories
```

So the useful remnant of the intuition is:

> **The computational meaning of a location is not exhausted by where it is anatomically. It is also given by what temporal influence that location can exert on other locations and on the receiver, in the current operating regime.**

That statement is cable theory plus nonlinear dynamics. The question for Dig is whether this established local interaction geometry explains the new FCI target better than the coarse structural and global-spectral summaries already tested.

## Primary-source anchors

- Wybo, Stiefel & Torben-Nielsen 2013, arXiv:1309.2382 — Green-function dendritic transfer.
- Eyal et al. 2018, Front. Cell. Neurosci. 12:181 — independent simultaneous NMDA spikes as a functional-complexity index.
- Wybo et al. 2019, Cell Reports 26:1759-1773.e7 — NET and impedance-based independence index; dynamic recompartmentalization.
- Beniaguev, Segev & London 2021, Neuron 109:2727-2739.e3 — deep DNN surrogate; NMDA removal dramatically simplifies the required surrogate.
- Cuntz et al. 2021, Neuron 109:3647-3662.e7 — morphology-invariant spike counts under distributed input but morphology-dependent spike timing.
- Aizenbud et al. 2026, PNAS 123:e2533168123 — deep-learning FCI across rat/human layers and morphology/NMDA interventions.
