# Guardrail: `lambda(ZK) -> 1` is a susceptibility warning, not yet “the NMDA spike count”

**Status:** mathematical correction / validation plan.  
**Date:** 2026-08-15.

## 0. The tempting jump

From the local Green/NMDA linearization

```text
delta v = Z [delta i + K delta v]
```

we obtain, under the chosen inward-current sign convention,

```text
Z_eff = (I - Z K)^(-1) Z.
```

It is tempting to say:

```text
lambda_max(ZK) -> 1
    == NMDA-spike threshold
```

and then go one step further:

```text
number of localized eigenvalues that can reach 1
    == number of independent NMDA subunits.
```

That is too strong.

The first statement can become approximately true in a carefully defined quasi-static reduction. The second is presently an unvalidated hypothesis.

---

## 1. What singularity of `I - ZK` actually means

Suppose we have a static fixed-point relation

```text
v = Z [i_ext + I_N(v)]
```

and define

```text
F(v) = v - Z[i_ext + I_N(v)].
```

Then

```text
dF/dv = I - ZK.
```

If `I - ZK` becomes singular, the local implicit mapping between drive and equilibrium voltage loses invertibility.

That is precisely the kind of condition that can occur at a fold / saddle-node of an equilibrium branch.

So in a **static or adiabatic approximation**, an eigenvalue of `ZK` approaching 1 is a legitimate warning that local regenerative gain is becoming very large.

It is useful.

It is not the full NMDA dynamics.

---

## 2. The actual FCI NMDA synapse has state and time

The released `AMPANMDA_EMS` mechanism contains dual-exponential NMDA conductance state variables with finite rise and decay kinetics, plus voltage-dependent magnesium block.

The membrane itself is capacitive.

Therefore the dynamical state is more like

```text
x = [v, synaptic gating variables, ...]
```

with

```text
dx/dt = F(x,u).
```

Local dynamical stability is controlled by the eigenvalues of the **full state Jacobian**

```text
A_x = dF/dx | x*
```

not by `Z(0)K` alone.

A dynamical transition is associated with the relevant eigenvalue(s) of that full Jacobian crossing the stability boundary. Depending on the system, the transition need not look exactly like a static fold.

`ZK` can still be an excellent reduced diagnostic when synaptic conductance is treated as slowly varying or frozen over the voltage relaxation being considered.

But that approximation must be stated.

---

## 3. NMDA plateau onset is nonlinear and saturating

The local NMDA current has several ingredients that break a one-number threshold picture:

```text
Mg block relief increases inward current with depolarization
reversal-potential driving force decreases with depolarization
conductance rises and decays in time
neighboring sites share voltage through the cable
other membrane currents may participate
```

Thus a large linearized loop gain is a **susceptibility**, not automatically an all-or-none spike.

The safe interpretation is:

> `lambda_max(ZK)` measures how close a chosen operating state is to strong regenerative amplification in the quasi-static local-feedback reduction.

---

## 4. Eyal's “independent simultaneous NMDA spikes” is a different object

Eyal et al. 2018 estimated how many dendritic regions in a detailed cell could generate NMDA spikes simultaneously while remaining sufficiently electrically independent.

Reported model estimates were approximately

```text
human L2/3: 24.8 +/- 4.4
rat L2/3:   13.7 +/- 2.1
```

That is a combinatorial/functional subunit count produced by explicit nonlinear simulations and electrical-decoupling structure.

There is no established theorem that says it equals the number of eigenvalues of `ZK` that can reach one.

Why the proposed correspondence may fail:

```text
one eigenmode can span several branches
several localized nonlinear regions can interact through one mode
K changes as voltage and conductance change
eigenvectors can delocalize as the operating point changes
simultaneous activation changes the operator itself
```

So do not call the eigen-count a “threshold-free replacement” for Eyal's procedure or for an `I_Z` cutoff until it reproduces explicit nonlinear simulations.

---

## 5. The right validation experiment

The idea is still worth testing because it makes a sharp prediction.

For one branch/site:

1. freeze a synaptic conductance level or drive parameter;
2. continue the equilibrium / slowly varying voltage branch as drive increases;
3. compute the passive or linearized impedance matrix `Z` at the same state;
4. compute the local incremental NMDA gain matrix `K`;
5. track `lambda_max(ZK)` and its eigenvector localization;
6. independently detect the explicit simulated NMDA knee / plateau.

Ask:

```text
Does lambda_max(ZK) approach 1 near the actual transition?
Does its eigenvector localize where the plateau starts?
```

If not, the reduced diagnostic is not useful enough.

---

## 6. Then test multiple independent subunits

Only after the one-site threshold test works:

- choose candidate dendritic regions;
- measure explicit pairwise/multi-site simultaneous NMDA-spike independence;
- compute the near-critical modes of the corresponding state-dependent feedback operator;
- compare mode localization and effective count with the explicit subunit count.

Useful quantities can include eigenvector participation ratio or inverse participation ratio, but predeclare them before looking at the final cell-type comparison.

The desired result is not “24.8 eigenvalues.”

The desired result is a robust mapping from a cheap linearized susceptibility calculation to the expensive explicit nonlinear independence test.

---

## 7. A better name for now

Call

```text
L(x) = Z(x) K(x)
```

the **local feedback susceptibility operator** in Dig notes.

Call

```text
rho(L)
```

the spectral radius of that reduced feedback loop.

Do not call it an NMDA-spike count, computational dimension, or new geometry.

If it survives explicit simulation, stronger language can come later.

## Primary anchors

- Eyal et al. 2018, *Frontiers in Cellular Neuroscience*, DOI `10.3389/fncel.2018.00181` — explicit independent simultaneous NMDA subunits in human vs rat L2/3 models.
- Aizenbud et al. 2026, *PNAS*, DOI `10.1073/pnas.2533168123` — FCI and NMDA nonlinearities.
- FCI `AMPANMDA_EMS.mod` — finite AMPA/NMDA kinetic states plus voltage-dependent Mg block.
- Wybo et al. Green/impedance work — established cable transfer machinery.

## Current sentence

> **`I-ZK` becoming ill-conditioned is a principled quasi-static warning for regenerative dendritic feedback. It is not yet an NMDA-spike theorem, and its eigenvalue count is not yet Eyal's nonlinear-subunit count. Validate one threshold first; only then test whether localized near-critical modes predict independent subunits.**
