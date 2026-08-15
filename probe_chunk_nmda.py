#!/usr/bin/env python3
"""Joint segmentation/contact-aggregation convergence screen on FCI Hay cell1.

This is Gate D0 from DISCRETIZATION_NMDA_GATE.md.

It intentionally changes the released HOC ``chunkSize`` and therefore changes
BOTH cable discretization and the spatial binning of the segment-level synaptic
point processes.  A difference is a reason to run the D1/D2 controls; it is not
by itself evidence of a synaptic aggregation artefact.

For a fixed physical dendritic section and center, the script activates an
interval of W micrometres.  It uses one equivalent excitatory contact per
micrometre, but collapses the contacts falling in each NEURON segment onto that
segment's released AMPANMDA point process.  Thus total equivalent contact count
is held approximately equal to W while the spatial aggregation scale changes
with ``chunkSize``.

Run both AMPA-only and released rat-NMDA conditions.

Example
-------
python probe_chunk_nmda.py --fci-root ../FCI --plot

Requirements
------------
- local clone of ido4848/FCI
- NEURON and the FCI mechanisms compiled/available as required by that repo
- numpy, pandas
- matplotlib only for --plot
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd


MODEL_MODULE = (
    "simulating_neurons.neuron_models.rat.hay."
    "Rat_L5b_PC_2_Hay_passive_dends_simple_soma.get_standard_model"
)
NATIVE_CHUNK_UM = 24.30


def canonical_sec_name(sec) -> str:
    """Drop template-instance prefix; keep e.g. apic[17]."""
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


def create_cell(module, chunk_um: float):
    # The Hay wrapper exposes max_segment_length, which is passed as the HOC
    # chunkSize used by nseg = 1 + 2*int(L/chunkSize).
    return module.create_cell(max_segment_length=float(chunk_um))


def unique_dendritic_sections(syn_df):
    found = {}
    for seg in syn_df["segments"]:
        found[canonical_sec_name(seg.sec)] = seg.sec
    return found


def choose_long_section(syn_df, min_length_um: float):
    sections = unique_dendritic_sections(syn_df)
    candidates = [(float(sec.L), name, sec) for name, sec in sections.items()]
    candidates.sort(reverse=True, key=lambda x: x[0])
    for length, name, sec in candidates:
        if length >= min_length_um:
            return name, float(length)
    raise RuntimeError(
        f"No dendritic section at least {min_length_um:g} um long; "
        f"longest is {candidates[0][0]:.3f} um" if candidates else "No dendritic sections"
    )


def section_rows(syn_df, section_name: str):
    mask = [canonical_sec_name(seg.sec) == section_name for seg in syn_df["segments"]]
    return syn_df.loc[mask]


def interval_overlaps(rows, center_x: float, window_um: float):
    """Return (row_index, overlap_um) for segment bins intersecting the window."""
    if len(rows) == 0:
        raise RuntimeError("Target section has no released synaptic rows")

    sec = rows.iloc[0]["segments"].sec
    L = float(sec.L)
    center_um = float(center_x) * L
    lo = center_um - window_um / 2.0
    hi = center_um + window_um / 2.0
    if lo < -1e-9 or hi > L + 1e-9:
        raise ValueError(
            f"Window {window_um:g} um around x={center_x:g} does not fit "
            f"inside section of length {L:.3f} um"
        )

    selected = []
    for idx, row in rows.iterrows():
        seg = row["segments"]
        seg_len = float(row["seg_lens"])
        seg_center = float(seg.x) * L
        seg_lo = seg_center - seg_len / 2.0
        seg_hi = seg_center + seg_len / 2.0
        overlap = max(0.0, min(hi, seg_hi) - max(lo, seg_lo))
        if overlap > 1e-12:
            selected.append((idx, overlap))
    return selected


def run_interval_event(
    h,
    cell,
    syn_df,
    section_name: str,
    center_x: float,
    window_um: float,
    nmda_on: bool,
    event_ms: float,
    tstop_ms: float,
    v_init_mv: float,
):
    rows = section_rows(syn_df, section_name)
    selected = interval_overlaps(rows, center_x, window_um)
    if not selected:
        raise RuntimeError("No segment overlap selected")

    target_sec = rows.iloc[0]["segments"].sec

    tvec = h.Vector().record(h._ref_t)
    soma_vec = h.Vector().record(cell.soma[0](0.5)._ref_v)
    local_vec = h.Vector().record(target_sec(center_x)._ref_v)

    originals = []
    released_rat_ratios = []
    try:
        for idx, overlap_um in selected:
            row = syn_df.loc[idx]
            syn = row["exc_synapses"]
            nc = row["exc_netcons"]
            ratio = float(syn.NMDA_ratio)
            base_weight = float(nc.weight[0])
            originals.append((syn, nc, ratio, base_weight))
            released_rat_ratios.append(ratio)

            # One equivalent source per micrometre.  The released implementation
            # collapses all sources represented by this spatial bin at the point
            # process, so multiply one-contact conductance by physical overlap.
            syn.NMDA_ratio = ratio if nmda_on else 0.0
            nc.weight[0] = base_weight * float(overlap_um)

        h.finitialize(v_init_mv)
        for syn, nc, ratio, base_weight in originals:
            nc.event(event_ms)
        h.continuerun(tstop_ms)

        tt = np.asarray(tvec, dtype=float)
        soma = np.asarray(soma_vec, dtype=float)
        local = np.asarray(local_vec, dtype=float)
    finally:
        for syn, nc, ratio, base_weight in originals:
            syn.NMDA_ratio = ratio
            nc.weight[0] = base_weight

    pre = tt < event_ms
    post = tt >= event_ms
    soma0 = float(np.median(soma[pre]))
    local0 = float(np.median(local[pre]))
    sd = soma[post] - soma0
    ld = local[post] - local0
    tp = tt[post] - event_ms

    si = int(np.argmax(sd))
    li = int(np.argmax(ld))
    equivalent_contacts = float(sum(overlap for _, overlap in selected))
    max_bin = float(max(overlap for _, overlap in selected))

    return {
        "equivalent_contacts": equivalent_contacts,
        "point_processes_used": int(len(selected)),
        "max_equiv_contacts_on_one_point": max_bin,
        "released_nmda_ratio": float(np.median(released_rat_ratios)),
        "local_peak_mv": float(ld[li]),
        "local_peak_time_ms": float(tp[li]),
        "soma_peak_mv": float(sd[si]),
        "soma_peak_time_ms": float(tp[si]),
        "soma_spiked": bool(np.max(soma[post]) > -20.0),
        "local_max_absolute_mv": float(np.max(local[post])),
        "soma_max_absolute_mv": float(np.max(soma[post])),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--fci-root", type=Path, required=True)
    p.add_argument(
        "--chunks-um",
        type=float,
        nargs="+",
        default=[24.30, 12.15, 6.075, 3.0375],
        help="HOC chunkSize values; native Hay value is 24.30 um",
    )
    p.add_argument(
        "--windows-um",
        type=float,
        nargs="+",
        default=[5, 10, 20, 35, 50],
        help="physical simultaneously activated interval; ~1 equivalent contact/um",
    )
    p.add_argument("--center-x", type=float, default=0.5)
    p.add_argument("--event-ms", type=float, default=20.0)
    p.add_argument("--tstop-ms", type=float, default=250.0)
    p.add_argument("--v-init-mv", type=float, default=-70.0)
    p.add_argument("--out", type=Path, default=Path("probe_chunk_nmda.csv"))
    p.add_argument("--plot", action="store_true")
    args = p.parse_args()

    if not (0.0 < args.center_x < 1.0):
        raise ValueError("--center-x must be strictly between 0 and 1")

    h, module = import_model(args.fci_root)

    # Select anatomy once from the native discretization, then use the same
    # section name and normalized center in every refined model.
    native_cell, native_syn_df = create_cell(module, NATIVE_CHUNK_UM)
    needed = max(args.windows_um) / (2.0 * min(args.center_x, 1.0 - args.center_x))
    section_name, section_length = choose_long_section(native_syn_df, needed)
    print(
        f"Target section: {section_name}, L={section_length:.3f} um, "
        f"center x={args.center_x:.3f}"
    )

    rows_out = []
    for chunk in args.chunks_um:
        cell, syn_df = create_cell(module, chunk)
        target_rows = section_rows(syn_df, section_name)
        if len(target_rows) == 0:
            raise RuntimeError(f"Could not recover {section_name} at chunk={chunk}")
        L = float(target_rows.iloc[0]["segments"].sec.L)
        print(
            f"\nchunk={chunk:g} um  dendritic channels={len(syn_df)}  "
            f"target nseg={len(target_rows)}  target L={L:.3f} um"
        )

        for nmda_on in [False, True]:
            condition = "RAT_NMDA" if nmda_on else "AMPA_ONLY"
            for window in args.windows_um:
                result = run_interval_event(
                    h,
                    cell,
                    syn_df,
                    section_name=section_name,
                    center_x=args.center_x,
                    window_um=float(window),
                    nmda_on=nmda_on,
                    event_ms=args.event_ms,
                    tstop_ms=args.tstop_ms,
                    v_init_mv=args.v_init_mv,
                )
                out = {
                    "chunk_um": float(chunk),
                    "native_chunk_ratio": float(chunk / NATIVE_CHUNK_UM),
                    "dendritic_channel_count": int(len(syn_df)),
                    "section": section_name,
                    "section_length_um": L,
                    "center_x": args.center_x,
                    "window_um": float(window),
                    "condition": condition,
                    **result,
                }
                rows_out.append(out)
                print(
                    f"  {condition:9s} W={window:5.1f}  "
                    f"points={result['point_processes_used']:3d}  "
                    f"maxbin={result['max_equiv_contacts_on_one_point']:6.2f}  "
                    f"local={result['local_peak_mv']:+8.3f} mV  "
                    f"soma={result['soma_peak_mv']:+8.3f} mV"
                )

    df = pd.DataFrame(rows_out)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"\nWrote {args.out.resolve()}")

    # Report native-vs-finest deltas for quick triage.
    native = min(args.chunks_um, key=lambda x: abs(x - NATIVE_CHUNK_UM))
    finest = min(args.chunks_um)
    for condition in ["AMPA_ONLY", "RAT_NMDA"]:
        a = df[(df.chunk_um == native) & (df.condition == condition)].set_index("window_um")
        b = df[(df.chunk_um == finest) & (df.condition == condition)].set_index("window_um")
        common = a.index.intersection(b.index)
        if len(common):
            gap = (a.loc[common, "local_peak_mv"] - b.loc[common, "local_peak_mv"]).abs()
            print(
                f"{condition}: max |native-finest| local peak = "
                f"{float(gap.max()):.6g} mV"
            )

    if args.plot:
        import matplotlib.pyplot as plt

        for condition in ["AMPA_ONLY", "RAT_NMDA"]:
            fig, ax = plt.subplots()
            sub = df[df.condition == condition]
            for chunk in args.chunks_um:
                s = sub[sub.chunk_um == chunk]
                ax.plot(
                    s["equivalent_contacts"],
                    s["local_peak_mv"],
                    marker="o",
                    label=f"chunk {chunk:g} um",
                )
            ax.set_xlabel("equivalent simultaneous contacts (~1/um)")
            ax.set_ylabel("local peak depolarization (mV)")
            ax.set_title(f"Joint refinement screen: {condition}")
            ax.legend()
            fig.tight_layout()
            path = args.out.with_name(f"{args.out.stem}_{condition}.png")
            fig.savefig(path, dpi=170)
            plt.close(fig)
            print(f"Wrote {path.resolve()}")


if __name__ == "__main__":
    main()
