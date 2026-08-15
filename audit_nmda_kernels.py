#!/usr/bin/env python3
"""Audit the released FCI NMDA temporal kernels against the passive membrane scale.

This is a formula/provenance helper for TEMPORAL_LOOP_MATCHING.md.  It does not
simulate a neuron and does not estimate FCI.

The defaults are the released FCI parameter values at commit
55826436751c03a32dfd39e91a48894869e1db57:

rat:   tau_r_NMDA=0.29 ms, tau_d_NMDA=43 ms, nominal NMDA peak=0.00030
human: tau_r_NMDA=5 ms,    tau_d_NMDA=43 ms, nominal NMDA peak=0.00131

The released passive HOC has tau_m = cm/g_pas = 20 ms in soma/axon and dendrite.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Kernel:
    name: str
    tau_r_ms: float
    tau_d_ms: float
    peak_scale: float


def t_peak_ms(tau_r_ms: float, tau_d_ms: float) -> float:
    if not (0 < tau_r_ms < tau_d_ms):
        raise ValueError("require 0 < tau_r < tau_d")
    return (
        tau_r_ms
        * tau_d_ms
        / (tau_d_ms - tau_r_ms)
        * math.log(tau_d_ms / tau_r_ms)
    )


def peak_normalization(tau_r_ms: float, tau_d_ms: float) -> float:
    tp = t_peak_ms(tau_r_ms, tau_d_ms)
    raw_peak = math.exp(-tp / tau_d_ms) - math.exp(-tp / tau_r_ms)
    return 1.0 / raw_peak


def unit_peak_integral_ms(tau_r_ms: float, tau_d_ms: float) -> float:
    """Integral of a peak-normalized dual exponential, in ms."""
    a = peak_normalization(tau_r_ms, tau_d_ms)
    return a * (tau_d_ms - tau_r_ms)


def report(k: Kernel, tau_m_ms: float) -> dict[str, float]:
    tp = t_peak_ms(k.tau_r_ms, k.tau_d_ms)
    area = unit_peak_integral_ms(k.tau_r_ms, k.tau_d_ms)
    return {
        "t_peak_ms": tp,
        "t_peak_over_tau_m": tp / tau_m_ms,
        "unit_peak_integral_ms": area,
        "nominal_conductance_area": area * k.peak_scale,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--tau-m-ms", type=float, default=20.0)
    args = p.parse_args()

    rat = Kernel("rat", tau_r_ms=0.29, tau_d_ms=43.0, peak_scale=0.00030)
    human = Kernel("human", tau_r_ms=5.0, tau_d_ms=43.0, peak_scale=0.00131)

    rr = report(rat, args.tau_m_ms)
    hr = report(human, args.tau_m_ms)

    print(f"Passive membrane reference tau_m = {args.tau_m_ms:.6g} ms\n")
    for k, r in [(rat, rr), (human, hr)]:
        print(k.name)
        print(f"  tau_r_NMDA                 = {k.tau_r_ms:.6g} ms")
        print(f"  tau_d_NMDA                 = {k.tau_d_ms:.6g} ms")
        print(f"  t_peak                     = {r['t_peak_ms']:.6f} ms")
        print(f"  t_peak / tau_m             = {r['t_peak_over_tau_m']:.6f}")
        print(f"  unit-peak integral         = {r['unit_peak_integral_ms']:.6f} ms")
        print(f"  nominal NMDA peak scale    = {k.peak_scale:.8f}")
        print(
            "  nominal conductance area  = "
            f"{r['nominal_conductance_area']:.10f} peak_scale*ms"
        )
        print()

    print("rat -> human ratios")
    print(f"  tau_r ratio                = {human.tau_r_ms / rat.tau_r_ms:.6f}")
    print(f"  t_peak ratio               = {hr['t_peak_ms'] / rr['t_peak_ms']:.6f}")
    print(
        "  unit-peak area ratio      = "
        f"{hr['unit_peak_integral_ms'] / rr['unit_peak_integral_ms']:.6f}"
    )
    print(f"  nominal peak ratio         = {human.peak_scale / rat.peak_scale:.6f}")
    print(
        "  nominal area ratio        = "
        f"{hr['nominal_conductance_area'] / rr['nominal_conductance_area']:.6f}"
    )

    # Exact regression values for the documented defaults.  These assertions
    # catch accidental formula/parameter drift in this small audit helper.
    assert abs(rr["t_peak_ms"] - 1.4595752438) < 1e-9
    assert abs(hr["t_peak_ms"] - 12.1744440448) < 1e-9
    assert abs(rr["unit_peak_integral_ms"] - 44.4846295446) < 1e-9
    assert abs(hr["unit_peak_integral_ms"] - 57.0727472354) < 1e-9


if __name__ == "__main__":
    main()
