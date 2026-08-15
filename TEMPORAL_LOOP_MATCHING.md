# Temporal loop matching: the NMDA rise time is an envelope on the feedback, not a new pole in `K`

**Status:** released-code audit + derived experiment. Not a result.  
**Date:** 2026-08-15.

## 0. The useful correction

A tempting next step from

```text
Z_eff = (I - ZK)^(-1) Z
```

is to make everything frequency-dependent and write

```text
L(omega) = Z(omega) K(omega)
```

and then say that the NMDA rise/decay kinetics live inside `K(omega)`.

For the **released Aizenbud FCI NMDA mechanism**, that is not quite right.

The NMODL synapse has two different pieces:

```text
presynaptic event
    -> dual-exponential NMDA conductance state g_N(t)

local voltage v
    -> instantaneous Mg-block factor B(v)
```

The NMDA conductance state variables decay with fixed time constants and do not themselves depend on voltage. Voltage enters through the instantaneous magnesium gate and the driving force.

Therefore, around a transient event, the incremental voltage feedback is better written as a **time-varying local gain**

```text
K_t = d I_N(v, g_N(t)) / d v | v*(t)
```

rather than assuming one stationary transfer function `K(omega)` containing the receptor rise/decay poles.

The full transient linearization is a linear-time-varying system.

A useful frozen-time approximation is

```text
L_t(omega) = Z(omega) K_t
```

where the cable supplies the frequency dependence and the synaptic conductance envelope moves the loop gain through time.

The slower human rise therefore matters because it changes **when and for how long the cell visits high-feedback operating states relative to the cable's own relaxation**, not because the FCI magnesium gate itself contains a 5 ms dynamical pole.

---

## 1. The passive membrane time constant is exactly 20 ms in the released model

The released HOC uses

```text
soma / axon:
    cm    = 1 uF/cm2
    g_pas = 1/20000 S/cm2

apical / basal dendrite:
    cm    = 2 uF/cm2
    g_pas = 2/20000 S/cm2
```

so in both cases

```text
tau_m = cm / g_pas = 20 ms.
```

The paper-nominal values (`Cm = 1 uF/cm2`, `Rm = 20000 Ohm cm2`) also imply the same 20 ms passive membrane time constant.

The dendritic tree has a spectrum of cable modes with time constants generally at or below this membrane scale, so `20 ms` is not the only relevant temporal constant. It is nevertheless a useful reference scale.

---

## 2. Rat and human NMDA kernels occupy very different fractions of that scale

Released FCI parameters:

```text
rat NMDA:
    tau_r = 0.29 ms
    tau_d = 43 ms

human NMDA:
    tau_r = 5 ms
    tau_d = 43 ms
```

For a normalized dual exponential

```text
g(t) = A [exp(-t/tau_d) - exp(-t/tau_r)]
```

with the peak normalized to one,

```text
t_peak = tau_r * tau_d / (tau_d - tau_r) * log(tau_d / tau_r).
```

This gives approximately

```text
rat:    t_peak =  1.46 ms    t_peak / tau_m = 0.073
human:  t_peak = 12.17 ms    t_peak / tau_m = 0.609
```

So the human conductance envelope rises on a time scale that sits well inside the dominant passive membrane/cable window, whereas the rat envelope reaches its peak much faster than the 20 ms membrane time.

Call this **temporal overlap**, not resonance.

The correct test is against the actual cable modes / local impulse responses, not against one scalar `tau_m`.

---

## 3. A second hidden effect: peak-normalized kinetics changes conductance area

Because the double exponential is normalized to the same *peak*, changing the rise time also changes the integral of the kernel.

For the released parameters, a unit-peak kernel has approximately

```text
integral rat   ~= 44.48 ms
integral human ~= 57.07 ms
```

so the human-shaped NMDA kernel carries about

```text
57.07 / 44.48 ~= 1.28 x
```

more conductance-time area even **before** changing the nominal peak conductance.

The released human nominal NMDA peak scale is also about

```text
0.00131 / 0.00030 ~= 4.37 x
```

larger than the rat value.

Multiplying those two purely waveform/peak factors gives roughly

```text
4.37 * 1.28 ~= 5.6 x
```

more nominal NMDA conductance-time area in the full human parameter set before the voltage-dependent Mg block and driving force are applied.

This is not synaptic charge, because current also depends on voltage and the Mg gate. It is a useful audit of the conductance waveform itself.

---

## 4. Therefore “kinetics-only” needs two controls

A naive intervention

```text
same g_peak
rat tau_r -> human tau_r
```

changes both temporal shape **and total conductance area**.

That is a legitimate biological intervention, but it does not isolate temporal placement from total drive.

Use two versions:

```text
K_peak:
    match peak conductance
    change only tau_r/tau_d

K_area:
    rescale conductance so integral(g dt) is matched
    change only the temporal distribution of the conductance
```

Then compare both with the rat baseline.

If `K_peak` changes the nonlinear knee but `K_area` does not, much of the effect is simply extra integrated conductance.

If `K_area` still changes the knee / trajectory / FCI proxy, the timing of the waveform relative to the cable matters independently of total conductance area.

---

## 5. The better dynamic object is a loop-gain trajectory

For a frozen operating state at time `t`, compute

```text
K_t = diag(k_i(t))
```

where for each active site

```text
k_i(t) = d I_N,i / d v_i
```

using the current synaptic conductance and local voltage.

Then track a reduced susceptibility such as

```text
rho_t = spectral_radius( Z(0) K_t )
```

or, better, use the full frequency-dependent cable impedance

```text
sigma_max( Z(omega) K_t )
```

across a small preregistered frequency range.

This produces a trajectory

```text
input event
   -> g_N(t)
   -> K_t
   -> loop susceptibility through the morphology
   -> local voltage trajectory
```

The experimental question is whether the human-shaped envelope keeps the system in a high-susceptibility region longer or places that region at a different phase of the passive cable response.

Do not call `rho_t = 1` an NMDA-spike theorem; `ZK_THRESHOLD_GUARDRAIL.md` still applies.

---

## 6. A cleaner branch-level factorial

On one fixed morphology / one fixed branch / identical event locations:

```text
T0  rat kinetics, rat peak, rat gamma

T1  human kinetics, rat peak, rat gamma              [peak matched]
T2  human kinetics, charge-area matched, rat gamma   [area matched]
T3  rat kinetics, human peak, rat gamma
T4  rat kinetics, rat peak, human gamma
T5  full human NMDA
```

Record

```text
local voltage
somatic voltage
NMDA conductance and current
integral of NMDA current
supralinearity ratio
knee location
loop-gain trajectory rho_t
```

Run both synchronous and temporally jittered input.

This is much cheaper than a new FCI panel and tells us what the 17x rise-time change actually does.

---

## 7. Why this is more interesting than “different materials oscillate differently”

The surviving physical statement is simpler:

> **different pieces of the neuron retain and transform recent input on different time scales, and geometry determines how those temporal kernels interact.**

In the linear limit, a synaptic kernel and a cable kernel compose by convolution.

With NMDA, the same temporal envelope also moves a voltage-dependent feedback gain through the operating states of the cable.

So the question is not whether the dendrite has one resonant frequency.

It is whether the **temporal kernel carried by a local synapse is well or poorly aligned with the spectrum of transfer times made available by the morphology.**

That is measurable.

---

## Source-code anchors

- `ido4848/FCI/simulating_neurons/neuron_models/model_utils.py` — rat/human AMPA/NMDA kinetics, peak conductances and gamma.
- `ido4848/FCI/.../AMPANMDA_EMS.mod` — dual-exponential conductance states + instantaneous voltage-dependent Mg block.
- `ido4848/FCI/simulating_neurons/neuron_models/passive_dends_simple_soma_model.hoc` — passive `cm`, `g_pas`, `Ra`.

## Current sentence

> **The 17x rise-time difference is not a separate “oscillator.” It changes the time course of the conductance envelope that sweeps a voltage-dependent feedback gain across the dendritic cable's own relaxation modes. Match peak and match conductance area separately before attributing any effect to timing itself.**
