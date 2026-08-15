#!/usr/bin/env python3
"""Q2: same morphology + same mechanisms, different operating state.

Executes OPERATING_STATE_Q2_GATE.md on the Beniaguev/Segev/London public
Hay L5PC model.  The full active cell is unchanged between conditions.  A
persistent somatic DC IClamp is calibrated by deterministic bisection to place
the mean somatic voltage near either -85 mV or -65 mV after 200 ms of settling.
The same tiny source perturbations and frozen Q0/Q1 receiver set are then
measured against matched no-source controls.

The intervention calibration sees only somatic voltage, never source-signature
geometry.  This is a controlled measurement of known voltage-dependent
transfer physics in the project's receiver-relative coordinate system, not a
novelty claim.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
from scipy.stats import pearsonr, spearmanr


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

TARGETS_MV = {
    "hyper": -85.0,
    "depol": -65.0,
}


def setup_neuron(model_root: Path):
    sim_dir = (model_root / "L5PC_NEURON_simulation").resolve()
    if not sim_dir.exists():
        raise FileNotFoundError(sim_dir)

    import neuron
    from neuron import h

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


def instantiate_cell(h, sim_dir: Path):
    old_cwd = Path.cwd()
    os.chdir(sim_dir)
    try:
        cell = h.L5PCtemplate("morphologies/cell1.asc")
    finally:
        os.chdir(old_cwd)
    return cell


def get_section(cell, family: str, index: int):
    return getattr(cell, family)[int(index)]


def site_segment(cell, spec):
    family, index, x = spec
    return get_section(cell, family, index)(float(x))


def site_desc(spec):
    family, index, x = spec
    return {
        "family": family,
        "index": int(index),
        "x": float(x),
        "name": f"{family}[{index}]",
    }


def configure_integrator(h, dt_ms: float, tstop_ms: float):
    h.cvode_active(0)
    h.dt = float(dt_ms)
    h.steps_per_ms = max(1.0, 1.0 / float(dt_ms))
    h.tstop = float(tstop_ms)


def run_trajectory(
    h,
    soma_seg,
    receivers,
    *,
    hold_amp_nA,
    tstop_ms,
    v_init_mv,
    source=None,
    source_amp_nA=0.0,
    source_delay_ms=220.0,
    source_dur_ms=0.5,
):
    """Identically initialized trial with persistent soma hold and optional source."""
    hold = h.IClamp(float(soma_seg.x), sec=soma_seg.sec)
    hold.delay = 0.0
    hold.dur = float(tstop_ms + 1.0)
    hold.amp = float(hold_amp_nA)

    source_stim = None
    try:
        if source is not None:
            source_stim = h.IClamp(float(source.x), sec=source.sec)
            source_stim.delay = float(source_delay_ms)
            source_stim.dur = float(source_dur_ms)
            source_stim.amp = float(source_amp_nA)

        tvec = h.Vector().record(h._ref_t)
        rvecs = [h.Vector().record(r._ref_v) for r in receivers]

        h.finitialize(float(v_init_mv))
        h.continuerun(float(tstop_ms))

        tt = np.asarray(tvec, dtype=np.float64).copy()
        vv = np.vstack([np.asarray(v, dtype=np.float64).copy() for v in rvecs])
        return tt, vv
    finally:
        hold.amp = 0.0
        hold.dur = 0.0
        if source_stim is not None:
            source_stim.amp = 0.0
            source_stim.dur = 0.0


def soma_voltage_for_hold(
    h,
    soma_seg,
    *,
    amp_nA,
    settle_ms,
    v_init_mv,
    dt_ms,
    calibration_window_ms,
):
    configure_integrator(h, dt_ms, settle_ms)
    tt, vv = run_trajectory(
        h,
        soma_seg,
        [soma_seg],
        hold_amp_nA=amp_nA,
        tstop_ms=settle_ms,
        v_init_mv=v_init_mv,
    )
    mask = tt >= float(settle_ms - calibration_window_ms)
    mean_v = float(np.mean(vv[0, mask]))
    max_v = float(np.max(vv[0, mask]))
    min_v = float(np.min(vv[0, mask]))
    return mean_v, min_v, max_v


def calibrate_hold_current(
    h,
    soma_seg,
    *,
    target_mv,
    lo_nA,
    hi_nA,
    tolerance_mv,
    max_iter,
    settle_ms,
    calibration_window_ms,
    v_init_mv,
    dt_ms,
):
    vlo, _, _ = soma_voltage_for_hold(
        h, soma_seg, amp_nA=lo_nA, settle_ms=settle_ms,
        v_init_mv=v_init_mv, dt_ms=dt_ms,
        calibration_window_ms=calibration_window_ms,
    )
    vhi, _, _ = soma_voltage_for_hold(
        h, soma_seg, amp_nA=hi_nA, settle_ms=settle_ms,
        v_init_mv=v_init_mv, dt_ms=dt_ms,
        calibration_window_ms=calibration_window_ms,
    )
    print(
        f"calibration target={target_mv:.3f} mV bracket "
        f"{lo_nA:.4f} nA -> {vlo:.3f} mV, {hi_nA:.4f} nA -> {vhi:.3f} mV"
    )

    if not (vlo <= target_mv <= vhi):
        raise RuntimeError(
            f"Target {target_mv} mV not bracketed by frozen current range: "
            f"V({lo_nA})={vlo}, V({hi_nA})={vhi}"
        )

    lo = float(lo_nA)
    hi = float(hi_nA)
    best = None
    history = []

    for iteration in range(1, int(max_iter) + 1):
        mid = 0.5 * (lo + hi)
        vm, vmin, vmax = soma_voltage_for_hold(
            h, soma_seg, amp_nA=mid, settle_ms=settle_ms,
            v_init_mv=v_init_mv, dt_ms=dt_ms,
            calibration_window_ms=calibration_window_ms,
        )
        err = vm - target_mv
        record = {
            "iteration": iteration,
            "amp_nA": mid,
            "mean_soma_mV": vm,
            "min_soma_mV": vmin,
            "max_soma_mV": vmax,
            "error_mV": err,
        }
        history.append(record)
        if best is None or abs(err) < abs(best["error_mV"]):
            best = record
        print(
            f"calibration iter={iteration:02d} target={target_mv:.1f} "
            f"amp={mid:.8f} nA mean={vm:.5f} mV err={err:+.5f}"
        )

        if abs(err) <= tolerance_mv:
            break
        if vm < target_mv:
            lo = mid
        else:
            hi = mid

    if best is None or abs(best["error_mV"]) > tolerance_mv:
        raise RuntimeError(
            f"Calibration failed target={target_mv}: best={best}, tolerance={tolerance_mv}"
        )
    return best, history, {"lo_nA": lo_nA, "hi_nA": hi_nA, "vlo_mV": vlo, "vhi_mV": vhi}


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
    erank = float(np.exp(-np.sum(p * np.log(p)))) if len(p) else 0.0
    s2 = s * s
    prank = float((s2.sum() ** 2) / np.maximum(np.sum(s2 * s2), eps))
    return erank, prank, s


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


def compare_distance_matrices(A, B):
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    iu = np.triu_indices(A.shape[0], 1)
    a = A[iu]
    b = B[iu]
    diff = a - b

    pearson = float(pearsonr(a, b).statistic)
    spearman = float(spearmanr(a, b).statistic)

    Am = A + np.eye(A.shape[0]) * 1e9
    Bm = B + np.eye(B.shape[0]) * 1e9
    nn_a = Am.argmin(axis=1)
    nn_b = Bm.argmin(axis=1)
    changed = nn_a != nn_b

    return {
        "pearson_pairwise_distance": pearson,
        "spearman_pairwise_distance": spearman,
        "relative_frobenius_distance": float(
            np.linalg.norm(A - B) / max(np.linalg.norm(B), 1e-15)
        ),
        "median_absolute_pairwise_change": float(np.median(np.abs(diff))),
        "q90_absolute_pairwise_change": float(np.quantile(np.abs(diff), 0.90)),
        "max_absolute_pairwise_change": float(np.max(np.abs(diff))),
        "nearest_neighbor_changes": int(np.sum(changed)),
        "nearest_neighbor_change_fraction": float(np.mean(changed)),
        "state_a_nearest_neighbor": [int(v) for v in nn_a],
        "state_b_nearest_neighbor": [int(v) for v in nn_b],
    }


def run_state(h, sim_dir: Path, *, label: str, target_mv: float, args):
    cell = instantiate_cell(h, sim_dir)
    configure_integrator(h, args.dt_ms, args.tstop_ms)

    soma_seg = cell.soma[0](0.5)
    sources = [site_segment(cell, s) for s in SOURCES]
    receivers = [site_segment(cell, r) for r in RECEIVERS]

    best, calibration_history, bracket = calibrate_hold_current(
        h,
        soma_seg,
        target_mv=target_mv,
        lo_nA=args.hold_lo_na,
        hi_nA=args.hold_hi_na,
        tolerance_mv=args.hold_tolerance_mv,
        max_iter=args.hold_max_iter,
        settle_ms=args.settle_ms,
        calibration_window_ms=args.calibration_window_ms,
        v_init_mv=args.v_init_mv,
        dt_ms=args.dt_ms,
    )
    hold_amp = float(best["amp_nA"])
    configure_integrator(h, args.dt_ms, args.tstop_ms)

    control_t, control_v = run_trajectory(
        h,
        soma_seg,
        receivers,
        hold_amp_nA=hold_amp,
        tstop_ms=args.tstop_ms,
        v_init_mv=args.v_init_mv,
        source=None,
        source_delay_ms=args.source_delay_ms,
        source_dur_ms=args.source_dur_ms,
    )

    baseline_mask = (
        (control_t >= args.settle_ms)
        & (control_t < args.source_delay_ms)
    )
    if not np.any(baseline_mask):
        raise RuntimeError("No baseline samples between settle and source delay")
    baseline_receiver_mean = np.mean(control_v[:, baseline_mask], axis=1)
    baseline_receiver_std = np.std(control_v[:, baseline_mask], axis=1)
    achieved_soma = float(baseline_receiver_mean[0])

    post = control_t >= args.source_delay_ms
    traces = []
    source_soma_delta = []
    source_max_delta = []
    source_max_soma_v = []
    source_max_any_v = []

    for k, src in enumerate(sources):
        tt, vv = run_trajectory(
            h,
            soma_seg,
            receivers,
            hold_amp_nA=hold_amp,
            tstop_ms=args.tstop_ms,
            v_init_mv=args.v_init_mv,
            source=src,
            source_amp_nA=args.source_amp_na,
            source_delay_ms=args.source_delay_ms,
            source_dur_ms=args.source_dur_ms,
        )
        if tt.shape != control_t.shape or not np.allclose(tt, control_t, atol=1e-12, rtol=0.0):
            raise RuntimeError("Stimulus/control time grids differ")
        dv = (vv - control_v)[:, post]
        traces.append(dv)
        source_soma_delta.append(float(np.max(np.abs(dv[0]))))
        source_max_delta.append(float(np.max(np.abs(dv))))
        source_max_soma_v.append(float(np.max(vv[0, post])))
        source_max_any_v.append(float(np.max(vv[:, post])))
        fam, idx, x = SOURCES[k]
        print(
            f"{label} source {k+1:02d}/{len(sources)} {fam}[{idx}]({x:.4f}) "
            f"soma_delta={source_soma_delta[-1]:.9g} mV "
            f"max_any_delta={source_max_delta[-1]:.9g} mV"
        )

    A = np.stack(traces, axis=0)
    soma_X = A[:, 0, :]
    multi_X = A.reshape(A.shape[0], -1)

    max_control_soma_v = float(np.max(control_v[0]))
    max_control_any_v = float(np.max(control_v))
    max_trial_soma_v = float(max(source_max_soma_v))
    max_trial_any_v = float(max(source_max_any_v))
    max_delta = float(max(source_max_delta))

    return {
        "label": label,
        "target_soma_mV": target_mv,
        "hold_current_nA": hold_amp,
        "calibration_best": best,
        "calibration_bracket": bracket,
        "calibration_history": calibration_history,
        "achieved_soma_baseline_mV": achieved_soma,
        "baseline_receiver_mean_mV": [float(v) for v in baseline_receiver_mean],
        "baseline_receiver_std_mV": [float(v) for v in baseline_receiver_std],
        "soma_only": signature_summary(soma_X),
        "multi_receiver": signature_summary(multi_X),
        "source_soma_delta_mV": source_soma_delta,
        "source_max_any_delta_mV": source_max_delta,
        "max_control_soma_voltage_mV": max_control_soma_v,
        "max_control_any_receiver_voltage_mV": max_control_any_v,
        "max_trial_soma_voltage_mV": max_trial_soma_v,
        "max_trial_any_receiver_voltage_mV": max_trial_any_v,
        "max_perturbation_delta_mV": max_delta,
        "soma_spike_guard": bool(max(max_control_soma_v, max_trial_soma_v) < -20.0),
        "large_event_guard": bool(max_delta < 20.0),
        "target_tolerance_guard": bool(abs(achieved_soma - target_mv) <= args.hold_tolerance_mv),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model-root", type=Path, required=True)
    p.add_argument("--source-amp-na", type=float, default=0.02)
    p.add_argument("--source-dur-ms", type=float, default=0.5)
    p.add_argument("--source-delay-ms", type=float, default=220.0)
    p.add_argument("--settle-ms", type=float, default=200.0)
    p.add_argument("--calibration-window-ms", type=float, default=20.0)
    p.add_argument("--tstop-ms", type=float, default=360.0)
    p.add_argument("--dt-ms", type=float, default=0.025)
    p.add_argument("--v-init-mv", type=float, default=-76.0)
    p.add_argument("--hold-lo-na", type=float, default=-2.0)
    p.add_argument("--hold-hi-na", type=float, default=2.0)
    p.add_argument("--hold-tolerance-mv", type=float, default=0.2)
    p.add_argument("--hold-max-iter", type=int, default=24)
    p.add_argument("--output", type=Path, default=Path("receiver_operating_state_cell1_result.json"))
    args = p.parse_args()

    h, sim_dir = setup_neuron(args.model_root)

    hyper = run_state(h, sim_dir, label="hyper", target_mv=TARGETS_MV["hyper"], args=args)
    depol = run_state(h, sim_dir, label="depol", target_mv=TARGETS_MV["depol"], args=args)

    soma_cmp = compare_distance_matrices(
        depol["soma_only"]["distance_matrix"],
        hyper["soma_only"]["distance_matrix"],
    )
    multi_cmp = compare_distance_matrices(
        depol["multi_receiver"]["distance_matrix"],
        hyper["multi_receiver"]["distance_matrix"],
    )

    result = {
        "model": {
            "repository": "SelfishGene/neuron_as_deep_net",
            "commit": "074c4666300a8ad246601dab179a97a6942f0f29",
            "morphology": "L5PC_NEURON_simulation/morphologies/cell1.asc",
            "biophysics": "released full active L5PCbiophys5b.hoc + L5PCtemplate_2.hoc",
        },
        "probe": {
            "source_amp_nA": args.source_amp_na,
            "source_dur_ms": args.source_dur_ms,
            "source_delay_ms": args.source_delay_ms,
            "settle_ms": args.settle_ms,
            "calibration_window_ms": args.calibration_window_ms,
            "tstop_ms": args.tstop_ms,
            "dt_ms": args.dt_ms,
            "v_init_mV": args.v_init_mv,
            "hold_current_bracket_nA": [args.hold_lo_na, args.hold_hi_na],
            "hold_tolerance_mV": args.hold_tolerance_mv,
            "baseline_subtraction": "matched hold-only trajectory per operating state",
        },
        "sources": [site_desc(x) for x in SOURCES],
        "receivers": [site_desc(x) for x in RECEIVERS],
        "hyper": hyper,
        "depol": depol,
        "comparison_depol_vs_hyper": {
            "soma_only": soma_cmp,
            "multi_receiver": multi_cmp,
            "entropy_rank_ratio_depol_over_hyper_soma": float(
                depol["soma_only"]["entropy_effective_rank"]
                / max(hyper["soma_only"]["entropy_effective_rank"], 1e-15)
            ),
            "entropy_rank_ratio_depol_over_hyper_multi": float(
                depol["multi_receiver"]["entropy_effective_rank"]
                / max(hyper["multi_receiver"]["entropy_effective_rank"], 1e-15)
            ),
        },
    }

    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")

    compact = {
        "hyper_hold_nA": hyper["hold_current_nA"],
        "hyper_achieved_mV": hyper["achieved_soma_baseline_mV"],
        "depol_hold_nA": depol["hold_current_nA"],
        "depol_achieved_mV": depol["achieved_soma_baseline_mV"],
        "hyper_soma_erank": hyper["soma_only"]["entropy_effective_rank"],
        "depol_soma_erank": depol["soma_only"]["entropy_effective_rank"],
        "hyper_multi_erank": hyper["multi_receiver"]["entropy_effective_rank"],
        "depol_multi_erank": depol["multi_receiver"]["entropy_effective_rank"],
        "multi_distance_pearson": multi_cmp["pearson_pairwise_distance"],
        "multi_distance_spearman": multi_cmp["spearman_pairwise_distance"],
        "multi_relative_frob": multi_cmp["relative_frobenius_distance"],
        "multi_median_abs_change": multi_cmp["median_absolute_pairwise_change"],
        "multi_q90_abs_change": multi_cmp["q90_absolute_pairwise_change"],
        "multi_nn_changes": multi_cmp["nearest_neighbor_changes"],
        "soma_distance_pearson": soma_cmp["pearson_pairwise_distance"],
        "soma_relative_frob": soma_cmp["relative_frobenius_distance"],
        "soma_nn_changes": soma_cmp["nearest_neighbor_changes"],
        "hyper_guards": bool(
            hyper["soma_spike_guard"] and hyper["large_event_guard"] and hyper["target_tolerance_guard"]
        ),
        "depol_guards": bool(
            depol["soma_spike_guard"] and depol["large_event_guard"] and depol["target_tolerance_guard"]
        ),
    }
    print("Q2_RESULT", json.dumps(compact, separators=(",", ":")))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
