#!/usr/bin/env python3
"""Equal-dimensional receiver control for Dig Q0.

Executes RECEIVER_DIMENSION_CONTROL_GATE.md.  The biology and impulse protocol
are identical to receiver_collapse_cell1.py.  The only new work happens after
the matched-subtracted response tensor A[source, receiver, time] has been
measured: compare the soma with individual dendritic receivers and with fixed-
seed random receiver projections of the same retained dimension.

This is a control on interpretation, not a new biological hypothesis.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np

import receiver_collapse_cell1 as q0


RNG_SEED = 20260815
N_RANDOM_1D = 512
N_RANDOM_K = 256


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


def percentile_leq(value, samples):
    x = np.asarray(samples, dtype=float)
    return float(100.0 * np.mean(x <= float(value)))


def one_dim_projection_matrix(A, w):
    # A: [source, receiver, time], w: [receiver]
    return np.einsum("r,srt->st", w, A, optimize=True)


def k_dim_projection_matrix(A, Q):
    # Q has shape [receiver, k] with orthonormal columns.
    Y = np.einsum("rk,srt->skt", Q, A, optimize=True)
    return Y.reshape(Y.shape[0], -1)


def random_unit_vector(rng, n):
    w = rng.normal(size=n)
    w /= np.linalg.norm(w)
    return w


def random_orthonormal_columns(rng, n, k):
    G = rng.normal(size=(n, k))
    Q, R = np.linalg.qr(G, mode="reduced")
    # Fix the arbitrary QR sign convention deterministically.
    signs = np.sign(np.diag(R))
    signs[signs == 0] = 1.0
    Q = Q * signs[np.newaxis, :]
    return Q


def simulate_q0_tensor(args):
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
    if not np.any(post):
        raise RuntimeError("No post-stimulus samples")

    traces = []
    soma_peaks = []
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
        soma_peaks.append(float(np.max(np.abs(dv[0]))))
        print(
            f"source {idx+1:02d}/{len(sources)} "
            f"{q0.canonical_sec_name(src.sec)}({float(src.x):.4f}) "
            f"path={q0.path_distance_um(h, src):.1f} um "
            f"peak_soma={soma_peaks[-1]:.9g} mV"
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
    return A, source_desc, receiver_desc, soma_peaks


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
        "--output", type=Path, default=Path("receiver_dimension_control_cell1_result.json")
    )
    args = p.parse_args()

    A, source_desc, receiver_desc, soma_peaks = simulate_q0_tensor(args)
    n_receivers = A.shape[1]
    if n_receivers != 6:
        raise RuntimeError(f"Gate expects six receivers, got {n_receivers}")

    full_summary = q0.signature_summary(A.reshape(A.shape[0], -1))

    receiver_only = []
    for r in range(n_receivers):
        s = q0.signature_summary(A[:, r, :])
        s["receiver_index"] = r
        s["receiver"] = receiver_desc[r]
        receiver_only.append(s)

    soma_summary = receiver_only[0]
    dend_eranks = [s["entropy_effective_rank"] for s in receiver_only[1:]]

    rng = np.random.default_rng(RNG_SEED)

    random_1d = []
    for _ in range(N_RANDOM_1D):
        w = random_unit_vector(rng, n_receivers)
        s = q0.signature_summary(one_dim_projection_matrix(A, w))
        random_1d.append(
            {
                "entropy_effective_rank": s["entropy_effective_rank"],
                "participation_rank": s["participation_rank"],
                "pairwise_cosine_median": s["pairwise_cosine_median"],
                "nearest_cosine_median": s["nearest_cosine_median"],
            }
        )

    random_1d_erank = [x["entropy_effective_rank"] for x in random_1d]
    random_1d_pair = [x["pairwise_cosine_median"] for x in random_1d]
    random_1d_nn = [x["nearest_cosine_median"] for x in random_1d]

    # Reinitialize a separate stream for the preregistered dimension curve so
    # its samples are invariant to the number of C2 projections above.
    rng_k = np.random.default_rng(RNG_SEED + 1)
    dimension_curve = []
    full_invariance_errors = []

    all_indices = tuple(range(n_receivers))
    for k in range(1, n_receivers + 1):
        random_rows = []
        for _ in range(N_RANDOM_K):
            Q = random_orthonormal_columns(rng_k, n_receivers, k)
            s = q0.signature_summary(k_dim_projection_matrix(A, Q))
            random_rows.append(
                {
                    "entropy_effective_rank": s["entropy_effective_rank"],
                    "participation_rank": s["participation_rank"],
                    "pairwise_cosine_median": s["pairwise_cosine_median"],
                    "nearest_cosine_median": s["nearest_cosine_median"],
                }
            )
            if k == n_receivers:
                full_invariance_errors.append(
                    abs(s["entropy_effective_rank"] - full_summary["entropy_effective_rank"])
                )

        physical_subsets = []
        for subset in itertools.combinations(all_indices, k):
            s = q0.signature_summary(q0.subset_matrix(A, subset))
            physical_subsets.append(
                {
                    "receiver_indices": list(subset),
                    "entropy_effective_rank": s["entropy_effective_rank"],
                    "participation_rank": s["participation_rank"],
                    "pairwise_cosine_median": s["pairwise_cosine_median"],
                    "nearest_cosine_median": s["nearest_cosine_median"],
                }
            )

        dimension_curve.append(
            {
                "k": k,
                "random_projection": {
                    "entropy_effective_rank": distribution_summary(
                        [x["entropy_effective_rank"] for x in random_rows]
                    ),
                    "participation_rank": distribution_summary(
                        [x["participation_rank"] for x in random_rows]
                    ),
                    "pairwise_cosine_median": distribution_summary(
                        [x["pairwise_cosine_median"] for x in random_rows]
                    ),
                },
                "physical_subsets": physical_subsets,
                "physical_entropy_rank": distribution_summary(
                    [x["entropy_effective_rank"] for x in physical_subsets]
                ),
            }
        )

    max_k6_invariance_error = float(max(full_invariance_errors))
    invariance_guard = bool(max_k6_invariance_error < 1e-8)

    result = {
        "model": {
            "repository": "ido4848/FCI",
            "commit": "55826436751c03a32dfd39e91a48894869e1db57",
            "model": "Rat_L5b_PC_2_Hay_passive_dends_simple_soma / cell1.asc",
        },
        "protocol": {
            "sources_per_tree": args.sources_per_tree,
            "amp_nA": args.amp_na,
            "delay_ms": args.delay_ms,
            "dur_ms": args.dur_ms,
            "tstop_ms": args.tstop_ms,
            "v_init_mV": args.v_init_mv,
            "dt_ms": args.dt_ms,
            "baseline_subtraction": "matched no-stimulus trajectory",
            "rng_seed_random_1d": RNG_SEED,
            "n_random_1d": N_RANDOM_1D,
            "rng_seed_dimension_curve": RNG_SEED + 1,
            "n_random_per_k": N_RANDOM_K,
        },
        "source_sites": source_desc,
        "receiver_sites": receiver_desc,
        "soma_peak_mV": soma_peaks,
        "full_six_port": full_summary,
        "receiver_only": receiver_only,
        "equal_dimensional_summary": {
            "soma_entropy_rank": soma_summary["entropy_effective_rank"],
            "dendritic_receiver_entropy_rank": dend_eranks,
            "dendritic_entropy_rank": distribution_summary(dend_eranks),
            "random_1d_entropy_rank": distribution_summary(random_1d_erank),
            "random_1d_pairwise_cosine_median": distribution_summary(random_1d_pair),
            "random_1d_nearest_cosine_median": distribution_summary(random_1d_nn),
            "soma_entropy_rank_percentile_random_1d": percentile_leq(
                soma_summary["entropy_effective_rank"], random_1d_erank
            ),
            "soma_pairwise_median_percentile_random_1d": percentile_leq(
                soma_summary["pairwise_cosine_median"], random_1d_pair
            ),
            "soma_nearest_median_percentile_random_1d": percentile_leq(
                soma_summary["nearest_cosine_median"], random_1d_nn
            ),
            "fraction_dendritic_receivers_erank_above_soma": float(
                np.mean(np.asarray(dend_eranks) > soma_summary["entropy_effective_rank"])
            ),
        },
        "dimension_curve": dimension_curve,
        "k6_orthonormal_invariance": {
            "max_entropy_rank_abs_error": max_k6_invariance_error,
            "guard_lt_1e-8": invariance_guard,
        },
    }

    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")

    compact = {
        "soma_erank": soma_summary["entropy_effective_rank"],
        "dend_erank_min": min(dend_eranks),
        "dend_erank_median": float(np.median(dend_eranks)),
        "dend_erank_max": max(dend_eranks),
        "fraction_dend_erank_above_soma": result["equal_dimensional_summary"][
            "fraction_dendritic_receivers_erank_above_soma"
        ],
        "random1d_erank_q05": result["equal_dimensional_summary"][
            "random_1d_entropy_rank"
        ]["q05"],
        "random1d_erank_median": result["equal_dimensional_summary"][
            "random_1d_entropy_rank"
        ]["median"],
        "random1d_erank_q95": result["equal_dimensional_summary"][
            "random_1d_entropy_rank"
        ]["q95"],
        "soma_erank_percentile_random1d": result["equal_dimensional_summary"][
            "soma_entropy_rank_percentile_random_1d"
        ],
        "full6_erank": full_summary["entropy_effective_rank"],
        "k6_invariance_max_error": max_k6_invariance_error,
        "k6_invariance_guard": invariance_guard,
    }
    print("DIM_CONTROL_RESULT", json.dumps(compact, separators=(",", ":")))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
