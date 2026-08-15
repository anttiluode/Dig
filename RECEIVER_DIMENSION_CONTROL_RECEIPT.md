# Receiver projection / dimensionality control — receipt

**Date:** 2026-08-15  
**Status:** executed preregistered control. **The strong soma-specific receiver-collapse interpretation is not supported.**  
**Gate:** `RECEIVER_DIMENSION_CONTROL_GATE.md`  
**Executable:** `receiver_dimension_control_cell1.py`

## Provenance

Pinned public FCI commit:

```text
ido4848/FCI
55826436751c03a32dfd39e91a48894869e1db57
```

Model/protocol are the same as Q0:

```text
Rat_L5b_PC_2_Hay_passive_dends_simple_soma / cell1.asc
16 fixed source sites
6 fixed receiver sites
0.02 nA / 0.5 ms IClamp
matched no-stimulus subtraction
same normalization and source-signature metrics
```

GitHub Actions run:

```text
31888419683
```

Dig commit tested:

```text
a70524c336d00e813e90abcd41b0ddd3fdebac22
```

All code and invariance guards completed successfully.

---

# Why this control was needed

Q0 compared:

```text
one soma time series
vs
six receiver time series
```

and found entropy effective rank:

```text
soma only            3.83836
six-port             8.51589
```

The receiver jackknife showed that no single dendritic port carried the six-port result, but it did not exclude a simpler explanation:

> more retained measurement dimensions preserve more distinctions.

This receipt tests that explanation directly.

---

# C1 — equal one-channel physical receivers

Entropy effective rank for each physical receiver alone:

```text
soma[0]              3.83836

dend[54]             3.27279
dend[67]             3.86996
apic[14]             3.18107
apic[37]             2.41673
apic[71]             2.78868
```

Summary over the five dendritic ports:

```text
minimum               2.41673
median                3.18107
maximum               3.86996
fraction > soma       0.20
```

So the soma is **not** an unusually collapsing one-dimensional receiver among these physical ports. Four of the five dendritic single-port views have lower entropy rank than the soma.

---

# C2 — fixed random one-dimensional mixtures

Using exactly 512 Gaussian receiver-weight vectors with preregistered seed `20260815`, each normalized to unit L2 norm:

```text
random 1-D entropy rank

minimum               2.85032
5th percentile        3.27086
25th percentile       3.65260
median                4.01179
mean                  4.06240
75th percentile       4.41955
95th percentile       4.99533
maximum               5.48675
```

The physical soma's entropy rank:

```text
3.83836
```

lies at only the

```text
36.91st percentile
```

of the fixed random one-dimensional projection ensemble.

Other soma percentiles:

```text
median pairwise cosine-distance percentile       23.24
median nearest-neighbour cosine-distance pct     14.65
```

Therefore the soma is neither a pathological low-information projection nor an unusually rich one. It is an ordinary-ish one-dimensional view of the six measured receiver signals under this protocol.

---

# C3 — dimension curve

For each retained output dimension `k`, 256 fixed-seed random orthonormal receiver projections were compared with **all** physical subsets of `k` of the six ports.

## Entropy effective rank

```text
k   random projection median   physical subset median   physical min..max

1           4.00054                  3.22693          2.41673 .. 3.86996
2           6.05070                  5.01339          4.16087 .. 5.52959
3           7.19592                  6.17729          5.12160 .. 6.67458
4           7.75687                  7.13673          6.28925 .. 7.44936
5           8.17810                  7.84684          7.41152 .. 8.12907
6           8.51589                  8.51589          8.51589 .. 8.51589
```

At every reduced dimension `k=1..5`, the median random linear receiver subspace preserves more normalized source-signature rank than the median physical coordinate subset.

Even the **best** physical subset remains below the random median at `k=1..5` in this run.

Examples:

```text
k=2
random median         6.05070
best physical pair    5.52959   receivers [0,3]

k=3
random median         7.19592
best physical triple  6.67458   receivers [0,2,3]
```

This is not surprising enough to be a biological discovery: a mixed low-dimensional projection can retain distributed information that coordinate selection discards. Random projection / observability / sensor-compression mathematics already gives a broad context for such behavior.

## Required k=6 invariance check

A six-dimensional orthonormal remix of all six physical receiver channels should preserve cosine geometry exactly.

Observed maximum entropy-rank absolute error over the fixed random ensemble:

```text
1.60e-14
```

Preregistered guard:

```text
< 1e-8       PASS
```

So the projection implementation is behaving consistently.

---

# Verdict

The preregistered branches were:

```text
C-A  soma is a special collapsing projection
C-B  soma is an ordinary one-channel observer
C-C  additional receiver complementarity beyond dimension
```

The strongest result is **C-B**.

> **The Q0 soma-versus-six-port rank jump is mostly a dimensionality / distributed-observation result, not evidence that the soma is uniquely destructive of source geometry.**

The better sentence is:

```text
distributed multiport observation preserves more of the source-transfer dictionary than scalar observation.
```

That is much weaker and much less exotic than:

```text
the soma specially collapses dendritic geometry.
```

Do not use Q0 as evidence for the latter.

---

# What remains mildly interesting

The random-projection control reveals a separate engineering fact:

```text
six distributed receiver signals
 -> low-dimensional linear mixtures
 -> retain more source-signature diversity than selecting the same number of local channels
```

For example, two random mixed outputs preserve median entropy rank ~6.05, versus at most ~5.53 for any physical two-port subset in this fixed set.

But this should **not** be promoted as novelty. It sits naturally beside random projection, sensor fusion, observability and compressed measurement ideas.

If pursued, the useful question is not:

```text
why is the soma bad?
```

It is:

> **What readout maps preserve the task-relevant distinctions already distributed through a physical or computational medium, under a fixed output-bandwidth/state budget?**

That question transfers cleanly to dendrites, wave systems and artificial networks, but it requires a serious prior-art collision before becoming a project claim.

---

# Updated kill status of the old sentence

Earlier working sentence:

> Different morphologies support different modes. Different local states deform those modes. Different receivers see different subsets of them. Computation may consist partly in controlling that deformation.

After Q0, Q1, Q2 and this control:

```text
Different morphologies support different modes/transfer structure.
    established generally; not our discovery.

Different local states deform those modes.
    biophysically true in general, but the measured small-signal source
    geometry was nearly isometric under both mechanism ablation and -85/-65 mV.

Different receivers see different subsets.
    true only in the ordinary sense that different / more measurement
    projections preserve different information; soma was not special at equal dimension.

Computation may consist partly in controlling that deformation.
    not earned here.
```

The romantic version has therefore been substantially killed by its own controls.

That is a good outcome.

## One-line handoff

> **Receiver identity did not rescue the geometry story: soma is ordinary among equal-dimensional projections. The surviving technical object is distributed source information plus a readout/compression map; any next step should collide that exact readout-design problem with observability, random projections, sensor fusion and neural readout literature before building.**
