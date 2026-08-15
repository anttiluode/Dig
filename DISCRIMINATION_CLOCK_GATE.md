# Gate — pair-specific discrimination clock and phase/magnitude decomposition

**Frozen:** 2026-08-15, before running the measurement.

## Question

On the exact FCI/Hay `cell1.asc` response tensor already used by the Dig receiver gates, is the surviving pair-specific maturity effect better described as a heterogeneous distribution of **when discrimination evidence arrives**, and how much of the final pairwise distinction on the measured window is carried by phase versus magnitude differences?

This is a measurement gate, not a novelty gate.

## Frozen biological protocol

Reuse without retuning:

```text
upstream repo/commit:
  ido4848/FCI
  55826436751c03a32dfd39e91a48894869e1db57

model:
  Rat_L5b_PC_2_Hay_passive_dends_simple_soma / cell1.asc

sources:
  same 8 basal + 8 apical path-order source sites

physical receivers:
  soma only
  soma + same 2 basal + 3 apical ports

stimulus:
  0.02 nA IClamp
  0.5 ms duration
  delay 20 ms

integration:
  dt = 0.05 ms
  analyze source-relative 0..120 ms

baseline:
  exact matched no-stimulus subtraction
```

No source, receiver, stimulus or membrane parameter may be changed after seeing the result.

---

# Measurement A — discrimination-time distribution

For each source pair `(i,j)` and physical readout `C`, define samplewise

```text
g_ij[n] = ||h_i[n]-h_j[n]||^2
```

on the frozen 0..120 ms window.

Normalize over the final window:

```text
p_ij[n] = g_ij[n] / sum_n g_ij[n].
```

This is a discrete probability mass over *when the pair's measured separation energy arrives*.

Its cumulative sum is the previously measured within-readout maturity curve.

For every pair report:

```text
t50_ms
t90_ms
t99_ms
mean_time_ms
std_time_ms
peak_time_ms
normalized_time_entropy = -sum p log p / log(N)
final_D2_mV2_ms
```

The entropy is explicitly a bin-dependent descriptive entropy of the normalized evidence-arrival distribution. It is not thermodynamic entropy and not mutual information.

Primary descriptive summaries across all 120 pairs:

```text
min / q10 / median / q90 / max
```

for `t50,t90,t99,mean_time,std_time,normalized_time_entropy`.

Do this separately for soma-only and six-port readouts.

No success threshold is preregistered. The goal is to quantify heterogeneity already implied by the previous maturity result.

---

# Measurement B — source-contrast Gramian spectrum

For each horizon

```text
T in [0.5, 1, 2, 5, 10, 20, 40, 80, 120] ms
```

construct the empirical source-space Gramian

```text
G_T = dt * X_T X_T^T
```

where each row of `X_T` is one source response flattened over the retained physical receiver channels and time prefix.

Project out the all-sources common direction with

```text
P = I - 11^T / n_sources
G_contrast,T = P G_T P.
```

Pairwise source distances are unchanged by this common-source centering.

Report the ordered eigenvalues of `G_contrast,T`, its trace, participation rank and entropy effective rank as descriptive spectrum summaries.

Important:

- each ordered eigenvalue should be nondecreasing with `T` up to numerical tolerance because `G_T` grows in PSD order;
- effective-rank summaries need not be monotone and must not be called literal observability rank.

Frozen guard:

```text
minimum ordered-eigenvalue increment >= -1e-10 * max(final top eigenvalue,1)
```

for both physical readouts.

---

# Measurement C — exact finite-window DFT phase/magnitude decomposition

For each source pair and physical readout, take the DFT of the frozen 120 ms response window.

For each frequency bin and receiver channel use

```text
|H_i-H_j|^2
  = (|H_i|-|H_j|)^2
    + 2(|H_i||H_j| - Re[H_i conj(H_j)]).
```

Call the first term `magnitude_component` and the second `phase_component`.

Both are nonnegative up to floating-point tolerance and sum exactly to total difference power.

Use correct one-sided real-FFT Parseval weights.

For every source pair report:

```text
magnitude_fraction
phase_fraction
spectral_centroid_hz       [of pair difference power]
normalized_spectral_entropy
```

The phase/magnitude fractions must sum to one up to numerical tolerance.

Frozen guards:

```text
max relative Parseval error < 1e-10
max |phase_fraction + magnitude_fraction - 1| < 1e-10
minimum phase component >= -1e-10 * max(total spectral power,1)
```

Windowing caveat: these are exact decompositions of the **measured finite window DFT**. Do not over-interpret individual bins as unwindowed physical eigenmodes.

---

# Measurement D — morphology/path descriptors, descriptive only

For each source pair derive only from frozen source metadata:

```text
max_path_um
mean_path_um
abs_path_difference_um
same_tree (basal/basal or apical/apical)
```

Report Spearman correlations of `t90_ms` with:

```text
max_path_um
abs_path_difference_um
final_D2
phase_fraction
```

separately for soma and six-port readouts.

These are exploratory descriptors. No p-value threshold, no selection of a favorable correlation after the run.

---

# Interpretation branches

## If discrimination-time distributions are narrow and nearly identical

Then the previous slow-tail result was carried by a small number of pairs and `heterogeneous discrimination clock` is not useful language. Keep only the pairwise matrix `D_C,T`.

## If they are broad across many pairs

Then it is fair to say:

> Different source contrasts under the same objective clock have measurably different evidence-arrival profiles at a fixed receiver.

Do **not** say different proper times, local clocks in the medium, or Clockfield validation.

## If phase fraction varies substantially across pairs

Then the old `phase versus magnitude` vocabulary has a concrete signal-processing role here.

Do **not** infer phase coding by the biological neuron merely from this decomposition; it is a decomposition of transfer responses.

## If phase fraction is uniformly tiny or uniformly dominant

Record that result as-is. Do not change the window or receiver set to manufacture a mixture.

---

# What this gate cannot establish

It cannot establish:

```text
Clockfield physics
black-hole/event-horizon mathematics
Connes spectral distance
thermodynamic entropy
a new observability theorem
state-dependent propagation geometry
biological phase coding
```

## Stop rule

After this run, do not tune it.

The next independent question, if warranted, is the multi-output model-reduction scaling suggested by the Kellems collision. That must get a separate gate because `reduced order ~ number of ports` is not a theorem.
