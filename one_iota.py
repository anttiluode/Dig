"""One Iota: time opens local geometry.

Conceptual unit test for the Dig repository.

The script finds two non-isomorphic trees with the same combinatorial
Laplacian spectrum. Because the eigenvalues are identical, every global
spectral statistic depending only on those eigenvalues is identical too,
including the heat trace Tr(exp(-t L)).

Then it looks locally.  For each vertex i it records the heat-kernel
self-response K_t(i,i) over several times.  The multiset of these local
signatures differs between the two trees.

So:

    global spectrum same
    global heat trace same
    local time evolution different

This does NOT establish anything biological.  It is a small exact warning
that a compressed global spectrum can throw away the location-dependent
information that a propagation experiment would reveal.

Dependencies:
    numpy
    networkx

Run:
    python one_iota.py
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

import networkx as nx
import numpy as np


TIMES = np.array([0.01, 0.03, 0.1, 0.3, 1.0, 3.0], dtype=float)


@dataclass
class CospectralPair:
    n: int
    first: nx.Graph
    second: nx.Graph


def laplacian(G: nx.Graph) -> np.ndarray:
    """Dense combinatorial graph Laplacian."""
    return nx.laplacian_matrix(G).toarray().astype(float)


def spectrum(G: nx.Graph) -> np.ndarray:
    return np.linalg.eigvalsh(laplacian(G))


def spectrum_key(G: nx.Graph, decimals: int = 10) -> tuple[float, ...]:
    return tuple(np.round(spectrum(G), decimals))


def find_laplacian_cospectral_trees(max_n: int = 14) -> CospectralPair:
    """Return the first pair of non-isomorphic trees sharing L spectrum."""
    for n in range(2, max_n + 1):
        buckets: dict[tuple[float, ...], list[nx.Graph]] = defaultdict(list)
        for G in nx.generators.nonisomorphic_trees(n):
            buckets[spectrum_key(G)].append(G)

        for group in buckets.values():
            if len(group) >= 2:
                return CospectralPair(n=n, first=group[0], second=group[1])

    raise RuntimeError(f"No Laplacian-cospectral tree pair found through n={max_n}")


def eigensystem(L: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    values, vectors = np.linalg.eigh(L)
    return values, vectors


def heat_kernel_from_eigensystem(
    values: np.ndarray, vectors: np.ndarray, t: float
) -> np.ndarray:
    """K_t = exp(-t L), using the symmetric eigendecomposition."""
    return (vectors * np.exp(-t * values)) @ vectors.T


def heat_trace(G: nx.Graph, times: np.ndarray = TIMES) -> np.ndarray:
    values = spectrum(G)
    return np.array([np.exp(-t * values).sum() for t in times])


def local_heat_signatures(
    G: nx.Graph, times: np.ndarray = TIMES
) -> np.ndarray:
    """Rows are vertex-local signatures [K_t(i,i)] across time."""
    L = laplacian(G)
    values, vectors = eigensystem(L)
    n = G.number_of_nodes()
    out = np.empty((n, len(times)), dtype=float)

    # K_t(i,i) = sum_k exp(-lambda_k t) * phi_k(i)^2
    local_mode_weight = vectors**2
    for j, t in enumerate(times):
        out[:, j] = local_mode_weight @ np.exp(-t * values)
    return out


def sorted_signature_rows(signatures: np.ndarray, decimals: int = 12) -> np.ndarray:
    """Permutation-invariant comparison of vertex-signature multisets."""
    rounded = np.round(signatures, decimals)
    return np.array(sorted(map(tuple, rounded)), dtype=float)


def graph_summary(G: nx.Graph) -> dict[str, object]:
    return {
        "n": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "degree_sequence": sorted(dict(G.degree()).values()),
        "diameter": nx.diameter(G),
        "edge_list": sorted(tuple(sorted(e)) for e in G.edges()),
    }


def main() -> None:
    pair = find_laplacian_cospectral_trees()
    G1, G2 = pair.first, pair.second

    s1 = spectrum(G1)
    s2 = spectrum(G2)
    trace1 = heat_trace(G1)
    trace2 = heat_trace(G2)
    local1 = local_heat_signatures(G1)
    local2 = local_heat_signatures(G2)

    local_multiset_gap = np.linalg.norm(
        sorted_signature_rows(local1) - sorted_signature_rows(local2)
    )

    print("ONE IOTA — COSPECTRAL WARNING")
    print("=" * 42)
    print(f"first Laplacian-cospectral tree pair found at n = {pair.n}")
    print(f"isomorphic? {nx.is_isomorphic(G1, G2)}")
    print(
        "same degree sequence?",
        sorted(dict(G1.degree()).values()) == sorted(dict(G2.degree()).values()),
    )
    print()

    print("graph A:")
    print(graph_summary(G1))
    print()
    print("graph B:")
    print(graph_summary(G2))
    print()

    print("GLOBAL SPECTRUM")
    print("max |lambda_A - lambda_B| =", float(np.max(np.abs(s1 - s2))))
    print("eigenvalues:")
    print(np.array2string(s1, precision=8, suppress_small=True))
    print()

    print("GLOBAL HEAT TRACE")
    for t, a, b in zip(TIMES, trace1, trace2):
        print(f"t={t:>4g}  trace_A={a:.12f}  trace_B={b:.12f}  diff={a-b:+.3e}")
    print()

    print("LOCAL HEAT SIGNATURES")
    print(
        "permutation-invariant Frobenius gap between the multisets of\n"
        "vertex signatures [K_t(i,i)] across the same times:"
    )
    print(f"local signature gap = {local_multiset_gap:.12f}")
    print()

    print("Interpretation:")
    print("  * the global eigenvalue spectrum is the same;")
    print("  * every global heat trace is therefore the same;")
    print("  * the trees are nevertheless non-isomorphic;")
    print("  * letting a localized observation evolve in time exposes a difference.")
    print()
    print("Spectrum alone did not carry the location algebra.")
    print("One iota of local evolution did.")


if __name__ == "__main__":
    main()
