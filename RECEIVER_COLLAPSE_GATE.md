# Receiver collapse on a fixed dendritic morphology

**Status:** preregistered measurement gate. **Not a novelty claim.**  
**Date:** 2026-08-15  
**First executable:** `receiver_collapse_cell1.py`

## Why this gate exists

Two V23 observations now need to be separated.

First, exact learned STP tuple -> exact dendritic address binding has failed to emerge in the passive and smooth-threshold synthetic gates. In the learned solutions, several contacts collapse onto the same site and the remaining within-afferent STP tuples are often nearly exchangeable.

Second, the broader receiver-relative idea is still biologically ordinary and real: dendrites are distributed systems, and a soma is only one possible projection of their state.

The danger is to rescue a failed exact-address hypothesis by simply renaming branch structure "geometry." This gate instead asks a measurement question that is meaningful even if STP-address binding is permanently dead:

> **How many source distinctions in one fixed reconstructed neuron are visible at the soma, and how many become visible when the observer is allowed a small distributed receiver set?**

No learning is involved.

---

## Prior-art boundary

Nothing here claims discovery of dendritic functional subunits, transfer impedance, electrical compartmentalization, or state-dependent impedance.

Relevant anchors:

- Wybo et al. 2021, *Data-driven reduction of dendritic morphologies with preserved dendro-somatic responses*, eLife 10:e60936. Their reduction fits resistance/impedance structure at chosen dendritic locations and shows that complex nonlinear events can often be retained with far fewer compartments.  
  https://doi.org/10.7554/eLife.60936

- Narayanan & Johnston / resonance-analysis lineage explicitly measures local and transfer impedance as a function of dendritic and somatic operating voltage, showing that communication between compartments is state dependent. A useful concrete example is:  
  Das & Narayanan 2018, *Resonance Analysis as a Tool for Characterizing Functional Division of Layer 5 Pyramidal Neurons*.  
  https://doi.org/10.3389/fncom.2018.00029

- Parallel / semi-independent dendritic functional architectures are established. One modern example is the CA1 study showing that dendritic Na-dependent integration is better described by multiple dynamic nonlinear subunits with clustered connectivity than by one global architecture.  
  https://doi.org/10.1016/j.neuron.2023.03.015

- TwinProp 2026 provides a particularly relevant current example: its reverse-engineered 2-bit XOR solution segregates computation into coarse apical and basal functional subunits and combines them through a dendritic calcium event.  
  https://doi.org/10.64898/2026.06.08.730984

Therefore the phrase **receiver quotient** below is only local bookkeeping for this project, not a claim to have invented a mathematical or biological concept.

---

## The object

For source location `i`, receiver set `R`, operating condition `x`, and finite horizon `T`, write the measured small-signal response signature as

```text
S_x(i | R,T) = vec( h_x[r <- i](t) )
               for r in R, 0 <= t <= T.
```

Two anatomical locations can be different in micrometres yet nearly identical under this observation map.

Conversely, adding receivers can split locations that were indistinguishable at the soma.

Informally, the observer sees morphology only through the quotient induced by the source-to-receiver map:

```text
anatomical source space
        |
        v
receiver-visible response signatures
        |
        v
operationally distinguishable source classes
```

The first gate avoids choosing a class threshold. It compares the continuous signature geometry directly.

---

# Q0 — fixed passive-ish Hay cell1, soma versus multi-receiver

Use the exact author-released FCI Hay `cell1.asc` wrapper already documented in `EXACT_L5_BRIDGE.md`.

Keep fixed:

```text
same morphology
same membrane model
same initial voltage
same tiny current pulse
same source set
same simulation horizon
```

Select 8 basal and 8 apical source sites spread by soma path-distance order.

Receiver sets:

```text
R_soma:
    soma only

R_multi:
    soma
    + 2 basal receiver sites
    + 3 apical receiver sites
```

The additional receivers are selected independently from the source list by predeclared path-order quantiles. They are not optimized after seeing responses.

For each source, concatenate the post-stimulus voltage traces over the chosen receiver set and normalize each source signature to unit L2 norm for the principal shape analysis.

Report, without fitting thresholds:

```text
entropy effective rank
participation rank
singular spectrum
pairwise cosine-distance distribution
nearest-neighbour cosine distances
```

Also retain raw somatic peak amplitude as a sanity check.

---

## Predictions / kill logic frozen before run

### Q0-A — receiver-collapse signal

If

```text
rank(R_multi) > rank(R_soma)
```

and pairwise / nearest-neighbour source distances systematically increase under `R_multi`, then the soma is demonstrably collapsing source distinctions available elsewhere in the same physical neuron.

This is a receiver statement, not intrinsic-complexity proof.

### Q0-B — null

If the normalized source-signature geometry is essentially the same for soma-only and the fixed multi-receiver set, then this particular receiver-collapse framing is weak for this model/protocol.

Do not add more receivers until it wins.

### Q0-C — trivial-amplitude warning

If the apparent difference is only raw amplitude while normalized temporal/relative-receiver signatures remain low-rank, call it attenuation, not new geometry.

### Q0-D — source/receiver identity leakage warning

The multi-receiver set is deliberately not the entire source set. If every source were recorded locally at itself, perfect source identification would be nearly trivial and scientifically uninteresting.

---

# Q1 — state deformation only after Q0

Only if Q0 establishes a useful receiver-dependent signature geometry, keep the exact same anatomy/source/receiver sets and alter the operating equations:

```text
P0 passive cable baseline
P1 common rat AMPA/NMDA regime
P2 selected active conductance regime / holding state
P3 full Hay active dendritic regime
```

Then ask whether the pairwise source-signature geometry itself changes:

```text
d_x0(i,j | R,T) != d_x1(i,j | R,T).
```

This is the disciplined descendant of the old sentence

```text
state deforms the geometry
```

because anatomy is fixed and only the realized transfer operator changes.

A useful state result would require more than gain scaling: normalized source geometry must split, merge, rotate, or reorder in a reproducible way.

---

## Relation to the V23 shuffle nulls

Do **not** reinterpret Q0/Q1 as rescuing exact STP-address binding.

The nulls say:

```text
in the tested synthetic tasks,
optimization did not need exact temporal-state tuple <-> exact site pairing.
```

This gate asks instead:

```text
what spatial distinctions are physically available to a receiver at all?
```

If later a biological temporal-state experiment is attempted, its shuffle controls should be informed by these measured receiver-visible distinctions rather than assuming every segment is an equally distinct computational address.

That is a refinement of the measurement coordinate, not permission to tune until a positive effect appears.
