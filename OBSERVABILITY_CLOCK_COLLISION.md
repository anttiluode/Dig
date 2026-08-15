# Observability clock collision: what survives from the old vocabulary

**Date:** 2026-08-15  
**Status:** mathematics/prior-art boundary note. This is not a Clockfield validation and not a Connes claim.

## Starting object

For a linearized system

```text
x_dot = A x
      y = C x
```

and a finite set of source impulse directions collected as columns of `B_s`, define

```text
Y(t) = C exp(A t) B_s
```

and the source-space finite-horizon Gramian

```text
G_C,T = integral_0^T Y(t)^T Y(t) dt
      = B_s^T W_C,T B_s
```

where

```text
W_C,T = integral_0^T exp(A^T t) C^T C exp(A t) dt
```

is the ordinary time-limited observability Gramian.

For source alternatives `i,j`, with contrast vector `q_ij = e_i-e_j`,

```text
D_C,T^2(i,j)
    = q_ij^T G_C,T q_ij
    = integral_0^T ||h_i(t)-h_j(t)||^2 dt.
```

This is the object already measured in Dig.

Prior art: finite-time/frequency Gramians and their use in reduction go back at least to Gawronski & Juang (1990), *Model reduction in limited time and frequency intervals*, DOI 10.1080/00207729008910366.

---

# Exact 'one iota' identity

Differentiate with respect to horizon:

```text
dG_C,T / dT = Y(T)^T Y(T) >= 0.
```

Therefore every infinitesimal extension of the observation horizon adds a positive-semidefinite information slice.

If `C` has `m` output ports,

```text
rank(dG_C,T/dT) <= m.
```

This is exact.

It gives a careful version of the old intuition:

```text
WAIT
    keeps C fixed and integrates additional PSD slices.

ROUTE
    changes C and therefore changes the directions and strengths
    of the slices that can be added.
```

Do not turn this into `rank(W_T) grows by m every instant`. That is false for continuous LTI systems.

---

# Correction 1: exact rank does not open one power at a time

For an observable continuous LTI pair `(A,C)`, `W_C,T` is positive definite for every `T>0`.

So exact algebraic observability does not wait for a finite horizon before becoming full rank.

The relevant short-time phenomenon is **conditioning / effective rank under finite precision or noise**.

The small-time expansion is

```text
W_C,T
  = sum_{p,q >= 0}
      T^(p+q+1) / [p! q! (p+q+1)]
      (A^p)^T C^T C A^q.
```

The associated observability/Krylov stack

```text
O_k = [ C ; C A ; ... ; C A^(k-1) ]
```

has

```text
rank(O_k) <= m k.
```

That is where the `m*k` counting belongs.

More sharply, if a direction `v` first becomes visible at derivative order `r`, i.e.

```text
C A^0 v = ... = C A^(r-1) v = 0
C A^r v != 0,
```

then as `T -> 0`

```text
v^T W_C,T v
  ~ ||C A^r v||^2 T^(2r+1) / [(r!)^2 (2r+1)].
```

So later-visible directions are not exactly absent for positive `T`; their information can be buried under very high odd powers of a small horizon.

This is a better mathematical reading of `one iota`.

---

# Correction 2: Kellems 165330 -> 15 is real, but not `because m=1`

Kellems, Roos, Xiao & Cox (2009), *Low-dimensional, morphologically accurate models of subthreshold membrane potential*, explicitly use a somatic output

```text
C in R^(1 x N)
```

while preserving distributed inputs. For the finely discretized n408 cell they report

```text
N = 165330
IRKA reduced order ~15
~5 digits accuracy.
```

That is a striking one-output reduction.

But the order `15` is determined by how well the full distributed-input -> soma-output transfer function can be approximated. It is not a theorem that one output implies order 15 or order proportional to one.

Adding outputs may increase the required reduced order, but the scaling can be sublinear, linear, saturating, or morphology-dependent.

**Therefore the useful experiment is to measure the scaling, not assume `order ~ m`.**

Paper: DOI 10.1007/s10827-008-0134-2.

---

# Phase and magnitude are not analogies here

For a stable linear response, Parseval connects time-domain discrimination to the frequency-domain transfer responses.

For one output channel and Fourier responses `H_i(omega), H_j(omega)`, pointwise:

```text
|H_i - H_j|^2
  = (|H_i|-|H_j|)^2
    + 2 |H_i| |H_j| [1 - cos(delta_phi)].
```

Thus pairwise discrimination power admits an exact nonnegative decomposition into:

```text
MAGNITUDE term
    (|H_i|-|H_j|)^2

PHASE term
    2 |H_i||H_j| [1-cos(delta_phi)].
```

For multiple receiver ports, sum the same identity over channels.

On a finite recorded window this remains an exact identity for the discrete Fourier transform of that window (with the usual Parseval scaling), though windowing mixes physical frequencies.

This is worth measuring.

---

# Entropy: one valid use and two invalid shortcuts

## Valid under stated assumptions

If the unknown source-coordinate vector has Gaussian prior covariance `Sigma_s` and the measurement noise is Gaussian with covariance `R`, then the finite-horizon Fisher information is the noise-weighted Gramian

```text
J_T = integral H(t)^T R^-1 H(t) dt
```

and Gaussian mutual information has the standard log-determinant form

```text
I(source ; observations_0:T)
  = 1/2 log det(I + Sigma_s^(1/2) J_T Sigma_s^(1/2)).
```

With `Sigma_s=I` and `R=sigma^2 I`, this reduces to a log-det expression built from `G_C,T/sigma^2`.

## Invalid shortcut 1

Do not call `log det(I+G)` entropy without stating a prior/noise model.

## Invalid shortcut 2

Do not identify entropy of Gramian eigenvalues with thermodynamic or black-hole entropy.

A normalized spectral entropy can still be used as a descriptive statistic, but it is a different object.

---

# Null directions are ordinary unobservability, not an event horizon

If a source contrast `q` lies in

```text
ker(G_C,T)
```

then the two corresponding source combinations produce identical output on the measured interval.

For continuous LTI systems the exact unobservable subspace does not depend on choosing a longer positive interval: if a direction is truly unobservable, waiting alone never recovers it.

That is a clean mathematical null direction / pseudometric statement.

Calling it a black-hole surface adds no mathematics and risks confusing a linear-algebraic kernel with a causal spacetime horizon.

The useful shared phrase is only:

> geometry is being extracted from an operator/readout.

Connes' distance formula is a different construction: a supremum over an algebra constrained by a commutator norm. There is no current derivation identifying it with the observability Gramian.

---

# The pair-specific 'clock' that is actually measured

For any distinguishable pair with final horizon `T_f`, define the instantaneous discrimination energy

```text
g_ij(t) = ||h_i(t)-h_j(t)||^2
```

and the normalized discrete/continuous distribution

```text
p_ij(t) = g_ij(t) / integral_0^Tf g_ij(s) ds.
```

Then

```text
M_ij(T) = integral_0^T p_ij(t) dt
```

is exactly the within-readout discrimination maturity already measured by Dig.

This makes `M_ij(T)` a CDF-like object over *when* the eventual pairwise evidence arrives.

From it one can define without a fitted decision threshold:

```text
t50, t90, t99
mean discrimination time
spread of discrimination time
time-distribution entropy (with explicit binning)
```

Different source pairs can have very different `p_ij(t)` even under the same objective clock.

That is the conservative meaning of a **heterogeneous discrimination clock**:

```text
not different physical proper times,
not state-dependent spacetime,
but different evidence-arrival profiles for different source contrasts
under a specified receiver.
```

---

# Immediate next gate

Run on the exact already-used FCI/Hay `cell1.asc` tensor:

1. keep the same 16 source sites and same physical receiver sets;
2. compute `p_ij(t)`, `t50/t90/t99`, mean time and spread for every source pair;
3. compute the exact DFT phase/magnitude decomposition of each pair's final discrimination energy;
4. compute the source-contrast Gramian eigen-spectrum versus horizon;
5. keep soma-only and six-port views separate;
6. do not add a noise threshold yet;
7. do not claim Clockfield/Connes/black-hole support from the result.

Only after this gate consider a multi-output model-reduction experiment.

## One-line state

> **The reusable object is not a frozen-time field. It is a receiver-relative PSD information geometry whose infinitesimal growth is `Y(T)^T Y(T)`, whose pairwise maturity is a normalized evidence-arrival distribution, and whose measured discrimination can be decomposed exactly into phase and magnitude contributions.**
