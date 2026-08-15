#!/usr/bin/env python3
"""Receiver-collapse baseline on the author-released FCI Hay cell1.

This is a measurement, not a training experiment and not a novelty claim.

Question
--------
For the same fixed morphology and the same tiny source perturbations, how much
of the location-specific transfer dictionary remains distinguishable when the
observer is only the soma, versus when a small distributed receiver set is
available?

The script uses the exact FCI rat Hay wrapper already documented in
EXACT_L5_BRIDGE.md.  It selects a fixed spread of basal/apical source sites by
path-distance order, injects the same subthreshold current pulse at each site,
and records either:

    R1 = soma only
    Rmulti = soma + 2 basal + 3 apical receiver locations

No parameter is fitted to FCI, task accuracy, or a desired result.

Output diagnostics are intentionally threshold-free:
- entropy effective rank of the normalized source-signature matrix
- participation rank
- pairwise cosine-distance distribution
- nearest-neighbour cosine distances

A larger multi-receiver rank is not 'more intrinsic neuron complexity'.  It
only means the soma projection collapses distinctions that are visible at the
chosen additional ports.
"""

from __future__ import annotations

import argparse
import importlib
import json
import math
import sys
from pathlib import Path

import numpy as np


MODEL_MODULE = (
    "simulating_neurons.neuron_models.rat.hay."
    "Rat_L5b_PC_2_Hay_passive_dends_simple_soma.get_standard_model"
)


def canonical_sec_name(sec) -> str:
    return str(sec.name()).split(".")[-1]


def import_model(fci_root: Path):
    root = fci_root.resolve()
    if not root.exists():
        raise FileNotFoundError(root)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    module = importlib.import_module(MODEL_MODULE)
    from neuron import h
    return h, module


def unique_dendritic_segments(syn_df):
    seen = {}
    for seg in syn_df["segments"]:
        name = canonical_sec_name(seg.sec)
        if "soma" in name or "axon" in name:
            continue
        key = (name, round(float(seg.x), 8))
        seen[key] = seg
    return list(seen.values())


def set_distance_origin(h, cell):
    # NEURON's distance() uses this call form to set the path-distance origin.
    h.distance(0.0, 0.5, sec=cell.soma[0])


def path_distance_um(h, seg) -> float:
    return float(h.distance(float(seg.x), sec=seg.sec))


def kind(seg) -> str:
    name = canonical_sec_name(seg.sec).lower()
    if "apic" in name:
        return "apical"
    if "dend" in name:
        return "basal"
    return "other"


def pick_evenly(items, n):
    if not items:
        return []
    n = min(int(n), len(items))
    idx = np.linspace(0, len(items) - 1, n).round().astype(int)
    out = []
    used = set()
    for i in idx:
        i = int(i)
        if i not in used:
            out.append(items[i])
            used.add(i)
    return out


def pick_quantiles(items, qs):
    if not items:
        return []
    out = []
    used = set()
    for q in qs:
        i = int(round(float(q) * (len(items) - 1)))
        if i not in used:
            out.append(items[i])
            used.add(i)
    return out


def describe_seg(h, seg):
    return {
        "section": canonical_sec_name(seg.sec),
        "x": float(seg.x),
        "path_um": path_distance_um(h, seg),
        "kind": kind(seg),
    }


def run_impulse(h, cell, source, receivers, *, amp_nA, delay_ms, dur_ms, tstop_ms, v_init_mv):
    stim = h.IClamp(float(source.x), sec=source.sec)
    stim.delay = float(delay_ms)
    stim.dur = float(dur_ms)
    stim.amp = float(amp_nA)

    tvec = h.Vector().record(h._ref_t)
    rvecs = [h.Vector().record(r._ref_v) for r in receivers]

    h.finitialize(float(v_init_mv))
    h.continuerun(float(tstop_ms))

    tt = np.asarray(tvec, dtype=np.float64)
    vv = np.vstack([np.asarray(v, dtype=np.float64) for v in rvecs])

    pre = tt < delay_ms
    if not np.any(pre):
        raise RuntimeError("No pre-stimulus samples")
    base = np.median(vv[:, pre], axis=1, keepdims=True)
    dv = vv - base

    post = (tt >= delay_ms) & (tt <= tstop_ms)
    return tt[post] - delay_ms, dv[:, post]


def row_normalize(X, eps=1e-15):
    n = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.maximum(n, eps)


def effective_rank(X, eps=1e-15):
    s = np.linalg.svd(X, compute_uv=False)
    if not np.any(s > eps):
        return 0.0, 0.0, s
    p = s / np.maximum(s.sum(), eps)
    p = p[p > eps]
    erank = float(np.exp(-np.sum(p * np.log(p))))
    s2 = s * s
    prank = float((s2.sum() ** 2) / np.maximum(np.sum(s2 * s2), eps))
    return erank, prank, s


def cosine_distance_stats(Xn):
    sim = np.clip(Xn @ Xn.T, -1.0, 1.0)
    D = 1.0 - sim
    n = D.shape[0]
    tri = D[np.triu_indices(n, 1)]
    masked = D + np.eye(n) * 1e9
    nn = masked.min(axis=1)
    return {
        "pairwise_cosine_median": float(np.median(tri)),
        "pairwise_cosine_q10": float(np.quantile(tri, 0.10)),
        "pairwise_cosine_q90": float(np.quantile(tri, 0.90)),
        "nearest_cosine_mean": float(np.mean(nn)),
        "nearest_cosine_min": float(np.min(nn)),
        "nearest_cosine_median": float(np.median(nn)),
    }


def signature_summary(X):
    Xn = row_normalize(X)
    erank, prank, s = effective_rank(Xn)
    out = {
        "n_sources": int(X.shape[0]),
        "feature_dim": int(X.shape[1]),
        "entropy_effective_rank": erank,
        "participation_rank": prank,
        "singular_values": [float(v) for v in s],
    }
    out.update(cosine_distance_stats(Xn))
    return out


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
    p.add_argument("--output", type=Path, default=Path("receiver_collapse_cell1_result.json"))
    args = p.parse_args()

    h, module = import_model(args.fci_root)
    cell, syn_df = module.create_cell()
    h.cvode_active(0)
    h.dt = float(args.dt_ms)
    h.steps_per_ms = max(1.0, 1.0 / float(args.dt_ms))
    h.tstop = float(args.tstop_ms)

    set_distance_origin(h, cell)
    segs = unique_dendritic_segments(syn_df)
    basal = sorted([s for s in segs if kind(s) == "basal"], key=lambda s: path_distance_um(h, s))
    apical = sorted([s for s in segs if kind(s) == "apical"], key=lambda s: path_distance_um(h, s))
    if len(basal) < 2 or len(apical) < 3:
        raise RuntimeError(f"Insufficient dendritic classes: basal={len(basal)} apical={len(apical)}")

    sources = pick_evenly(basal, args.sources_per_tree) + pick_evenly(apical, args.sources_per_tree)

    # Receivers are selected independently from the source list by fixed
    # path-order quantiles.  The soma is always receiver 0.
    receiver_segs = [cell.soma[0](0.5)]
    receiver_segs += pick_quantiles(basal, [0.25, 0.75])
    receiver_segs += pick_quantiles(apical, [0.20, 0.55, 0.90])

    traces = []
    source_peaks_soma = []
    max_abs = []
    time_axis = None
    for k, src in enumerate(sources):
        tt, dv = run_impulse(
            h, cell, src, receiver_segs,
            amp_nA=args.amp_na,
            delay_ms=args.delay_ms,
            dur_ms=args.dur_ms,
            tstop_ms=args.tstop_ms,
            v_init_mv=args.v_init_mv,
        )
        if time_axis is None:
            time_axis = tt
        traces.append(dv)
        source_peaks_soma.append(float(np.max(np.abs(dv[0]))))
        max_abs.append(float(np.max(np.abs(dv))))
        print(
            f"source {k+1:02d}/{len(sources)} "
            f"{canonical_sec_name(src.sec)}({float(src.x):.4f}) "
            f"path={path_distance_um(h, src):.1f} um "
            f"peak_soma={source_peaks_soma[-1]:.6g} mV"
        )

    # traces: [source, receiver, time]
    A = np.stack(traces, axis=0)
    soma_matrix = A[:, 0, :]
    multi_matrix = A.reshape(A.shape[0], -1)

    result = {
        "model": "FCI rat Hay Rat_L5b_PC_2_Hay_passive_dends_simple_soma / cell1.asc",
        "intervention": {
            "amp_nA": args.amp_na,
            "delay_ms": args.delay_ms,
            "dur_ms": args.dur_ms,
            "tstop_ms": args.tstop_ms,
            "v_init_mV": args.v_init_mv,
            "dt_ms": args.dt_ms,
        },
        "source_sites": [describe_seg(h, s) for s in sources],
        "receiver_sites": [describe_seg(h, r) if canonical_sec_name(r.sec) != canonical_sec_name(cell.soma[0]) else {
            "section": canonical_sec_name(r.sec), "x": float(r.x), "path_um": 0.0, "kind": "soma"
        } for r in receiver_segs],
        "soma_only": signature_summary(soma_matrix),
        "multi_receiver": signature_summary(multi_matrix),
        "soma_peak_mV": source_peaks_soma,
        "max_any_receiver_delta_mV": max_abs,
        "max_soma_peak_mV": float(max(source_peaks_soma)),
        "all_subthreshold_guard": bool(max(source_peaks_soma) < 10.0),
    }
    result["receiver_rank_ratio_entropy"] = float(
        result["multi_receiver"]["entropy_effective_rank"] /
        max(result["soma_only"]["entropy_effective_rank"], 1e-15)
    )
    result["receiver_rank_ratio_participation"] = float(
        result["multi_receiver"]["participation_rank"] /
        max(result["soma_only"]["participation_rank"], 1e-15)
    )

    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    compact = {
        "n_sources": len(sources),
        "n_receivers": len(receiver_segs),
        "soma_erank": result["soma_only"]["entropy_effective_rank"],
        "multi_erank": result["multi_receiver"]["entropy_effective_rank"],
        "erank_ratio": result["receiver_rank_ratio_entropy"],
        "soma_prank": result["soma_only"]["participation_rank"],
        "multi_prank": result["multi_receiver"]["participation_rank"],
        "soma_pairwise_cos_median": result["soma_only"]["pairwise_cosine_median"],
        "multi_pairwise_cos_median": result["multi_receiver"]["pairwise_cosine_median"],
        "soma_nn_cos_median": result["soma_only"]["nearest_cosine_median"],
        "multi_nn_cos_median": result["multi_receiver"]["nearest_cosine_median"],
        "max_soma_peak_mV": result["max_soma_peak_mV"],
        "subthreshold_guard": result["all_subthreshold_guard"],
    }
    print("RC_RESULT", json.dumps(compact, separators=(",", ":")))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
