# Synaptic age field: local hidden state on the edges

**Status:** released-code audit + literature-grounded synthesis + proposed experiment. Not a claim that synapses contain literal clocks.  
**Date:** 2026-08-15.

## 0. The correction that matters

A tempting sentence is:

> the FCI synapses are memoryless and deterministic.

Only half of that is right.

The standard released FCI synapse **does remove presynaptic short-term plasticity / probabilistic release state**, but it still contains temporal state in the AMPA/NMDA conductance variables.

The released `AMPANMDA_EMS.mod` retains the historical BBP header describing a probabilistic two-state synapse with depression/facilitation, but the executable mechanism contains only

```text
A_AMPA, B_AMPA, A_NMDA, B_NMDA
```

plus the instantaneous voltage-dependent NMDA magnesium gate.

Its `NET_RECEIVE` deterministically adds the same weight-scaled increment at each incoming event. There is no `Rstate`, `u`, `Use`, `Dep`, `Fac`, random draw, or recovery process in the standard `AMPANMDA_EMS` mechanism.

So the precise statement is:

> **FCI keeps postsynaptic conductance-trace memory but removes presynaptic resource/release memory.**

That distinction is central to the current Dig question.

---

## 1. What the original BBP mechanism had

The intact `ProbAMPANMDA_EMS` family contains an event-driven local state machine.

Its variables include, schematically,

```text
Rstate   recovered / unrecovered release state
u        running release probability / facilitation state
tsyn_fac time of previous presynaptic event
Dep      recovery time constant
Fac      facilitation time constant
Use      baseline utilization
```

On each incoming spike the mechanism:

```text
updates facilitation from elapsed time
updates recovery probability from elapsed time
asks whether release occurs
if release occurs, changes the local resource state
```

Thus two identical incoming spikes can produce different outputs because the local synapse is in a different hidden state.

The FCI standard mechanism deliberately removes this layer and keeps the receptor/conductance dynamics.

This is not an error. It is an experimental/modeling choice that makes another mechanism available for a clean follow-up.

---

## 2. “Local time” has an ordinary dynamical-systems translation

Do not say that time literally freezes at a synapse.

The measurable object is a local state variable whose value depends on elapsed time since previous events.

For the simplest depressing resource variable `R`, between events one may write

```text
dR/dt = (1 - R) / tau_rec.
```

Immediately after a release, `R` is reduced. During silence it relaxes toward the recovered state.

For a single known release from a known post-event value,

```text
R(t) = 1 - [1 - R(t0+)] exp(-(t-t0)/tau_rec).
```

In that restricted case, `R` is a monotone encoding of the age `t-t0`.

The next incoming spike **samples that age-dependent state** because its released amount/probability depends on `R` (and, with facilitation, on `u`).

This is very close to the intuitive sentence:

```text
local state evolves quietly
network event arrives
local state is read / transformed
its contribution rejoins the distributed dynamics
```

But it is not an absolute clock. With repeated inputs, the state generally becomes a compressed summary of a recent event history rather than a unique timestamp.

That is exactly why Maass & Markram called dynamic synapses **memory buffers** rather than clocks.

---

## 3. A graph with state on the edges

Point-neuron abstractions often place dynamical state on neurons and treat connections as fixed weights.

Short-term plasticity changes the ontology:

```text
node state       membrane / spiking state
edge state       synaptic resource / facilitation / receptor state
geometry         which edge connects which local source and receiver
```

For synapse `i`, write a local hidden state

```text
z_i(t) = [R_i(t), u_i(t), A_i(t), B_i(t), ...].
```

Across a dendritic arbor or network,

```text
Z_syn(t) = {z_i(t)}_i
```

is a distributed field of local histories living on the connections.

Incoming events do not merely carry values through fixed edges. They **query and update the edge state**.

This is ordinary hybrid/event-driven dynamics. The interesting biological question is how these local state machines are arranged in space and coupled by dendritic voltage.

---

## 4. The closest disciplined descendant of the Clockfield intuition

The useful remnant is not

```text
matter = frozen time
```

or

```text
synapse = a tiny physical clock.
```

It is:

> **recent events leave local physical state behind; different locations retain those traces for different durations; later events encounter that state and therefore have different causal effects.**

A network can therefore carry a broad present without every piece of information being represented by ongoing spikes.

This connects directly to established short-term-plasticity theories of transient/working memory, where synaptic state can retain information that is later refreshed or read out by spiking.

The scientific object is a field of decaying/recovering hidden states, not a metaphysical present.

---

## 5. Four kinds of “memory” now need to be kept separate

The current FCI discussion had been mixing several physically different traces.

```text
1. cable / membrane memory
   capacitive voltage relaxation and distributed cable modes

2. receptor-kernel memory
   AMPA/NMDA/GABA conductance states after an event

3. synaptic resource memory
   depression/facilitation/recovery/release state

4. structural memory
   morphology, locations, long-term weights/connectivity
```

The standard released FCI baseline contains 1, 2 and 4.

It largely omits 3 in the standard deterministic `AMPANMDA_EMS` / `GABAAB_EMS` path.

This gives a cleaner intervention than saying vaguely that “synaptic memory was removed.”

---

## 6. Why the missing state is computationally nontrivial

With a fixed receptor kernel, the effect of an incoming event is largely determined by

```text
event amplitude
local voltage
fixed synaptic parameters
```

With STP, the event also depends on

```text
recent event history at this particular connection.
```

The same physical input at the same location and same membrane voltage can therefore produce a different synaptic output because the edge itself remembers.

Primary work on dynamic synapses shows that this state can retain information about the recent presynaptic spike train. Other experiments show that depression + recovery can make postsynaptic amplitude encode an interspike interval.

So the local state is not merely biological decoration. It can be a temporal code.

---

## 7. The clean FCI follow-up is not simply “turn STP on”

Adding depression/facilitation changes mean synaptic efficacy, variance and output firing rate.

A useful intervention therefore needs matching controls.

Start on one exact morphology with a simple synapse family:

```text
S0  released deterministic synapse

S1  dynamic synapse / STP
    same receptor kinetics
    same morphology
    same source spike trains

S2  shuffled dynamic-state parameters
    same multiset of U / tau_rec / tau_fac
    permuted across spatial locations

S3  homogeneous dynamic-state parameters
    same mean release budget
```

For each condition, re-match the mean effective synaptic drive and the output-rate regime before comparing complexity.

The important comparisons are then:

```text
S1 - S0      value of adding local edge history
S1 - S2      value of pairing a particular history kernel with a particular geometry
S1 - S3      value of heterogeneity versus one common local clock
```

Do this first with AMPA-only or weak-voltage-dependence if the goal is to isolate STP from NMDA feedback.

---

## 8. Geometry x local time is now a literal factorial

Suppose each synaptic location carries recovery/facilitation parameters

```text
tau_i = [tau_rec,i, tau_fac,i, ...].
```

The morphology supplies source-to-receiver transfer kernels

```text
h[r <- i](t).
```

The dynamic synapse supplies a history-dependent local map

```text
z_i(t-) + event_i(t) -> released current_i(t+).
```

Then a genuine geometry/time question is:

> does the **assignment** of local temporal states to spatial/electrical addresses matter beyond the multiset of states and the morphology separately?

The shuffle control answers exactly that.

This generalizes the retinal “structured temporal kernels versus shuffled kernels” experiment from fixed filters to history-dependent edge states.

---

## 9. Wide-present connection, stated narrowly

A broad present need not mean a single globally smeared state.

It can mean that, at clock time `t`, many local variables still carry consequences of events from different past times:

```text
membrane voltage traces
receptor conductance traces
vesicle/resource recovery states
facilitation variables
calcium traces
```

Each has its own decay/recovery scale.

The instantaneous system state is therefore a **superposition of differently aged local traces**.

A new event meets those traces and its effect depends on them.

That is enough to obtain a physically wide present without positing a special time field.

---

## 10. Kill conditions

Do not promote this into a new general theory unless the interventions earn it.

Kill or sharply narrow the branch if:

```text
1. adding matched STP does not materially alter local transfer, emulation difficulty or task capacity;
2. structured versus shuffled STP parameters are indistinguishable;
3. any effect disappears after matching mean release / output firing rate;
4. ordinary receptor/cable memory already explains the result.
```

A positive result would still mean only that **dynamic edge state contributes to the tested computation**.

---

## Source anchors

- `ido4848/FCI/.../AMPANMDA_EMS.mod` — standard released mechanism: deterministic event increments + AMPA/NMDA conductance state, no `Rstate/u/Dep/Fac` machinery.
- `ido4848/FCI/.../GABAAB_EMS.mod` — analogous deterministic conductance-state mechanism in the standard path.
- Original BBP `ProbAMPANMDA_EMS` family — probabilistic recovered/unrecovered release state with utilization, depression and facilitation variables.
- Tsodyks, Pawelzik & Markram (1998), *Neural Computation*, DOI `10.1162/089976698300017502` — dynamic synapses / short-term plasticity model.
- Maass & Markram (2002), *Neural Networks*, DOI `10.1016/S0893-6080(01)00144-7` — synaptic internal state as a transient memory buffer for recent spike history.
- Mongillo, Barak & Tsodyks (2008), *Science*, DOI `10.1126/science.1150769` — working-memory model in which calcium-mediated synaptic facilitation stores a latent trace that can be refreshed/read by spiking.
- Oesch & Diamond (2011), *Nature Neuroscience*, DOI `10.1038/nn.2945` — ribbon-synapse vesicle depletion/recovery computes temporal contrast while sustained release encodes luminance.
- Watkins & Burrows (2018), *J Neurophysiology*, PMID `30206296` — matched depression/recovery at one synapse makes EPSP amplitude encode presynaptic interspike interval.

## Current sentence

> **The missing FCI mechanism is not “memory” in general; cable and receptor traces remain. What is absent is a local edge-state memory that changes what the next event means. In an STP synapse, elapsed recent history is stored physically in recovery/facilitation/resource variables and is sampled by the next transmission. A field of such states distributed over morphology is a concrete, testable descendant of the local-time intuition.**
