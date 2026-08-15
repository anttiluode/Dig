# The “human synapse” is a bundle: split kinetics, conductance and Mg-block slope

**Status:** released-code audit + cheap factorial experiment. Not a new biological claim.  
**Date:** 2026-08-15.

## 0. One more thing hidden inside Fig. 4

The Aizenbud paper compares four excitatory synapse parameter sets:

```text
rat
rat + human gamma
human + rat gamma
human
```

That is useful, but it does not independently vary every biological parameter that differs between the released rat and human synapse models.

The released code shows that “human synapse” bundles together several changes at once.

---

## 1. Released parameters

At FCI commit `55826436751c03a32dfd39e91a48894869e1db57`:

```text
                            rat             human
AMPA tau_r (ms)             0.2              0.3
AMPA tau_d (ms)             1.7              1.8
AMPA peak g                  0.0004           0.00088

NMDA tau_r (ms)             0.29             5.0
NMDA tau_d (ms)             43               43
NMDA/AMPA ratio             0.75             0.00131/0.00088 ~= 1.489
Mg-block gamma (/mV)        0.062            0.078
```

Therefore the nominal NMDA peak-conductance scale is

```text
rat:   0.0004  * 0.75   = 0.000300
human: 0.00088 * 1.489  = 0.001310
```

or about **4.37x larger** in the human parameter set.

The NMDA rise constant changes

```text
5 / 0.29 ~= 17.24x.
```

With the same 43 ms decay constant, the normalized double-exponential time-to-peak changes from roughly

```text
rat:   1.46 ms
human: 12.17 ms
```

while `gamma` changes by about 26%.

So “human NMDA” is not one scalar difference.

---

## 2. What the published hybrids actually isolate

The four released parameter sets are a valid 2 x 2 design if the factors are defined as

```text
G = Mg-block slope gamma
    rat / human

B = everything else in the excitatory synapse bundle
    rat / human
```

Then

```text
rat                 = G_rat   + B_rat
rat_human_gamma     = G_human + B_rat
human_rat_gamma     = G_rat   + B_human
human               = G_human + B_human
```

That means Fig. 4 can reveal whether the human `gamma` interacts with the **rest of the human synapse bundle**.

It cannot tell us which part of `B_human` matters:

```text
larger AMPA conductance
larger NMDA conductance ratio
much slower NMDA rise
small AMPA kinetic change
some interaction among these
```

This is an identifiability issue, not a criticism of the question the paper chose to ask.

---

## 3. Why the 17x rise-time change deserves its own gate

The NMDA mechanism is normalized so the peak conductance is specified independently of the rise/decay constants.

Changing `tau_r_NMDA` therefore changes **when and for how long the conductance approaches its peak**, not simply its nominal peak amplitude.

That can alter:

```text
coincidence window
local voltage trajectory
amount of Mg-block relief before peak
interaction among sequential inputs
how much recent input history is retained
```

This is directly relevant to a temporal surrogate such as the FCI TCN.

It is also exactly the kind of mechanism that a “time as geometry” intuition should translate into mundane language as **different temporal kernels**, not a new physical oscillation.

---

## 4. Do the cheap branch experiment before another FCI run

On one fixed morphology and one fixed dendritic branch, use the same simultaneous and jittered input patterns under a small preregistered parameter matrix.

A useful decomposition is:

```text
R0  rat baseline

R1  rat + human gamma only
R2  rat + human NMDA peak conductance only
R3  rat + human NMDA rise kinetics only

R4  rat + human peak conductance + human gamma
R5  rat + human kinetics + human gamma
R6  rat + human peak conductance + human kinetics

R7  full human excitatory set
```

For an even cheaper first pass, use only `R0`, `R1`, `R2`, `R3`, `R7`.

Keep morphology, inhibitory mechanism, input locations and total event pattern fixed.

Record:

```text
local peak voltage
somatic EPSP
NMDA current peak and integral
supralinearity ratio
knee location under synchronous count sweep
response to temporal jitter
```

The purpose is parameter attribution, not species inference.

---

## 5. Temporal jitter may distinguish amplitude from kinetics

A synchronous Fig. 4-style input count sweep is excellent for the nonlinear knee but can hide the role of kinetics.

Add a second stimulus family in which the same events are jittered over, for example,

```text
0 ms
5 ms
10 ms
20 ms
40 ms
```

Do not optimize these windows after seeing results.

A conductance-amplitude effect should remain visible under many timing patterns.

A slow-rise/temporal-integration effect may reveal itself as a different sensitivity to jitter and event history.

That gives the 17x kinetic difference somewhere to show itself without requiring a GPU-trained FCI surrogate.

---

## 6. Connect back to the Green/NMDA closure carefully

In the quasi-static reduction

```text
Z_eff = (I - ZK)^(-1) Z
```

`gamma` and instantaneous local conductance directly affect the incremental gain `K(v,t)`.

The rise/decay constants determine the **trajectory of K through time**.

So a more faithful object is not one fixed matrix `ZK`, but a state/time-dependent sequence

```text
L(t) = Z(t) K(t)
```

or, in the full dynamics, the time-varying Jacobian of membrane + synaptic state.

This is another reason not to collapse human/rat NMDA differences into a single static scalar.

---

## 7. Relation to FCI

Only after the local parameter matrix is understood should the expensive question be asked:

```text
which parameter changes increase FCI?
```

Possible outcomes:

```text
local nonlinear knee changes but FCI does not
    -> FCI is insensitive to that mechanism under its drive distribution

FCI changes mainly with conductance amplitude
    -> simpler gain/nonlinearity explanation

FCI changes strongly with kinetics at matched local peak
    -> temporal memory/history is a real component

only the combined human parameter set moves FCI
    -> strong interaction, consistent with the published hybrid pattern
```

This is more informative than treating “human synapse” as one feature column.

## Code/source anchors

- `ido4848/FCI/simulating_neurons/neuron_models/model_utils.py` — exact four released parameter sets.
- Aizenbud et al. PNAS 2026, DOI `10.1073/pnas.2533168123`, Fig. 4 and Methods — rat/human/hybrid synapse comparison.
- `AMPANMDA_EMS.mod` — normalized double-exponential conductance and voltage-dependent Mg block.

## Current sentence

> **The published hybrid experiment cleanly separates human `gamma` from a bundled “everything else” synapse factor, but that bundle contains a 4.37x NMDA peak-conductance change and a 17.2x NMDA rise-time change. Split those cheaply at one branch before asking FCI to tell us which biology matters.**
