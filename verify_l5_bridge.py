#!/usr/bin/env python3
"""Verify the byte-identical Hay L5 morphology shared by two released lineages.

This checks a useful provenance bridge:

1. Aizenbud et al. FCI repository (2026 PNAS), rat L5 `cell1.asc`.
2. Beniaguev, Segev & London `neuron_as_deep_net` repository (2021 Neuron),
   the L5PC morphology loaded by `simulate_L5PC_and_create_dataset.py`.

The two public repositories currently expose the same Git blob SHA-1.  This
script verifies that from the downloaded bytes rather than trusting filenames.

Important: this does NOT prove that the unreleased TwinProp repository uses
these exact bytes.  The 2026 TwinProp preprint states that it uses the Hay et
al. 2011 L5PC and builds on the Beniaguev digital-twin line, but its code/data
are stated to become public upon publication.  Keep that distinction explicit.
"""

from __future__ import annotations

import hashlib
from urllib.request import Request, urlopen


FCI_URL = (
    "https://raw.githubusercontent.com/ido4848/FCI/main/"
    "simulating_neurons/neuron_models/rat/hay/"
    "Rat_L5b_PC_2_Hay_passive_dends_simple_soma/"
    "morphologies/cell1.asc"
)

BENIAGUEV_COMMIT = "074c4666300a8ad246601dab179a97a6942f0f29"
BENIAGUEV_URL = (
    "https://raw.githubusercontent.com/SelfishGene/neuron_as_deep_net/"
    f"{BENIAGUEV_COMMIT}/L5PC_NEURON_simulation/morphologies/cell1.asc"
)

EXPECTED_GIT_BLOB_SHA1 = "2ba87cb91601c44a78a764646cf5abd01d5e1266"

# In the frozen GeometricNeuronV22 mapping, this morphology is order 7 in
# Aizenbud Fig. 2.  The digitized/published target table assigns order 7 FCI:
AIZENBUD_FIG2_ORDER = 7
AIZENBUD_FIG2_FCI = 0.2342


def download(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": "Dig-L5-bridge-verifier/1"})
    with urlopen(req, timeout=60) as response:
        return response.read()


def git_blob_sha1(data: bytes) -> str:
    prefix = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(prefix + data).hexdigest()


def main() -> None:
    fci = download(FCI_URL)
    beniaguev = download(BENIAGUEV_URL)

    fci_sha = git_blob_sha1(fci)
    ben_sha = git_blob_sha1(beniaguev)

    print("FCI bytes:       ", len(fci))
    print("Beniaguev bytes: ", len(beniaguev))
    print("FCI Git blob:    ", fci_sha)
    print("Beniaguev blob:  ", ben_sha)
    print("Expected blob:   ", EXPECTED_GIT_BLOB_SHA1)
    print("Byte-identical:  ", fci == beniaguev)
    print()
    print(
        f"Aizenbud Fig. 2 mapping: order={AIZENBUD_FIG2_ORDER}, "
        f"FCI={AIZENBUD_FIG2_FCI:.4f}"
    )

    if fci_sha != EXPECTED_GIT_BLOB_SHA1:
        raise RuntimeError("FCI source blob no longer matches the frozen receipt")
    if ben_sha != EXPECTED_GIT_BLOB_SHA1:
        raise RuntimeError("Beniaguev source blob no longer matches the frozen receipt")
    if fci != beniaguev:
        raise RuntimeError("The two morphology files are no longer byte-identical")

    print("[OK] exact morphology bridge verified")


if __name__ == "__main__":
    main()
