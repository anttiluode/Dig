# Correction: the published FCI probe is segment-addressed, not dendro-plexed

**Status:** code-level correction to `DENDROPLEXING_TWINPROP_GAP.md`.  
**Date:** 2026-08-15.

This correction matters. The dendro-plexing paper is highly relevant to **TwinProp/task capacity**, but I was too quick to suggest that the same multi-contact mechanism might directly explain the published Aizenbud FCI.

Inspection of the released FCI code shows a different input-addressing scheme.

## 1. What the FCI simulator actually creates

In `ido4848/FCI`, `create_synapses()` walks through every dendritic segment and creates:

```text
one excitatory AMPA/NMDA point process per segment
one inhibitory GABA point process per segment
```

The simulation code then defines a number of hidden/initial presynaptic spike trains associated with each segment. By default the count is approximately the segment length in microns:

```python
count_initial_synapses_per_super_synapse = ceil(seg_len)
```

Those independent spike trains are linearly mixed with a random kernel into **one weighted spike channel for that segment**.

Schematic:

```text
many independent initial sources
        |
        | random scalar weights
        v
[segment i super-synapse] ---> one weighted spike train for segment i
```

The TCN sees the resulting segment-level weighted spike channels.

Critically, the code partitions the initial presynaptic sources into disjoint slices for successive segments. An initial source assigned to one segment is not reused at other dendritic locations.

Therefore the published FCI data generator does **not** instantiate the defining dendro-plexing situation:

```text
one identifiable presynaptic axon
    -> multiple contacts
    -> several dendritic locations
    -> one spike expressed through several cable filters
```

That is a different experiment.

## 2. Why this actually sharpens the FCI/TwinProp distinction

The input representations are different:

```text
FCI
    segment-addressed channels
    source identity is effectively local to one segment

TwinProp / dendro-plexing
    axon-addressed inputs
    one axon's spike can be expressed at multiple dendritic locations
```

Thus FCI and TwinProp do not only measure different outputs (`emulation difficulty` versus `optimized task capacity`). They expose the cell to different **addressing algebras**.

This makes a naive FCI-versus-TwinProp correlation even harder to interpret.

A cell could have:

```text
moderate FCI under segment-local random drive
but
large capacity gain when axon identity can be multiplexed over multiple locations.
```

That would not be contradictory.

## 3. What passive Green kernels can still contribute to FCI

The correction does **not** remove passive cable filtering from FCI.

Each segment-level input channel still passes through a location-specific transfer kernel before reaching the soma. A fixed TCN must therefore represent a large collection of mappings such as

```text
x_i(t) -> h_soma<-i(t) -> somatic state
```

and, with NMDA, local channels interact nonlinearly through the dendritic voltage field.

But the passive candidate for FCI is now:

> **diversity and organization of segment-addressed transfer functions**

not:

> **dendro-plexing of one axon through several filters.**

This also reinforces the earlier warning: because the TCN's first convolution has separate weights for each input channel, a bank of passive per-segment filters may be relatively cheap for it to emulate. The stronger FCI mechanism may still be local nonlinear interaction among channels.

## 4. A new controlled experiment: change the addressing algebra while keeping the cell fixed

This gives a useful experiment that neither paper performs.

On the exact same morphology and biophysics construct two input protocols with matched total contact count, rates and conductance budget.

### Protocol S — segment-local, FCI-like

```text
each input identity -> one dendritic segment
```

### Protocol D — dendro-plexed / axon-preserving

```text
each input identity -> m contacts at multiple dendritic locations
all contacts share the same presynaptic spike train
```

Then measure both:

```text
surrogate emulation difficulty
and
optimized task capacity
```

The difference isolates something quite precise:

> the computational consequence of allowing **one temporal variable to occupy several spatial addresses**.

That is a much better connection to the old “time as geometry” intuition than treating all dendritic filtering as dendro-plexing.

## 5. Four-way address/control matrix

The cleanest version crosses two factors:

```text
A = source identity
    independent-per-contact / shared-per-axon

L = contact location structure
    single-location / multi-location
```

giving:

```text
independent + single      FCI-like local channels
independent + multiple    more contacts, but no temporal identity multiplexing
shared + single           repeated-strength control
shared + multiple         true dendro-plexing
```

Keep the number of physical contacts fixed across conditions.

This separates the benefit of merely having more dendritic contacts from the specific benefit of **sharing one spike history across spatially different cable filters**.

## 6. Consequence for the Dig ladder

Use two ladders rather than collapsing them:

```text
FCI mechanism ladder
    segment transfer kernels
    -> electrical/local interaction structure
    -> NMDA / active nonlinearities
    -> fixed-probe emulation difficulty

capacity ladder
    axon identity
    -> multiple spatial contacts / dendro-plexing
    -> local nonlinear subunits
    -> optimized task performance
```

The interesting experiment is the bridge between the ladders, not the assumption that they are identical.

## 7. Source-code anchors

Released FCI implementation inspected at commit:

```text
55826436751c03a32dfd39e91a48894869e1db57
```

Relevant files:

```text
simulating_neurons/neuron_models/model_utils.py
    create_synapses()

simulating_neurons/simulate_neuron.py
    generate_spike_times_and_weights_for_kernel_based_weights()
```

The first creates one excitatory and one inhibitory synaptic point process for every dendritic segment. The second allocates disjoint groups of initial presynaptic spike trains to each segment and collapses them to a segment-level weighted spike channel.

## Current correction sentence

> **Dendro-plexing is a strong mechanism for task capacity, but it is not the input architecture used to define published FCI. FCI preserves dendritic location but largely discards cross-location axon identity. That difference is itself experimentally useful: it lets us ask what is gained when one temporal source is allowed to inhabit several spatial addresses.**
