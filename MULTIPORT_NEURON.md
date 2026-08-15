# The neuron as a multiport dynamical system

**Status:** synthesis / engineering language. Not a novelty claim.  
**Date:** 2026-08-15.

## 0. The point-neuron correction that survives

The McCulloch-Pitts-style abstraction is enormously useful when the question is:

```text
many inputs -> one thresholded output
```

Aizenbud FCI deliberately opens the box and asks how hard the detailed internal map is to emulate, but its headline complexity score is still evaluated through prediction of the cell's spike output.

TwinProp similarly optimizes a detailed pyramidal neuron toward task decisions that are eventually read from a somatic/axonal spike criterion.

For cortical pyramidal cells this is a legitimate interface.

The retina shows why it is not a universal definition of a neuron.

---

## 1. The minimally general abstraction is multiport

Let

```text
S = source / input locations
R = receiver / output locations
x = distributed internal state
u_S(t) = external inputs
```

and write

```text
dx/dt = F(x, u_S)
y_R    = G_R(x, u_S).
```

Around an operating state, the linearized input-to-output object is not one scalar impulse response but a matrix-valued family

```text
H_R<-S(t).
```

Each entry asks

```text
what does source s do at receiver r after time t?
```

This is ordinary multi-input/multi-output systems language.

The biological content comes from what counts as a port and what state lives between the ports.

---

## 2. The pieces now fit without calling all of them “geometry”

```text
cable / morphology
    distributed electrical state
    transfer between spatial ports

synapse
    local stateful boundary/transducer
    receptor kinetics, Mg block, vesicle state, plasticity

active membrane
    local voltage-dependent dynamics

extracellular domain
    optional additional spatial coupling between membrane ports

soma / axon
    one important receiver / nonlinear output mechanism

local dendritic release site
    another possible receiver / output port
```

The shape constrains the coupling.
The state determines the current operating operator.
The ports determine what computation is visible to the observer.

---

## 3. Why the synapse is a “choke point” only in one sense

A synapse is spatially local compared with the full neuron, so it is a point at which a distributed presynaptic state is transformed into a localized postsynaptic current or, in the opposite direction, a local presynaptic voltage/Ca state is transformed into transmitter release.

But it is not a memoryless bottleneck.

A useful schematic is

```text
pre-synaptic history
      -> local release state
      -> cleft / receptor state
      -> postsynaptic current history
```

or for a ribbon synapse

```text
graded terminal voltage
      -> Ca entry
      -> vesicle-pool state
      -> stochastic release amplitudes/times
```

The state at the synapse can retain information about recent input and alter the next transmission event.

So the stronger surviving statement is:

> **a synapse is a local transducer with its own state and temporal kernel, embedded in a larger spatial transfer system.**

---

## 4. “Blur” becomes impulse response, not vagueness

In a linear approximation, each physical stage that has memory contributes an impulse response.

For example, a voltage-independent synaptic current at source `i` followed by passive dendritic transfer to receiver `r` gives schematically

```text
y_r(t) = h_cable[r <- i](t) * g_syn,i(t) * x_i(t)
```

where `*` is convolution.

This is a precise version of saying that each stage “blurs” recent input.

But not every domain supplies temporal blur:

- a purely resistive extracellular volume conductor mainly supplies instantaneous **spatial mixing**;
- membrane capacitance supplies temporal memory;
- receptor and vesicle kinetics supply temporal memory;
- voltage-dependent nonlinearities make the effective kernel state-dependent.

So do not flatten every medium into “another low-pass filter.”

---

## 5. The distributed receiver changes the meaning of complexity

Suppose the complete output is

```text
Y_R(t) = [y_1(t), ..., y_M(t)].
```

A soma-based experiment observes only

```text
y_soma(t) = P_soma Y_R(t)
```

for one projection `P_soma`.

If biologically relevant distinctions cancel or never reach that projection, a soma-based complexity measure can be low while local-output computation is rich.

Starburst amacrine cells give an empirical example: local dendritic Ca/output is direction-selective while somatic membrane voltage need not be.

This makes receiver choice part of the definition of the computational problem, not a cosmetic readout choice.

---

## 6. Aizenbud can now be located precisely inside the larger object

Aizenbud asks approximately:

```text
fixed distributed source protocol
      -> detailed morphology + synapse + membrane state
      -> soma/axon spike receiver
      -> how hard is this projection for a fixed TCN to emulate?
```

That is valuable.

It does not by itself measure:

```text
all local dendritic outputs
all possible receiver choices
optimized task capacity
the intrinsic state dimension of the cell
```

Those are different questions.

The Dig program should therefore stop trying to make FCI stand for all of “neuron complexity.”

Use it as one receiver-specific probe and compare it to other probes.

---

## 7. The clean empirical program

On the same physical model:

```text
A. freeze the source set
B. vary the receiver set
C. vary one mechanism at a time
```

Receiver sets:

```text
R1 = soma/spike
R2 = selected dendritic voltages
R3 = local nonlinear-event sites
R4 = local transmitter-release sites where the biology provides them
R5 = all of the above jointly
```

Mechanism gates:

```text
passive cable
+ local synaptic state
+ NMDA feedback
+ active dendrites
+ optional extracellular coupling
```

Then ask separately:

```text
what information reaches each receiver?
how difficult is each map to emulate?
how much task capacity is available after optimization?
```

No single scalar is assumed to answer all three.

---

## 8. The current synthesis sentence

> **A neuron is usefully viewed as a distributed, stateful multiport system. Morphology specifies much of the spatial coupling; synapses and membrane mechanisms supply local state and nonlinear transduction; time turns those constraints into receiver-specific transfer; and a point-neuron output is one projection of that larger object, not always the object itself.**
