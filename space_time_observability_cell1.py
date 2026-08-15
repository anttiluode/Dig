#!/usr/bin/env python3
"""Space-time observability frontier on the frozen Dig Q0 response tensor.

Executes SPACE_TIME_OBSERVABILITY_GATE.md.

Biology is unchanged from receiver_collapse_cell1.py.  After measuring the
matched-subtracted tensor A[source, receiver, time], this script varies only:

- temporal prefix T after the source pulse
- retained receiver-output dimension k

The experiment is a finite-horizon observability-inspired measurement and not
a novelty claim.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import pearsonr, spearmanr

import receiver_collapse_cell1 as q0


HORIZONS_MS = [0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 40.0, 80.0, 120.0]
RNG_SEED = 20260817
N_RANDOM_PER_K = 128


def distribution_summary(values):
    x = np.asarray(values, dtype=float)
    return {
        "n": int(x.size),
        "min": float(np.min(x)),
        "q05": float(np.quantile(x, 0.05)),
        "q25": float(np.quantile(x, 0.25)),
        "median": float(np.median(x)),
        "mean": float(np.mean(x)),
        "q75": float(np.quantile(x, 0.75)),
        "q95": float(np.quantile(x, 0.95)),
        "max": float(np.max(x)),
        "std": float(np.std(x)),
    }


def cosine_distance_matrix(X, eps=1e-15):
    Xn = q0.row_normalize(X, eps=eps)
    sim = np.clip(Xn @ Xn.T, -1.0, 1.0)
    D = 1.0 - sim
    np.fill_diagonal(D, 0.0)
    return D


def nearest_neighbors(D):
    D = np.asarray(D, dtype=float)
    masked = D + np.eye(D.shape[0]) * 1e9
    return masked.argmin(axis=1)


def geometry_summary(X):
    s = q0.signature_summary(X)
    D = cosine_distance_matrix(X)
    return s, D


def compare_to_final(D, D_final):
    D = np.asarray(D, dtype=float)
    Df = np.asarray(D_final, dtype=float)
    iu = np.triu_indices(D.shape[0], 1)
    a = D[iu]
    b = Df[iu]
    if np.std(a) <= 1e-15 or np.std(b) <= 1e-15:
        pear = float("nan")
        spear = float("nan")
    else:
        pear = float(pearsonr(a, b).statistic)
        spear = float(spearmanr(a, b).statistic)
    nn = nearest_neighbors(D)
    nnf = nearest_neighbors(Df)
    return {
        "pearson_to_final": pear,
        "spearman_to_final": spear,
        "nearest_neighbor_agreement": float(np.mean(nn == nnf)),
        "nearest_neighbor_match_count": int(np.sum(nn == nnf)),
        "relative_frobenius_to_final": float(
            np.linalg.norm(D - Df) / max(np.linalg.norm(Df), 1e-15)
        ),
    }


def random_orthonormal_columns(rng, n, k):
    G = rng.normal(size=(n, k))
    Q, R = np.linalg.qr(G, mode="reduced")
    signs = np.sign(np.diag(R))
    signs[signs == 0] = 1.0
    return Q * signs[np.newaxis, :]


def project_tensor(A, Q):
    # A [source, receiver, time], Q [receiver, k]
    # Y [source, k, time]
    return np.einsum("rk,srt->skt", Q, A, optimize=True)


def simulate_tensor(args):
    h, module = q0.import_model(args.fci_root)
    cell, syn_df = module.create_cell()
    h.cvode_active(0)
    h.dt = float(args.dt_ms)
    h.steps_per_ms = max(1.0, 1.0 / float(args.dt_ms))
    h.tstop = float(args.tstop_ms)

    q0.set_distance_origin(h, cell)
    segs = q0.unique_dendritic_segments(syn_df)
    basal = sorted(
        [s for s in segs if q0.kind(s) == "basal"],
        key=lambda s: q0.path_distance_um(h, s),
    )
    apical = sorted(
        [s for s in segs if q0.kind(s) == "apical"],
        key=lambda s: q0.path_distance_um(h, s),
    )

    sources = q0.pick_evenly(basal, args.sources_per_tree) + q0.pick_evenly(
        apical, args.sources_per_tree
    )
    receivers = [cell.soma[0](0.5)]
    receivers += q0.pick_quantiles(basal, [0.25, 0.75])
    receivers += q0.pick_quantiles(apical, [0.20, 0.55, 0.90])

    control_t, control_v = q0.run_voltage_trajectory(
        h,
        receivers,
        source=None,
        delay_ms=args.delay_ms,
        dur_ms=args.dur_ms,
        tstop_ms=args.tstop_ms,
        v_init_mv=args.v_init_mv,
    )
    post = (control_t >= args.delay_ms) & (control_t <= args.tstop_ms)
    rel_t = control_t[post] - args.delay_ms

    traces = []
    for idx, src in enumerate(sources):
        tt, vv = q0.run_voltage_trajectory(
            h,
            receivers,
            source=src,
            amp_nA=args.amp_na,
            delay_ms=args.delay_ms,
            dur_ms=args.dur_ms,
            tstop_ms=args.tstop_ms,
            v_init_mv=args.v_init_mv,
        )
        if tt.shape != control_t.shape or not np.allclose(
            tt, control_t, atol=1e-12, rtol=0.0
        ):
            raise RuntimeError("Stimulus/control time grids differ")
        dv = (vv - control_v)[:, post]
        traces.append(dv)
        print(
            f"source {idx+1:02d}/{len(sources)} "
            f"{q0.canonical_sec_name(src.sec)}({float(src.x):.4f}) "
            f"path={q0.path_distance_um(h, src):.1f} um "
            f"peak_soma={float(np.max(np.abs(dv[0]))):.9g} mV"
        )

    A = np.stack(traces, axis=0)
    receiver_desc = []
    for r in receivers:
        if q0.canonical_sec_name(r.sec) == q0.canonical_sec_name(cell.soma[0]):
            receiver_desc.append(
                {
                    "section": q0.canonical_sec_name(r.sec),
                    "x": float(r.x),
                    "path_um": 0.0,
                    "kind": "soma",
                }
            )
        else:
            receiver_desc.append(q0.describe_seg(h, r))
    source_desc = [q0.describe_seg(h, s) for s in sources]
    return A, rel_t, source_desc, receiver_desc


def first_horizon(rows, predicate):
    for row in rows:
        if predicate(row):
            return row["horizon_ms"]
    return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fci-root", type=Path, required=True)
    p.add_argument("--sources-per-tree", type=int, default=8)
    p.add_argument("--amp-na", type=float, default=0.02)
    p.add_argument("--delay-ms", type=float, default=20.0)
    p.add_argument("--dur-ms", type=float, default=0.5)
    p.add_argument("--tstop-ms", type=float, default=140.0)
    p.add_argument("--v-init-mv", type=float, default=-70.0)
    p.add_argument("--dt-ms", type=float, default=0.05)
    p.add_argument(
        "--output", type=Path, default=Path("space_time_observability_cell1_result.json")
    )
    args = p.parse_args()

    A, rel_t, source_desc, receiver_desc = simulate_tensor(args)
    if A.shape[1] != 6:
        raise RuntimeError(f"Expected six receivers, got {A.shape[1]}")

    max_available = float(rel_t.max())
    if max_available + 1e-9 < max(HORIZONS_MS):
        raise RuntimeError(
            f"Requested horizon {max(HORIZONS_MS)} exceeds available {max_available} ms"
        )

    # Final reference geometry at 120 ms.
    final_mask = rel_t <= max(HORIZONS_MS) + 1e-12
    A_final = A[:, :, final_mask]
    soma_final_X = A_final[:, 0, :]
    six_final_X = A_final.reshape(A.shape[0], -1)
    soma_final_summary, soma_D_final = geometry_summary(soma_final_X)
    six_final_summary, six_D_final = geometry_summary(six_final_X)

    full_energy_soma = float(np.sum(soma_final_X * soma_final_X))
    full_energy_six = float(np.sum(A_final * A_final))

    physical_rows = {"soma": [], "six_port": []}
    for T in HORIZONS_MS:
        mask = rel_t <= T + 1e-12
        At = A[:, :, mask]
        soma_X = At[:, 0, :]
        six_X = At.reshape(A.shape[0], -1)

        soma_s, soma_D = geometry_summary(soma_X)
        six_s, six_D = geometry_summary(six_X)

        soma_cmp = compare_to_final(soma_D, soma_D_final)
        six_cmp = compare_to_final(six_D, six_D_final)

        physical_rows["soma"].append(
            {
                "horizon_ms": T,
                **{k: v for k, v in soma_s.items() if k != "singular_values"},
                "energy_fraction_of_120ms": float(
                    np.sum(soma_X * soma_X) / max(full_energy_soma, 1e-30)
                ),
                **soma_cmp,
            }
        )
        physical_rows["six_port"].append(
            {
                "horizon_ms": T,
                **{k: v for k, v in six_s.items() if k != "singular_values"},
                "energy_fraction_of_120ms": float(
                    np.sum(At * At) / max(full_energy_six, 1e-30)
                ),
                **six_cmp,
            }
        )

    maturation_landmarks = {}
    for key, rows in physical_rows.items():
        maturation_landmarks[key] = {
            "first_pearson_ge_0_90_ms": first_horizon(
                rows, lambda r: np.isfinite(r["pearson_to_final"]) and r["pearson_to_final"] >= 0.90
            ),
            "first_pearson_ge_0_99_ms": first_horizon(
                rows, lambda r: np.isfinite(r["pearson_to_final"]) and r["pearson_to_final"] >= 0.99
            ),
            "first_nn_agreement_ge_0_75_ms": first_horizon(
                rows, lambda r: r["nearest_neighbor_agreement"] >= 0.75
            ),
            "first_nn_agreement_eq_1_ms": first_horizon(
                rows, lambda r: r["nearest_neighbor_agreement"] >= 1.0 - 1e-12
            ),
        }

    # Fixed random readout ensembles by k, reused across all horizons.
    rng = np.random.default_rng(RNG_SEED)
    projections = {}
    for k in range(1, 7):
        projections[k] = [
            random_orthonormal_columns(rng, 6, k) for _ in range(N_RANDOM_PER_K)
        ]

    frontier_rows = []
    k6_errors = []
    for T in HORIZONS_MS:
        mask = rel_t <= T + 1e-12
        At = A[:, :, mask]
        six_X = At.reshape(A.shape[0], -1)
        six_s = q0.signature_summary(six_X)

        by_k = []
        for k in range(1, 7):
            eranks = []
            pranks = []
            pairmed = []
            nnmed = []
            for Q in projections[k]:
                Y = project_tensor(At, Q)
                X = Y.reshape(Y.shape[0], -1)
                s = q0.signature_summary(X)
                eranks.append(s["entropy_effective_rank"])
                pranks.append(s["participation_rank"])
                pairmed.append(s["pairwise_cosine_median"])
                nnmed.append(s["nearest_cosine_median"])
                if k == 6:
                    k6_errors.append(
                        abs(s["entropy_effective_rank"] - six_s["entropy_effective_rank"])
                    )
            by_k.append(
                {
                    "k": k,
                    "entropy_effective_rank": distribution_summary(eranks),
                    "participation_rank": distribution_summary(pranks),
                    "pairwise_cosine_median": distribution_summary(pairmed),
                    "nearest_cosine_median": distribution_summary(nnmed),
                }
            )
        frontier_rows.append({"horizon_ms": T, "by_k": by_k})

    max_k6_error = float(max(k6_errors))
    k6_guard = bool(max_k6_error < 1e-8)

    # Convenience median grid: rows horizons, columns k=1..6.
    median_rank_grid = []
    for row in frontier_rows:
        median_rank_grid.append(
            {
                "horizon_ms": row["horizon_ms"],
                "median_entropy_rank_by_k": [
                    item["entropy_effective_rank"]["median"] for item in row["by_k"]
                ],
            }
        )

    # A simple measured space-time comparison: how early can each k reach the
    # final soma entropy rank? This is descriptive, not a success threshold.
    soma_final_rank = float(soma_final_summary["entropy_effective_rank"])
    first_horizon_reaching_soma_final_rank = {}
    for k in range(1, 7):
        hit = None
        for row in frontier_rows:
            med = row["by_k"][k - 1]["entropy_effective_rank"]["median"]
            if med >= soma_final_rank:
                hit = row["horizon_ms"]
                break
        first_horizon_reaching_soma_final_rank[str(k)] = hit

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
            "sources_per_tree": args.sources_per_tree,
            "amp_nA": args.amp_na,
            "delay_ms": args.delay_ms,
            "dur_ms": args.dur_ms,
            "tstop_ms": args.tstop_ms,
            "v_init_mV": args.v_init_mv,
            "dt_ms": args.dt_ms,
            "baseline_subtraction": "matched no-stimulus trajectory",
        },
        "source_sites": source_desc,
        "receiver_sites": receiver_desc,
        "final_120ms": {
            "soma_only": soma_final_summary,
            "six_port": six_final_summary,
        },
        "physical_horizon_curves": physical_rows,
        "maturation_landmarks": maturation_landmarks,
        "random_projection_frontier": frontier_rows,
        "median_entropy_rank_grid": median_rank_grid,
        "first_horizon_random_k_median_reaches_final_soma_rank_ms": first_horizon_reaching_soma_final_rank,
        "k6_orthonormal_invariance": {
            "max_entropy_rank_abs_error": max_k6_error,
            "guard_lt_1e8": k6_guard,
        },
    }

    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")

    compact = {
        "soma_final_erank": soma_final_rank,
        "six_final_erank": six_final_summary["entropy_effective_rank"],
        "soma_maturation": maturation_landmarks["soma"],
        "six_maturation": maturation_landmarks["six_port"],
        "first_T_reach_soma_final_rank_by_k": first_horizon_reaching_soma_final_rank,
        "rank_grid": [
            [r["horizon_ms"], *r["median_entropy_rank_by_k"]] for r in median_rank_grid
        ],
        "k6_invariance_max_error": max_k6_error,
        "k6_invariance_guard": k6_guard,
    }
    print("SPACE_TIME_RESULT", json.dumps(compact, separators=(",", ":")))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
