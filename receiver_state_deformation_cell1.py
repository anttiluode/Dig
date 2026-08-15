#!/usr/bin/env python3
"""Q1: state/operator deformation on byte-identical Hay cell1.asc.

This script executes the preregistered STATE_DEFORMATION_Q1_GATE.md.
It instantiates the Beniaguev/Segev/London 2021 released Hay L5PC model and
compares two conditions on the same morphology and frozen source/receiver
coordinates:

  ACTIVE             released dendritic conductances unchanged
  DENDRITE_ABLATED   maximal active dendritic conductances explicitly zeroed

Soma/axon mechanisms, passive dendritic parameters, anatomy, sources,
receivers, stimulus, integration, and response metrics are held fixed.

The primary object is the normalized source-to-receiver response geometry,
not raw voltage gain.  Every source trial is differenced against a matched
no-stimulus trajectory within the same condition.

This is a controlled measurement, not a novelty claim and not an attempt to
reproduce an author's named passive-dendrite dataset condition.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
from scipy.stats import pearsonr, spearmanr


# Frozen from Dig Q0.  Do not reselect from the active model.
SOURCES = [
    ("dend", 7, 0.16666666666666666),
    ("dend", 12, 0.5),
    ("dend", 82, 0.22727272727272727),
    ("dend", 49, 0.5),
    ("dend", 62, 0.05555555555555555),
    ("dend", 38, 0.9),
    ("dend", 67, 0.9444444444444444),
    ("dend", 70, 0.9666666666666667),
    ("apic", 0, 0.16666666666666666),
    ("apic", 13, 0.11538461538461539),
    ("apic", 10, 0.9285714285714286),
    ("apic", 18, 0.8333333333333334),
    ("apic", 60, 0.2894736842105263),
    ("apic", 68, 0.8333333333333334),
    ("apic", 67, 0.3),
    ("apic", 63, 0.9615384615384616),
]

RECEIVERS = [
    ("soma", 0, 0.5),
    ("dend", 54, 0.16666666666666666),
    ("dend", 67, 0.7222222222222222),
    ("apic", 14, 0.9),
    ("apic", 37, 0.2826086956521739),
    ("apic", 71, 0.5),
]

APICAL_ACTIVE_GBARS = [
    "gSK_E2bar_SK_E2",
    "gCa_LVAstbar_Ca_LVAst",
    "gCa_HVAbar_Ca_HVA",
    "gSKv3_1bar_SKv3_1",
    "gNaTs2_tbar_NaTs2_t",
    "gImbar_Im",
    "gIhbar_Ih",
]

BASAL_ACTIVE_GBARS = ["gIhbar_Ih"]


def setup_neuron(model_root: Path):
    sim_dir = (model_root / "L5PC_NEURON_simulation").resolve()
    if not sim_dir.exists():
        raise FileNotFoundError(sim_dir)

    # Import after cwd is known because the historical HOC files use relative
    # morphology paths.
    import neuron
    from neuron import h

    # Load mechanisms compiled by nrnivmodl in the released simulation folder.
    loaded = neuron.load_mechanisms(str(sim_dir))
    print(f"load_mechanisms={loaded} sim_dir={sim_dir}")

    old_cwd = Path.cwd()
    os.chdir(sim_dir)
    try:
        h.load_file("stdrun.hoc")
        h.load_file("import3d.hoc")
        h.load_file("L5PCbiophys5b.hoc")
        h.load_file("L5PCtemplate_2.hoc")
    finally:
        os.chdir(old_cwd)
    return h, sim_dir


def get_section(cell, family: str, index: int):
    arr = getattr(cell, family)
    return arr[int(index)]


def site_segment(cell, spec):
    family, index, x = spec
    return get_section(cell, family, index)(float(x))


def site_desc(spec):
    family, index, x = spec
    return {"family": family, "index": int(index), "x": float(x), "name": f"{family}[{index}]"}


def zero_segment_attr_if_present(seg, attr: str):
    try:
        getattr(seg, attr)
    except Exception:
        return False
    setattr(seg, attr, 0.0)
    return True


def ablate_dendritic_active_conductances(cell):
    changed = {name: 0 for name in APICAL_ACTIVE_GBARS + BASAL_ACTIVE_GBARS}

    for sec in cell.apical:
        for seg in sec:
            for attr in APICAL_ACTIVE_GBARS:
                if zero_segment_attr_if_present(seg, attr):
                    changed[attr] += 1

    for sec in cell.basal:
        for seg in sec:
            for attr in BASAL_ACTIVE_GBARS:
                if zero_segment_attr_if_present(seg, attr):
                    changed[attr] += 1

    missing = [name for name, count in changed.items() if count == 0]
    if missing:
        raise RuntimeError(f"Ablation attributes not found: {missing}; counts={changed}")
    return changed


def configure_integrator(h, dt_ms: float, tstop_ms: float):
    h.cvode_active(0)
    h.dt = float(dt_ms)
    h.steps_per_ms = max(1.0, 1.0 / float(dt_ms))
    h.tstop = float(tstop_ms)


def run_voltage_trajectory(
    h,
    receivers,
    *,
    source=None,
    amp_nA=0.0,
    delay_ms,
    dur_ms,
    tstop_ms,
    v_init_mv,
):
    stim = None
    try:
        if source is not None:
            stim = h.IClamp(float(source.x), sec=source.sec)
            stim.delay = float(delay_ms)
            stim.dur = float(dur_ms)
            stim.amp = float(amp_nA)

        tvec = h.Vector().record(h._ref_t)
        rvecs = [h.Vector().record(r._ref_v) for r in receivers]

        h.finitialize(float(v_init_mv))
        h.continuerun(float(tstop_ms))

        tt = np.asarray(tvec, dtype=np.float64).copy()
        vv = np.vstack([np.asarray(v, dtype=np.float64).copy() for v in rvecs])
        return tt, vv
    finally:
        if stim is not None:
            stim.amp = 0.0
            stim.dur = 0.0


def row_normalize(X, eps=1e-15):
    n = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.maximum(n, eps)


def cosine_distance_matrix(X):
    Xn = row_normalize(X)
    sim = np.clip(Xn @ Xn.T, -1.0, 1.0)
    D = 1.0 - sim
    np.fill_diagonal(D, 0.0)
    return D


def effective_rank(X, eps=1e-15):
    Xn = row_normalize(X)
    s = np.linalg.svd(Xn, compute_uv=False)
    p = s / np.maximum(s.sum(), eps)
    p = p[p > eps]
    entropy_rank = float(np.exp(-np.sum(p * np.log(p)))) if len(p) else 0.0
    s2 = s * s
    participation_rank = float((s2.sum() ** 2) / np.maximum(np.sum(s2 * s2), eps))
    return entropy_rank, participation_rank, s


def signature_summary(X):
    erank, prank, s = effective_rank(X)
    D = cosine_distance_matrix(X)
    tri = D[np.triu_indices(D.shape[0], 1)]
    masked = D + np.eye(D.shape[0]) * 1e9
    nn = masked.argmin(axis=1)
    return {
        "entropy_effective_rank": erank,
        "participation_rank": prank,
        "singular_values": [float(v) for v in s],
        "pairwise_cosine_median": float(np.median(tri)),
        "pairwise_cosine_q10": float(np.quantile(tri, 0.10)),
        "pairwise_cosine_q90": float(np.quantile(tri, 0.90)),
        "nearest_neighbor_source_index": [int(v) for v in nn],
        "distance_matrix": D.tolist(),
    }


def run_condition(h, sim_dir, *, condition: str, args):
    # L5PCtemplate.init() calls forall delete_section(), so each condition is a
    # fresh cell and old cell state cannot leak into the next one.
    old_cwd = Path.cwd()
    os.chdir(sim_dir)
    try:
        cell = h.L5PCtemplate("morphologies/cell1.asc")
    finally:
        os.chdir(old_cwd)

    ablation_counts = None
    if condition == "dendrite_ablated":
        ablation_counts = ablate_dendritic_active_conductances(cell)
    elif condition != "active":
        raise ValueError(condition)

    configure_integrator(h, args.dt_ms, args.tstop_ms)
    sources = [site_segment(cell, s) for s in SOURCES]
    receivers = [site_segment(cell, r) for r in RECEIVERS]

    control_t, control_v = run_voltage_trajectory(
        h,
        receivers,
        source=None,
        delay_ms=args.delay_ms,
        dur_ms=args.dur_ms,
        tstop_ms=args.tstop_ms,
        v_init_mv=args.v_init_mv,
    )
    post = control_t >= args.delay_ms

    traces = []
    soma_peaks = []
    max_any_delta = []
    max_abs_soma_voltage = []
    max_abs_receiver_voltage = []

    for k, src in enumerate(sources):
        tt, vv = run_voltage_trajectory(
            h,
            receivers,
            source=src,
            amp_nA=args.amp_na,
            delay_ms=args.delay_ms,
            dur_ms=args.dur_ms,
            tstop_ms=args.tstop_ms,
            v_init_mv=args.v_init_mv,
        )
        if tt.shape != control_t.shape or not np.allclose(tt, control_t, atol=1e-12, rtol=0.0):
            raise RuntimeError("Stimulus/control time grids differ")
        dv = (vv - control_v)[:, post]
        traces.append(dv)
        soma_peaks.append(float(np.max(np.abs(dv[0]))))
        max_any_delta.append(float(np.max(np.abs(dv))))
        max_abs_soma_voltage.append(float(np.max(vv[0, post])))
        max_abs_receiver_voltage.append(float(np.max(vv[:, post])))
        fam, idx, x = SOURCES[k]
        print(
            f"{condition} source {k+1:02d}/{len(sources)} "
            f"{fam}[{idx}]({x:.4f}) soma_delta={soma_peaks[-1]:.9g} mV "
            f"max_any_delta={max_any_delta[-1]:.9g} mV"
        )

    A = np.stack(traces, axis=0)  # source, receiver, time
    soma_X = A[:, 0, :]
    multi_X = A.reshape(A.shape[0], -1)

    return {
        "condition": condition,
        "ablation_counts": ablation_counts,
        "soma_only": signature_summary(soma_X),
        "multi_receiver": signature_summary(multi_X),
        "soma_peak_delta_mV": soma_peaks,
        "max_any_receiver_delta_mV": max_any_delta,
        "max_absolute_soma_voltage_mV": float(max(max_abs_soma_voltage)),
        "max_absolute_recorded_voltage_mV": float(max(max_abs_receiver_voltage)),
        "soma_spike_guard": bool(max(max_abs_soma_voltage) < -20.0),
        "large_local_event_guard": bool(max(max_any_delta) < 20.0),
    }


def rank_correlation(a, b):
    if np.allclose(a, a[0]) or np.allclose(b, b[0]):
        return float("nan")
    return float(spearmanr(a, b).statistic)


def compare_distance_matrices(A, B):
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    iu = np.triu_indices(A.shape[0], 1)
    a = A[iu]
    b = B[iu]
    diff = a - b
    pearson = float(pearsonr(a, b).statistic)
    spearman = rank_correlation(a, b)
    rel_frob = float(np.linalg.norm(A - B) / max(np.linalg.norm(B), 1e-15))

    Am = A + np.eye(A.shape[0]) * 1e9
    Bm = B + np.eye(B.shape[0]) * 1e9
    nn_a = Am.argmin(axis=1)
    nn_b = Bm.argmin(axis=1)
    changed = nn_a != nn_b

    return {
        "pearson_pairwise_distance": pearson,
        "spearman_pairwise_distance": spearman,
        "relative_frobenius_distance": rel_frob,
        "median_absolute_pairwise_change": float(np.median(np.abs(diff))),
        "q90_absolute_pairwise_change": float(np.quantile(np.abs(diff), 0.90)),
        "max_absolute_pairwise_change": float(np.max(np.abs(diff))),
        "nearest_neighbor_changes": int(np.sum(changed)),
        "nearest_neighbor_change_fraction": float(np.mean(changed)),
        "active_nearest_neighbor": [int(v) for v in nn_a],
        "ablated_nearest_neighbor": [int(v) for v in nn_b],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model-root", type=Path, required=True)
    p.add_argument("--amp-na", type=float, default=0.02)
    p.add_argument("--delay-ms", type=float, default=20.0)
    p.add_argument("--dur-ms", type=float, default=0.5)
    p.add_argument("--tstop-ms", type=float, default=160.0)
    p.add_argument("--v-init-mv", type=float, default=-76.0)
    p.add_argument("--dt-ms", type=float, default=0.025)
    p.add_argument("--output", type=Path, default=Path("receiver_state_deformation_cell1_result.json"))
    args = p.parse_args()

    h, sim_dir = setup_neuron(args.model_root)

    active = run_condition(h, sim_dir, condition="active", args=args)
    ablated = run_condition(h, sim_dir, condition="dendrite_ablated", args=args)

    soma_cmp = compare_distance_matrices(
        active["soma_only"]["distance_matrix"],
        ablated["soma_only"]["distance_matrix"],
    )
    multi_cmp = compare_distance_matrices(
        active["multi_receiver"]["distance_matrix"],
        ablated["multi_receiver"]["distance_matrix"],
    )

    result = {
        "model": {
            "repository": "SelfishGene/neuron_as_deep_net",
            "commit": "074c4666300a8ad246601dab179a97a6942f0f29",
            "morphology": "L5PC_NEURON_simulation/morphologies/cell1.asc",
            "biophysics": "L5PCbiophys5b.hoc + L5PCtemplate_2.hoc",
        },
        "probe": {
            "amp_nA": args.amp_na,
            "delay_ms": args.delay_ms,
            "dur_ms": args.dur_ms,
            "tstop_ms": args.tstop_ms,
            "v_init_mV": args.v_init_mv,
            "dt_ms": args.dt_ms,
            "baseline_subtraction": "matched no-stimulus trajectory per condition",
        },
        "sources": [site_desc(x) for x in SOURCES],
        "receivers": [site_desc(x) for x in RECEIVERS],
        "active": active,
        "dendrite_ablated": ablated,
        "comparison": {
            "soma_only": soma_cmp,
            "multi_receiver": multi_cmp,
            "entropy_rank_active_over_ablated_soma": float(
                active["soma_only"]["entropy_effective_rank"]
                / max(ablated["soma_only"]["entropy_effective_rank"], 1e-15)
            ),
            "entropy_rank_active_over_ablated_multi": float(
                active["multi_receiver"]["entropy_effective_rank"]
                / max(ablated["multi_receiver"]["entropy_effective_rank"], 1e-15)
            ),
        },
    }

    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")

    compact = {
        "active_soma_erank": active["soma_only"]["entropy_effective_rank"],
        "ablated_soma_erank": ablated["soma_only"]["entropy_effective_rank"],
        "active_multi_erank": active["multi_receiver"]["entropy_effective_rank"],
        "ablated_multi_erank": ablated["multi_receiver"]["entropy_effective_rank"],
        "multi_distance_pearson": multi_cmp["pearson_pairwise_distance"],
        "multi_distance_spearman": multi_cmp["spearman_pairwise_distance"],
        "multi_relative_frob": multi_cmp["relative_frobenius_distance"],
        "multi_median_abs_change": multi_cmp["median_absolute_pairwise_change"],
        "multi_q90_abs_change": multi_cmp["q90_absolute_pairwise_change"],
        "multi_nn_changes": multi_cmp["nearest_neighbor_changes"],
        "soma_distance_pearson": soma_cmp["pearson_pairwise_distance"],
        "soma_relative_frob": soma_cmp["relative_frobenius_distance"],
        "soma_nn_changes": soma_cmp["nearest_neighbor_changes"],
        "active_max_soma_v": active["max_absolute_soma_voltage_mV"],
        "active_max_delta": max(active["max_any_receiver_delta_mV"]),
        "active_small_signal_guards": bool(active["soma_spike_guard"] and active["large_local_event_guard"]),
        "ablated_small_signal_guards": bool(ablated["soma_spike_guard"] and ablated["large_local_event_guard"]),
    }
    print("Q1_RESULT", json.dumps(compact, separators=(",", ":")))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
