#!/usr/bin/env python3
"""Monotone finite-horizon discrimination on the frozen Dig Q0 tensor.

Executes MONOTONE_DISCRIMINATION_GATE.md.

For source responses h_i and h_j observed through a fixed receiver map C,
compute cumulative pairwise separation energy

    D_T^2(i,j) = integral_0^T ||h_i(t)-h_j(t)||^2 dt.

Unlike the earlier row-normalized cosine/effective-rank proxy, D_T^2 is
nondecreasing with T by construction.  No noise scale or discriminability
threshold is fitted.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import space_time_observability_cell1 as sto


HORIZONS_MS = sto.HORIZONS_MS
RNG_SEED = 20260818
N_RANDOM_PER_K = 128
PAIR_MATURITY_THRESHOLDS = [0.50, 0.90, 0.99]
FRONTIER_REFERENCE_FRACTIONS = [0.10, 0.25, 0.50, 0.75, 0.90]


def summary(values):
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


def projection_summary(values):
    x = np.asarray(values, dtype=float)
    return {
        "n": int(x.size),
        "q05": float(np.quantile(x, 0.05)),
        "median": float(np.median(x)),
        "q95": float(np.quantile(x, 0.95)),
        "mean": float(np.mean(x)),
    }


def pairwise_d2_from_tensor(Y, dt_ms):
    """Return upper-triangle pairwise squared separation energy.

    Y shape: [source, channel, time]. Units of output are mV^2 ms.
    """
    X = Y.reshape(Y.shape[0], -1)
    g = np.sum(X * X, axis=1)
    D = g[:, None] + g[None, :] - 2.0 * (X @ X.T)
    D = np.maximum(D, 0.0) * float(dt_ms)
    iu = np.triu_indices(D.shape[0], 1)
    return D[iu]


def maturity_summary(current, final):
    current = np.asarray(current, dtype=float)
    final = np.asarray(final, dtype=float)
    if np.any(final <= 0.0):
        raise RuntimeError("Final pairwise discrimination contains non-positive pair")
    m = np.clip(current / final, 0.0, 1.0 + 1e-12)
    out = {
        "min": float(np.min(m)),
        "q10": float(np.quantile(m, 0.10)),
        "median": float(np.median(m)),
        "q90": float(np.quantile(m, 0.90)),
        "max": float(np.max(m)),
    }
    for threshold in PAIR_MATURITY_THRESHOLDS:
        out[f"fraction_pairs_ge_{threshold:.2f}"] = float(np.mean(m >= threshold))
    return out


def first_horizon(rows, predicate):
    for row in rows:
        if predicate(row):
            return row["horizon_ms"]
    return None


def physical_curve(A, rel_t, receiver_indices, dt_ms):
    final_mask = rel_t <= max(HORIZONS_MS) + 1e-12
    final_d2 = pairwise_d2_from_tensor(A[:, receiver_indices, :][:, :, final_mask], dt_ms)

    rows = []
    pair_curves = []
    for T in HORIZONS_MS:
        mask = rel_t <= T + 1e-12
        d2 = pairwise_d2_from_tensor(A[:, receiver_indices, :][:, :, mask], dt_ms)
        pair_curves.append(d2)
        rows.append(
            {
                "horizon_ms": T,
                "pairwise_D2_mV2_ms": summary(d2),
                "pairwise_final_fraction": maturity_summary(d2, final_d2),
            }
        )

    pair_curves = np.stack(pair_curves, axis=0)
    min_increment = float(np.min(np.diff(pair_curves, axis=0)))

    landmarks = {}
    for threshold in PAIR_MATURITY_THRESHOLDS:
        landmarks[f"first_median_maturity_ge_{threshold:.2f}_ms"] = first_horizon(
            rows,
            lambda r, th=threshold: r["pairwise_final_fraction"]["median"] >= th,
        )
        landmarks[f"first_90pct_pairs_ge_{threshold:.2f}_ms"] = first_horizon(
            rows,
            lambda r, th=threshold: r["pairwise_final_fraction"][
                f"fraction_pairs_ge_{th:.2f}"
            ]
            >= 0.90,
        )

    return rows, final_d2, min_increment, landmarks


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
        "--output",
        type=Path,
        default=Path("finite_horizon_discrimination_cell1_result.json"),
    )
    args = p.parse_args()

    A, rel_t, source_desc, receiver_desc = sto.simulate_tensor(args)
    if A.shape[1] != 6:
        raise RuntimeError(f"Expected six receivers, got {A.shape[1]}")
    if float(rel_t.max()) + 1e-9 < max(HORIZONS_MS):
        raise RuntimeError(
            f"Available response horizon {float(rel_t.max())} ms < {max(HORIZONS_MS)} ms"
        )

    soma_rows, soma_final_d2, soma_min_inc, soma_landmarks = physical_curve(
        A, rel_t, [0], args.dt_ms
    )
    six_rows, six_final_d2, six_min_inc, six_landmarks = physical_curve(
        A, rel_t, list(range(6)), args.dt_ms
    )

    reference_median = float(np.median(six_final_d2))
    if reference_median <= 0:
        raise RuntimeError("Non-positive six-port final median discrimination")

    rng = np.random.default_rng(RNG_SEED)
    projections = {
        k: [sto.random_orthonormal_columns(rng, 6, k) for _ in range(N_RANDOM_PER_K)]
        for k in range(1, 7)
    }

    # For monotonicity, retain each projection's 120-pair vector across horizons.
    random_curves = {
        k: [[None for _ in HORIZONS_MS] for _ in range(N_RANDOM_PER_K)]
        for k in range(1, 7)
    }

    frontier = []
    max_k6_relative_error = 0.0
    for ti, T in enumerate(HORIZONS_MS):
        mask = rel_t <= T + 1e-12
        At = A[:, :, mask]
        six_d2_T = pairwise_d2_from_tensor(At, args.dt_ms)

        by_k = []
        for k in range(1, 7):
            medians = []
            for pi, Q in enumerate(projections[k]):
                Y = sto.project_tensor(At, Q)
                d2 = pairwise_d2_from_tensor(Y, args.dt_ms)
                random_curves[k][pi][ti] = d2
                medians.append(float(np.median(d2)))

                if k == 6:
                    denom = np.maximum(np.abs(six_d2_T), 1e-30)
                    rel_err = float(np.max(np.abs(d2 - six_d2_T) / denom))
                    max_k6_relative_error = max(max_k6_relative_error, rel_err)

            dist = projection_summary(medians)
            dist["median_fraction_of_physical_six_120"] = float(
                dist["median"] / reference_median
            )
            by_k.append({"k": k, "median_pair_D2_over_projections": dist})
        frontier.append({"horizon_ms": T, "by_k": by_k})

    random_min_increment = float("inf")
    for k in range(1, 7):
        for pi in range(N_RANDOM_PER_K):
            curves = np.stack(random_curves[k][pi], axis=0)
            random_min_increment = min(
                random_min_increment,
                float(np.min(np.diff(curves, axis=0))),
            )

    frontier_landmarks = {}
    for k in range(1, 7):
        per_k = [row["by_k"][k - 1] for row in frontier]
        frontier_landmarks[str(k)] = {}
        for frac in FRONTIER_REFERENCE_FRACTIONS:
            hit = None
            for T, item in zip(HORIZONS_MS, per_k):
                if (
                    item["median_pair_D2_over_projections"][
                        "median_fraction_of_physical_six_120"
                    ]
                    >= frac
                ):
                    hit = T
                    break
            frontier_landmarks[str(k)][f"first_T_reach_{frac:.2f}_of_six120_ms"] = hit

    monotonicity_min_increment = min(
        soma_min_inc, six_min_inc, random_min_increment
    )
    monotonicity_guard = bool(monotonicity_min_increment >= -1e-12)
    k6_guard = bool(max_k6_relative_error < 1e-10)

    result = {
        "model": {
            "repository": "ido4848/FCI",
            "commit": "55826436751c03a32dfd39e91a48894869e1db57",
            "model": "Rat_L5b_PC_2_Hay_passive_dends_simple_soma / cell1.asc",
        },
        "protocol": {
            "horizons_ms": HORIZONS_MS,
            "rng_seed": RNG_SEED,
            "n_random_per_k": N_RANDOM_PER_K,
            "dt_ms": args.dt_ms,
            "amp_nA": args.amp_na,
            "dur_ms": args.dur_ms,
            "delay_ms": args.delay_ms,
            "tstop_ms": args.tstop_ms,
            "baseline_subtraction": "matched no-stimulus trajectory",
            "metric": "integral ||h_i-h_j||^2 dt (fixed-step Riemann sum)",
        },
        "source_sites": source_desc,
        "receiver_sites": receiver_desc,
        "physical": {
            "soma": {
                "rows": soma_rows,
                "final_120ms_pairwise_D2_mV2_ms": summary(soma_final_d2),
                "landmarks": soma_landmarks,
            },
            "six_port": {
                "rows": six_rows,
                "final_120ms_pairwise_D2_mV2_ms": summary(six_final_d2),
                "landmarks": six_landmarks,
            },
        },
        "six_port_120ms_median_reference_mV2_ms": reference_median,
        "random_projection_frontier": frontier,
        "frontier_landmarks": frontier_landmarks,
        "guards": {
            "physical_soma_min_increment_mV2_ms": soma_min_inc,
            "physical_six_min_increment_mV2_ms": six_min_inc,
            "random_projection_min_increment_mV2_ms": random_min_increment,
            "global_min_increment_mV2_ms": monotonicity_min_increment,
            "monotonicity_guard_ge_minus_1e_12": monotonicity_guard,
            "k6_max_pairwise_relative_error": max_k6_relative_error,
            "k6_invariance_guard_lt_1e_10": k6_guard,
        },
    }

    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")

    compact = {
        "soma_final_median_D2": float(np.median(soma_final_d2)),
        "six_final_median_D2": reference_median,
        "soma_landmarks": soma_landmarks,
        "six_landmarks": six_landmarks,
        "frontier_landmarks": frontier_landmarks,
        "global_min_increment": monotonicity_min_increment,
        "monotonicity_guard": monotonicity_guard,
        "k6_max_relative_error": max_k6_relative_error,
        "k6_guard": k6_guard,
    }
    print("MONOTONE_RESULT", json.dumps(compact, separators=(",", ":")))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
