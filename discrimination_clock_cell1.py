#!/usr/bin/env python3
"""Pair-specific discrimination clock on the frozen Dig cell1 tensor.

Executes DISCRIMINATION_CLOCK_GATE.md.

No neuron parameter is fitted here.  The script reuses the exact tensor
simulator from space_time_observability_cell1.py and adds three analyses:

1. a normalized distribution over when each source pair's separation energy
   arrives;
2. the source-contrast Gramian eigen-spectrum versus horizon;
3. an exact finite-window DFT decomposition of pair discrimination into
   magnitude and phase contributions.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

import space_time_observability_cell1 as sto


HORIZONS_MS = sto.HORIZONS_MS
FINAL_T_MS = max(HORIZONS_MS)


def dist_summary(values):
    x = np.asarray(values, dtype=float)
    return {
        "n": int(x.size),
        "min": float(np.min(x)),
        "q10": float(np.quantile(x, 0.10)),
        "median": float(np.median(x)),
        "q90": float(np.quantile(x, 0.90)),
        "max": float(np.max(x)),
        "mean": float(np.mean(x)),
    }


def first_quantile_time(rel_t, cdf, q):
    idx = int(np.searchsorted(cdf, q, side="left"))
    idx = min(max(idx, 0), len(rel_t) - 1)
    return float(rel_t[idx])


def temporal_clock_rows(Y, rel_t, dt_ms, source_desc):
    """Y shape [source, channel, time] on final frozen window."""
    rows = []
    nsrc = Y.shape[0]
    for i in range(nsrc):
        for j in range(i + 1, nsrc):
            diff = Y[i] - Y[j]
            g = np.sum(diff * diff, axis=0)
            raw_total = float(np.sum(g))
            if raw_total <= 0.0:
                raise RuntimeError(f"Non-positive pair energy for {i},{j}")
            p = g / raw_total
            cdf = np.cumsum(p)
            tmean = float(np.sum(p * rel_t))
            tstd = float(np.sqrt(np.sum(p * (rel_t - tmean) ** 2)))
            nz = p > 0.0
            h = float(-np.sum(p[nz] * np.log(p[nz])))
            hnorm = h / np.log(len(p)) if len(p) > 1 else 0.0
            si = source_desc[i]
            sj = source_desc[j]
            rows.append(
                {
                    "i": i,
                    "j": j,
                    "t50_ms": first_quantile_time(rel_t, cdf, 0.50),
                    "t90_ms": first_quantile_time(rel_t, cdf, 0.90),
                    "t99_ms": first_quantile_time(rel_t, cdf, 0.99),
                    "mean_time_ms": tmean,
                    "std_time_ms": tstd,
                    "peak_time_ms": float(rel_t[int(np.argmax(g))]),
                    "normalized_time_entropy": hnorm,
                    "final_D2_mV2_ms": raw_total * float(dt_ms),
                    "max_path_um": float(max(si["path_um"], sj["path_um"])),
                    "mean_path_um": float(0.5 * (si["path_um"] + sj["path_um"])),
                    "abs_path_difference_um": float(abs(si["path_um"] - sj["path_um"])),
                    "same_tree": bool(si["kind"] == sj["kind"]),
                }
            )
    return rows


def rows_summary(rows):
    keys = [
        "t50_ms",
        "t90_ms",
        "t99_ms",
        "mean_time_ms",
        "std_time_ms",
        "normalized_time_entropy",
        "final_D2_mV2_ms",
    ]
    return {k: dist_summary([r[k] for r in rows]) for k in keys}


def contrast_spectrum(A, rel_t, receiver_indices, dt_ms):
    nsrc = A.shape[0]
    P = np.eye(nsrc) - np.ones((nsrc, nsrc)) / float(nsrc)
    rows = []
    eigs_all = []
    for T in HORIZONS_MS:
        mask = rel_t <= T + 1e-12
        X = A[:, receiver_indices, :][:, :, mask].reshape(nsrc, -1)
        G = float(dt_ms) * (X @ X.T)
        Gc = P @ G @ P
        Gc = 0.5 * (Gc + Gc.T)
        eig = np.linalg.eigvalsh(Gc)[::-1]
        # Only remove tiny negative roundoff; do not threshold positive modes.
        eig = np.maximum(eig, 0.0)
        trace = float(np.sum(eig))
        if trace > 0.0:
            p = eig / trace
            pos = p > 0.0
            erank = float(np.exp(-np.sum(p[pos] * np.log(p[pos]))))
            prank = float(trace * trace / max(float(np.sum(eig * eig)), 1e-300))
        else:
            erank = 0.0
            prank = 0.0
        rows.append(
            {
                "horizon_ms": float(T),
                "eigenvalues_mV2_ms": [float(v) for v in eig],
                "trace_mV2_ms": trace,
                "entropy_effective_rank": erank,
                "participation_rank": prank,
            }
        )
        eigs_all.append(eig)
    E = np.stack(eigs_all, axis=0)
    min_inc = float(np.min(np.diff(E, axis=0)))
    final_top = float(max(E[-1, 0], 1.0))
    guard = bool(min_inc >= -1e-10 * final_top)
    return rows, min_inc, guard


def rfft_weights(n):
    nf = n // 2 + 1
    w = np.full(nf, 2.0, dtype=float)
    w[0] = 1.0
    if n % 2 == 0:
        w[-1] = 1.0
    return w


def phase_magnitude_rows(Y, dt_ms, clock_rows):
    """Exact DFT decomposition on the frozen finite window."""
    n = Y.shape[2]
    F = np.fft.rfft(Y, axis=2)
    freqs = np.fft.rfftfreq(n, d=float(dt_ms) / 1000.0)
    w = rfft_weights(n)
    rows = []
    max_parseval_rel = 0.0
    max_fraction_err = 0.0
    min_phase_component = float("inf")
    max_total_power = 0.0

    clock_by_pair = {(r["i"], r["j"]): r for r in clock_rows}

    for i in range(Y.shape[0]):
        for j in range(i + 1, Y.shape[0]):
            Fi = F[i]
            Fj = F[j]
            ai = np.abs(Fi)
            aj = np.abs(Fj)
            mag = (ai - aj) ** 2
            phase = 2.0 * (ai * aj - np.real(Fi * np.conj(Fj)))
            total = np.abs(Fi - Fj) ** 2

            min_phase_component = min(min_phase_component, float(np.min(phase)))
            max_total_power = max(max_total_power, float(np.max(total)))

            weighted_mag = float(np.sum(mag * w[None, :]))
            weighted_phase = float(np.sum(phase * w[None, :]))
            weighted_total = float(np.sum(total * w[None, :]))
            if weighted_total <= 0.0:
                raise RuntimeError(f"Non-positive spectral pair power {i},{j}")

            frac_mag = weighted_mag / weighted_total
            frac_phase = weighted_phase / weighted_total
            max_fraction_err = max(max_fraction_err, abs(frac_mag + frac_phase - 1.0))

            time_power = float(np.sum((Y[i] - Y[j]) ** 2))
            spec_time_power = weighted_total / float(n)
            rel = abs(spec_time_power - time_power) / max(abs(time_power), 1e-300)
            max_parseval_rel = max(max_parseval_rel, rel)

            # One-sided full-spectrum-equivalent pair difference power by frequency.
            pf = w * np.sum(total, axis=0)
            psum = float(np.sum(pf))
            centroid = float(np.sum(freqs * pf) / psum)
            pp = pf / psum
            pos = pp > 0.0
            hs = float(-np.sum(pp[pos] * np.log(pp[pos])))
            hsn = hs / np.log(len(pp)) if len(pp) > 1 else 0.0

            base = clock_by_pair[(i, j)]
            rows.append(
                {
                    "i": i,
                    "j": j,
                    "magnitude_fraction": float(frac_mag),
                    "phase_fraction": float(frac_phase),
                    "spectral_centroid_hz": centroid,
                    "normalized_spectral_entropy": hsn,
                    "t90_ms": base["t90_ms"],
                    "final_D2_mV2_ms": base["final_D2_mV2_ms"],
                    "max_path_um": base["max_path_um"],
                    "abs_path_difference_um": base["abs_path_difference_um"],
                }
            )

    guards = {
        "max_parseval_relative_error": float(max_parseval_rel),
        "max_phase_plus_magnitude_fraction_error": float(max_fraction_err),
        "minimum_raw_phase_component": float(min_phase_component),
        "max_raw_total_component": float(max_total_power),
        "parseval_guard_lt_1e_10": bool(max_parseval_rel < 1e-10),
        "fraction_sum_guard_lt_1e_10": bool(max_fraction_err < 1e-10),
        "phase_nonnegative_guard": bool(
            min_phase_component >= -1e-10 * max(max_total_power, 1.0)
        ),
    }
    return rows, guards


def spectral_rows_summary(rows):
    keys = [
        "magnitude_fraction",
        "phase_fraction",
        "spectral_centroid_hz",
        "normalized_spectral_entropy",
    ]
    return {k: dist_summary([r[k] for r in rows]) for k in keys}


def safe_spearman(x, y):
    r = spearmanr(np.asarray(x, dtype=float), np.asarray(y, dtype=float))
    return {
        "rho": float(r.statistic) if np.isfinite(r.statistic) else None,
        "p_value_descriptive_only": float(r.pvalue) if np.isfinite(r.pvalue) else None,
    }


def correlations(clock_rows, spectral_rows):
    spec = {(r["i"], r["j"]): r for r in spectral_rows}
    t90 = [r["t90_ms"] for r in clock_rows]
    return {
        "t90_vs_max_path_um": safe_spearman(t90, [r["max_path_um"] for r in clock_rows]),
        "t90_vs_abs_path_difference_um": safe_spearman(
            t90, [r["abs_path_difference_um"] for r in clock_rows]
        ),
        "t90_vs_final_D2": safe_spearman(t90, [r["final_D2_mV2_ms"] for r in clock_rows]),
        "t90_vs_phase_fraction": safe_spearman(
            t90, [spec[(r["i"], r["j"])]["phase_fraction"] for r in clock_rows]
        ),
    }


def analyze_readout(A, rel_t, receiver_indices, dt_ms, source_desc):
    mask = rel_t <= FINAL_T_MS + 1e-12
    rt = rel_t[mask]
    Y = A[:, receiver_indices, :][:, :, mask]
    clock = temporal_clock_rows(Y, rt, dt_ms, source_desc)
    spectrum, min_eig_inc, eig_guard = contrast_spectrum(
        A, rel_t, receiver_indices, dt_ms
    )
    phase_rows, dft_guards = phase_magnitude_rows(Y, dt_ms, clock)
    return {
        "receiver_indices": [int(i) for i in receiver_indices],
        "clock_pairs": clock,
        "clock_summary": rows_summary(clock),
        "contrast_spectrum_by_horizon": spectrum,
        "spectral_pair_rows": phase_rows,
        "spectral_pair_summary": spectral_rows_summary(phase_rows),
        "correlations": correlations(clock, phase_rows),
        "guards": {
            "min_ordered_eigenvalue_increment": min_eig_inc,
            "ordered_eigenvalue_monotonicity_guard": eig_guard,
            **dft_guards,
        },
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fci-root", type=Path, required=True)
    p.add_argument("--sources-per-tree", type=int, default=8)
    p.add_argument("--amp-na", type=float, default=0.02)
    p.add_argument("--delay-ms", type=float, default=20.0)
    p.add_argument("--dur-ms", type=float, default=0.5)
    p.add_argument("--tstop-ms", type=float, default=140.05)
    p.add_argument("--v-init-mv", type=float, default=-70.0)
    p.add_argument("--dt-ms", type=float, default=0.05)
    p.add_argument(
        "--output", type=Path, default=Path("discrimination_clock_cell1_result.json")
    )
    args = p.parse_args()

    A, rel_t, source_desc, receiver_desc = sto.simulate_tensor(args)
    if A.shape[0] != 16 or A.shape[1] != 6:
        raise RuntimeError(f"Expected [16,6,time] tensor, got {A.shape}")
    if float(rel_t.max()) + 1e-9 < FINAL_T_MS:
        raise RuntimeError("Insufficient final horizon")

    soma = analyze_readout(A, rel_t, [0], args.dt_ms, source_desc)
    six = analyze_readout(A, rel_t, list(range(6)), args.dt_ms, source_desc)

    all_guards = [
        soma["guards"]["ordered_eigenvalue_monotonicity_guard"],
        six["guards"]["ordered_eigenvalue_monotonicity_guard"],
        soma["guards"]["parseval_guard_lt_1e_10"],
        six["guards"]["parseval_guard_lt_1e_10"],
        soma["guards"]["fraction_sum_guard_lt_1e_10"],
        six["guards"]["fraction_sum_guard_lt_1e_10"],
        soma["guards"]["phase_nonnegative_guard"],
        six["guards"]["phase_nonnegative_guard"],
    ]

    result = {
        "model": {
            "repository": "ido4848/FCI",
            "commit": "55826436751c03a32dfd39e91a48894869e1db57",
            "model": "Rat_L5b_PC_2_Hay_passive_dends_simple_soma / cell1.asc",
        },
        "protocol": {
            "final_horizon_ms": FINAL_T_MS,
            "horizons_ms": HORIZONS_MS,
            "dt_ms": args.dt_ms,
            "amp_nA": args.amp_na,
            "dur_ms": args.dur_ms,
            "delay_ms": args.delay_ms,
            "baseline_subtraction": "matched no-stimulus trajectory",
        },
        "source_sites": source_desc,
        "receiver_sites": receiver_desc,
        "soma": soma,
        "six_port": six,
        "all_frozen_guards_pass": bool(all(all_guards)),
    }
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")

    compact = {
        "soma_t90": soma["clock_summary"]["t90_ms"],
        "six_t90": six["clock_summary"]["t90_ms"],
        "soma_phase_fraction": soma["spectral_pair_summary"]["phase_fraction"],
        "six_phase_fraction": six["spectral_pair_summary"]["phase_fraction"],
        "soma_t90_vs_phase_rho": soma["correlations"]["t90_vs_phase_fraction"]["rho"],
        "six_t90_vs_phase_rho": six["correlations"]["t90_vs_phase_fraction"]["rho"],
        "all_guards_pass": bool(all(all_guards)),
    }
    print("DISCRIM_CLOCK_RESULT", json.dumps(compact, separators=(",", ":")))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
