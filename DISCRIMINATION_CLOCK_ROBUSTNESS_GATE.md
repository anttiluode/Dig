# Post-hoc robustness gate — discrimination clock

**Frozen:** 2026-08-15 after the first `DISCRIMINATION_CLOCK_GATE.md` result, before running these controls.

The primary gate revealed that source 6 (`dend[67](0.9444)`) lies on the same branch as physical receiver 2 (`dend[67](0.7222)`) and creates very large local separation energy. This overlap was already documented in the earlier Q0 receiver work, but it can dominate source-space spectral summaries.

This is therefore a robustness control, not part of the original preregistration.

## Frozen controls

Reuse the exact same neuron tensor and analysis definitions.

Compare:

```text
R0      soma only                        [receiver 0]
R6      all six physical receivers       [0,1,2,3,4,5]
J1      R6 minus receiver 1              [0,2,3,4,5]
J2      R6 minus receiver 2              [0,1,3,4,5]  <-- removes same-dend[67] local port
J3      R6 minus receiver 3              [0,1,2,4,5]
J4      R6 minus receiver 4              [0,1,2,3,5]
J5      R6 minus receiver 5              [0,1,2,3,4]
```

For each readout report across all 120 source pairs:

```text
t90 min/q10/median/q90/max
phase-fraction min/q10/median/q90/max
Spearman t90 vs max_path
Spearman t90 vs phase_fraction
final source-contrast Gramian top eigenvalue
final contrast spectral participation rank
```

Also for R6 and J2 report the same summaries after excluding all 15 pairs containing source 6. This is a source-pair robustness diagnostic, not permission to redefine the source panel for the primary result.

## Interpretation rule

The claims

```text
pair discrimination times are broadly heterogeneous
phase contribution is pair-dependent
```

survive only if they remain visibly broad in J2 and in the source-6-excluded diagnostic.

Do not require the exact correlations or medians to be invariant.

The claim

```text
the six-port Gramian spectrum itself is a morphology fingerprint
```

is **not earned** by the primary run and should remain quarantined unless the spectrum is qualitatively robust to dropping the same-branch receiver.

No receiver is moved or optimized in this control.
