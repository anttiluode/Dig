#!/usr/bin/env python3
"""Cheap mechanism probe on the author-released FCI rat Hay L5 model.

This is NOT an FCI reproduction and NOT a biological clustered-synapse result.
It is a plumbing/sanity experiment for the missing AMPA-only gate described in
MISSING_AMPA_ONLY_GATE.md.

The script loads the exact FCI `cell1.asc` model through the authors'
`get_standard_model.py`, selects dendritic sites at path-distance quantiles,
and compares the response of the same AMPANMDA_EMS point process with its
normal rat NMDA ratio versus `NMDA_ratio = 0`.

A "multiplier" scales one point process's event weight.  This is deliberately
called a conductance multiplier, not N biological synapses.  Its purpose is to
verify that the NMDA-off intervention works and to reveal where voltage-
dependent amplification begins before spending resources on full FCI runs.

Requirements
------------
- a clone of https://github.com/ido4848/FCI
- NEURON + the model mechanisms compiled as required by that repository
- numpy, pandas
- matplotlib only for --plot

Example
-------
python probe_nmda_cable.py --fci-root ../FCI --out probe_nmda_cable.csv --plot
"""

from __future__ import annotations

import argparse
import importlib
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


MODEL_MODULE = (
    "simulating_neurons.neuron_models.rat.hay."
    "Rat_L5b_PC_2_Hay_passive_dends_simple_soma.get_standard_model"
)


@dataclass
class Site:
    label: str
    row_index: int
    distance_um: float
    sec_name: str
    x: float


def load_author_model(fci_root: Path):
    root = fci_root.resolve()
    if not root.exists():
        raise FileNotFoundError(root)
    sys.path.insert(0, str(root))
    module = importlib.import_module(MODEL_MODULE)
    cell, syn_df = module.create_cell()
    from neuron import h

    return h, cell, syn_df


def dendritic_distances(h, cell, syn_df) -> np.ndarray:
    # Define distance origin at the center of the soma.
    h.distance(0.0, 0.5, sec=cell.soma[0])
    out = []
    for seg in syn_df["segments"]:
        out.append(float(h.distance(seg.x, sec=seg.sec)))
    return np.asarray(out, dtype=float)


def choose_sites(distances: np.ndarray, syn_df, quantiles: list[float]) -> list[Site]:
    order = np.argsort(distances)
    sites: list[Site] = []
    used: set[int] = set()
    for q in quantiles:
        pos = int(round(q * (len(order) - 1)))
        idx = int(order[pos])
        # Avoid duplicate quantile picks on small morphologies.
        if idx in used:
            continue
        used.add(idx)
        seg = syn_df.iloc[idx]["segments"]
        sites.append(
            Site(
                label=f"q{q:.2f}",
                row_index=idx,
                distance_um=float(distances[idx]),
                sec_name=str(seg.sec.name()),
                x=float(seg.x),
            )
        )
    return sites


def run_event(
    h,
    cell,
    syn_df,
    site: Site,
    nmda_ratio: float,
    weight_multiplier: float,
    event_ms: float,
    tstop_ms: float,
    v_init_mv: float,
):
    row = syn_df.iloc[site.row_index]
    seg = row["segments"]
    syn = row["exc_synapses"]
    nc = row["exc_netcons"]

    original_ratio = float(syn.NMDA_ratio)
    original_weight = float(nc.weight[0])

    t = h.Vector()
    soma_v = h.Vector()
    local_v = h.Vector()
    t.record(h._ref_t)
    soma_v.record(cell.soma[0](0.5)._ref_v)
    local_v.record(seg._ref_v)

    try:
        syn.NMDA_ratio = float(nmda_ratio)
        nc.weight[0] = original_weight * float(weight_multiplier)

        h.finitialize(v_init_mv)
        # NetCon(None, synapse) in the released FCI model accepts explicit events.
        nc.event(event_ms)
        h.continuerun(tstop_ms)

        tt = np.asarray(t, dtype=float)
        sv = np.asarray(soma_v, dtype=float)
        lv = np.asarray(local_v, dtype=float)
    finally:
        syn.NMDA_ratio = original_ratio
        nc.weight[0] = original_weight

    pre = tt < event_ms
    post = tt >= event_ms
    soma_base = float(np.median(sv[pre]))
    local_base = float(np.median(lv[pre]))

    soma_delta = sv[post] - soma_base
    local_delta = lv[post] - local_base
    soma_peak_i = int(np.argmax(soma_delta))
    local_peak_i = int(np.argmax(local_delta))
    t_post = tt[post]

    return {
        "soma_peak_mv": float(soma_delta[soma_peak_i]),
        "soma_peak_time_ms": float(t_post[soma_peak_i] - event_ms),
        "local_peak_mv": float(local_delta[local_peak_i]),
        "local_peak_time_ms": float(t_post[local_peak_i] - event_ms),
        "soma_spiked": bool(np.max(sv[post]) > -20.0),
        "soma_max_absolute_mv": float(np.max(sv[post])),
        "local_max_absolute_mv": float(np.max(lv[post])),
        "original_netcon_weight": original_weight,
    }


def add_supralinearity(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["local_gain_vs_weight"] = np.nan
    df["soma_gain_vs_weight"] = np.nan
    group_cols = ["site", "nmda_condition"]
    for _, inds in df.groupby(group_cols).groups.items():
        sub = df.loc[inds]
        one = sub[np.isclose(sub["weight_multiplier"], 1.0)]
        if len(one) != 1:
            continue
        local1 = float(one.iloc[0]["local_peak_mv"])
        soma1 = float(one.iloc[0]["soma_peak_mv"])
        for idx in inds:
            mult = float(df.loc[idx, "weight_multiplier"])
            if local1 != 0:
                df.loc[idx, "local_gain_vs_weight"] = float(
                    df.loc[idx, "local_peak_mv"] / (mult * local1)
                )
            if soma1 != 0 and not bool(df.loc[idx, "soma_spiked"]):
                df.loc[idx, "soma_gain_vs_weight"] = float(
                    df.loc[idx, "soma_peak_mv"] / (mult * soma1)
                )
    return df


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--fci-root", type=Path, required=True)
    p.add_argument("--out", type=Path, default=Path("probe_nmda_cable.csv"))
    p.add_argument(
        "--quantiles",
        type=float,
        nargs="+",
        default=[0.10, 0.35, 0.60, 0.85, 0.97],
        help="dendritic path-distance quantiles",
    )
    p.add_argument(
        "--multipliers",
        type=float,
        nargs="+",
        default=[1, 5, 20, 50, 100],
        help="event conductance multipliers (not biological synapse counts)",
    )
    p.add_argument("--event-ms", type=float, default=20.0)
    p.add_argument("--tstop-ms", type=float, default=250.0)
    p.add_argument("--v-init-mv", type=float, default=-70.0)
    p.add_argument("--plot", action="store_true")
    args = p.parse_args()

    h, cell, syn_df = load_author_model(args.fci_root)
    distances = dendritic_distances(h, cell, syn_df)
    sites = choose_sites(distances, syn_df, args.quantiles)

    # Read the released rat ratio from each target rather than hard-coding it.
    rows = []
    for site in sites:
        original_ratio = float(syn_df.iloc[site.row_index]["exc_synapses"].NMDA_ratio)
        print(
            f"\n[{site.label}] {site.sec_name}({site.x:.3f}) "
            f"distance={site.distance_um:.1f} um  released NMDA_ratio={original_ratio:.4g}"
        )
        for condition, ratio in [("AMPA_ONLY", 0.0), ("RAT_NMDA", original_ratio)]:
            for mult in args.multipliers:
                result = run_event(
                    h,
                    cell,
                    syn_df,
                    site,
                    nmda_ratio=ratio,
                    weight_multiplier=mult,
                    event_ms=args.event_ms,
                    tstop_ms=args.tstop_ms,
                    v_init_mv=args.v_init_mv,
                )
                row = {
                    "site": site.label,
                    "row_index": site.row_index,
                    "distance_um": site.distance_um,
                    "section": site.sec_name,
                    "x": site.x,
                    "nmda_condition": condition,
                    "nmda_ratio": ratio,
                    "weight_multiplier": float(mult),
                    **result,
                }
                rows.append(row)
                print(
                    f"  {condition:10s} x{mult:<5g} "
                    f"local={result['local_peak_mv']:+8.3f} mV  "
                    f"soma={result['soma_peak_mv']:+8.3f} mV  "
                    f"spike={result['soma_spiked']}"
                )

    df = add_supralinearity(pd.DataFrame(rows))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"\nWrote {args.out.resolve()}")

    # Basic intervention guardrail: the two conditions should not be numerically
    # identical once the drive is strong enough to recruit NMDA appreciably.
    merged = df.pivot_table(
        index=["site", "weight_multiplier"],
        columns="nmda_condition",
        values="local_peak_mv",
    )
    if {"AMPA_ONLY", "RAT_NMDA"}.issubset(merged.columns):
        max_gap = float(np.max(np.abs(merged["RAT_NMDA"] - merged["AMPA_ONLY"])))
        print(f"Max local peak difference, NMDA-on minus AMPA-only: {max_gap:.6g} mV")
        if max_gap < 1e-6:
            raise RuntimeError(
                "NMDA-on and AMPA-only responses are numerically identical. "
                "Treat this as an intervention/plumbing failure before doing FCI work."
            )

    if args.plot:
        import matplotlib.pyplot as plt

        for site in df["site"].unique():
            fig, ax = plt.subplots()
            for condition in ["AMPA_ONLY", "RAT_NMDA"]:
                sub = df[(df["site"] == site) & (df["nmda_condition"] == condition)]
                ax.plot(
                    sub["weight_multiplier"],
                    sub["local_peak_mv"],
                    marker="o",
                    label=condition,
                )
            ax.set_xscale("log")
            ax.set_xlabel("event conductance multiplier (not synapse count)")
            ax.set_ylabel("local peak depolarization (mV)")
            ax.set_title(f"{site}: NMDA intervention sanity")
            ax.legend()
            fig.tight_layout()
            path = args.out.with_name(f"{args.out.stem}_{site}.png")
            fig.savefig(path, dpi=160)
            plt.close(fig)
            print(f"Wrote {path.resolve()}")


if __name__ == "__main__":
    main()
