# Receiver projection / dimensionality control

**Status:** preregistered before execution. **Not a novelty claim.**  
**Date:** 2026-08-15.

## Why this control is necessary

Q0 established that the exact FCI/Hay `cell1.asc` source dictionary has much higher normalized effective rank when observed through

```text
soma + 5 dendritic receivers
```

than through

```text
soma alone.
```

The receiver jackknife showed that no single lucky dendritic port carries the six-port effect.

But a simpler objection remains:

> six time series have more measurement dimensions than one time series.

Therefore Q0 does **not yet** justify the stronger statement that the soma is a particularly collapsing observer, or that receiver identity matters strongly at equal readout dimension.

This gate asks that question directly.

---

# Frozen biological protocol

Use the exact Q0 model family and protocol.

Pin FCI to current public commit:

```text
ido4848/FCI
55826436751c03a32dfd39e91a48894869e1db57
```

Model:

```text
simulating_neurons/neuron_models/rat/hay/
Rat_L5b_PC_2_Hay_passive_dends_simple_soma
```

Morphology:

```text
cell1.asc
```

Reuse Q0 exactly:

```text
8 basal + 8 apical source sites by path-distance spread
soma + 2 basal + 3 apical fixed receiver sites
IClamp amplitude      0.02 nA
pulse duration        0.5 ms
delay                 20 ms
tstop                 140 ms
dt                    0.05 ms
v_init                -70 mV
matched no-stimulus subtraction
```

No source/receiver position or electrical parameter may change.

---

# Equal-dimensional controls

Let the matched-subtracted response tensor be

```text
A[source, receiver, time]
```

with 16 sources and 6 receivers.

## C1 — each receiver alone

For every physical receiver `r`, form

```text
X_r[source,time] = A[source,r,time].
```

L2-normalize each source signature exactly as Q0 did and report:

```text
entropy effective rank
participation rank
median pairwise cosine distance
median nearest-neighbour cosine distance
```

This is the cleanest equal-dimensional comparison:

```text
soma-only vs dendritic-receiver-only.
```

## C2 — random one-dimensional projections

Use fixed RNG seed:

```text
20260815
```

Generate exactly:

```text
512
```

random Gaussian vectors `w in R^6`, normalize each to unit L2 norm, and form one time series per source:

```text
X_w[source,time] = sum_r w[r] A[source,r,time].
```

Each projected source signature is then L2-normalized before the same metrics are computed.

Report the distribution of entropy effective rank and pairwise-distance metrics, plus the percentile of the physical soma projection within that fixed random ensemble.

No random search result is used to alter the receiver set.

## C3 — dimension curve

For each retained receiver dimension

```text
k = 1,2,3,4,5,6
```

generate `256` fixed-seed random orthonormal projections from the six physical receiver channels into `k` channels.

For each projection:

```text
project receiver axis
flatten projected receiver x time features
L2-normalize source rows
compute effective rank / source-distance metrics
```

At `k=6`, an orthonormal receiver mixing must preserve the full six-port cosine geometry to numerical precision. Treat failure of this invariance as a harness bug.

Also exhaustively evaluate all physical receiver subsets of size `k` (there are only 6 receivers), without optimizing after seeing results.

---

# Predictions / kill logic

## C-A — soma is a special collapsing projection

This stronger receiver interpretation earns support only if, at the same one-channel output dimension:

```text
soma effective rank is materially lower than most individual dendritic receivers
and/or
soma lies in the low tail of the fixed random 1-D projection ensemble.
```

The continuous percentile must be reported; no post-hoc cutoff is invented.

## C-B — soma is an ordinary one-channel observer

If soma rank lies near the center of individual/random one-dimensional views, then much of Q0's 2.2x rank gain is simply the expected consequence of keeping more receiver dimensions.

In that case demote the language from

```text
receiver identity exposes radically different geometry
```

to

```text
distributed multiport observation preserves more of the transfer dictionary than scalar pooling.
```

That is still true, but much less surprising.

## C-C — receiver complementarity

If individual one-port views differ substantially, and particular physical subsets preserve more source geometry than typical random/subset controls of the same dimension, then receiver placement / complementarity is an additional real effect beyond raw dimensionality.

Do not call this optimal sensor placement; sensor selection and observability are established fields.

---

# Why this matters to the current pivot

Q1 and Q2 weakened the idea that current state dramatically bends the small-signal source-neighbour geometry.

Q0 appeared to leave receiver projection as the strong lever.

But before promoting that lever into a PivotPoint / routing / AI story, we need to know whether it is truly **receiver-relative** or merely **dimension-relative**.

This control is therefore a stop-gate on the conceptual pivot.

## One-line preregistration

> **Re-run exact Q0 once, hold the biology fixed, and compare soma to equal-dimensional physical and random receiver projections before claiming receiver identity is the surviving lever.**
