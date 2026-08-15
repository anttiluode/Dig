#!/usr/bin/env python3
"""Fetch the four complete morphology files currently exposed by ido4848/FCI.

This is intentionally boring provenance plumbing.  It does *not* analyse the
morphologies and it does not imply that these four cells constitute a valid
species comparison.  The goal is to make the first Green-function sanity test
start from author-released bytes with checked Git blob IDs.

Optional SWC conversion uses MorphIO.  The original ASC files are always kept.

Usage
-----
    python fetch_aizenbud_exact4.py
    python fetch_aizenbud_exact4.py --convert-swc

For the optional conversion:
    pip install morphio
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen


REPO_RAW = "https://raw.githubusercontent.com/ido4848/FCI/main/"

FILES = {
    "rat_L2": {
        "path": (
            "simulating_neurons/neuron_models/rat/bbp/"
            "Rat_L2_TPC_BBP_Mandge_diams_fixed_passive_dends_simple_soma/"
            "morphologies/mtC191200B_idA_diams_fixed.asc"
        ),
        "git_blob_sha1": "3c9bcd81ff3e21bbe980f7bda50eca5efb9a7109",
    },
    "rat_L5": {
        "path": (
            "simulating_neurons/neuron_models/rat/hay/"
            "Rat_L5b_PC_2_Hay_passive_dends_simple_soma/"
            "morphologies/cell1.asc"
        ),
        "git_blob_sha1": "2ba87cb91601c44a78a764646cf5abd01d5e1266",
    },
    "human_L23": {
        "path": (
            "simulating_neurons/neuron_models/human/eyal/"
            "Human_L23_PC_0603_11_937_Eyal_passive_dends_simple_soma/"
            "morphologies/2013_03_06_cell11_1125_H41_06.asc"
        ),
        "git_blob_sha1": "42ce70f86f6ff01bfa35816fb1f66d5c407147af",
    },
    "human_L5": {
        "path": (
            "simulating_neurons/neuron_models/human/bbp/"
            "Human_L5_PC_BBP_passive_dends_simple_soma/"
            "morphologies/2057_H21_29_197_11_01_03_metcontour.asc"
        ),
        "git_blob_sha1": "39675ab43f032083fd1f3ce92d141385f058f6f7",
    },
}


def git_blob_sha1(data: bytes) -> str:
    """Compute the SHA-1 Git uses for a blob object."""
    prefix = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(prefix + data).hexdigest()


def download(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": "Dig-Aizenbud-Green-provenance/1"})
    with urlopen(req, timeout=60) as response:
        return response.read()


def convert_with_morphio(src: Path, dst: Path) -> None:
    try:
        from morphio.mut import Morphology
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise SystemExit(
            "--convert-swc requested but MorphIO is not installed. "
            "Run: pip install morphio"
        ) from exc

    morph = Morphology(str(src))
    # SWC cannot represent every ASC section convention.  MorphIO documents
    # remove_unifurcations() as the canonical preparation when such sections
    # are present.  This keeps the original ASC alongside the derived SWC.
    try:
        morph.write(str(dst))
    except Exception:
        morph.remove_unifurcations()
        morph.write(str(dst))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data") / "aizenbud_exact4",
        help="output directory (default: data/aizenbud_exact4)",
    )
    parser.add_argument(
        "--convert-swc",
        action="store_true",
        help="also make derived SWC copies using MorphIO",
    )
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    receipt: dict[str, dict[str, object]] = {}

    for label, meta in FILES.items():
        rel = str(meta["path"])
        url = REPO_RAW + rel
        data = download(url)
        observed = git_blob_sha1(data)
        expected = str(meta["git_blob_sha1"])

        if observed != expected:
            raise RuntimeError(
                f"{label}: provenance check failed: expected Git blob "
                f"{expected}, got {observed}"
            )

        src = args.out / f"{label}__{Path(rel).name}"
        src.write_bytes(data)

        row: dict[str, object] = {
            "source_repository": "ido4848/FCI",
            "source_branch": "main",
            "source_path": rel,
            "source_url": url,
            "git_blob_sha1": observed,
            "bytes": len(data),
            "local_asc": str(src),
        }

        if args.convert_swc:
            dst = src.with_suffix(".swc")
            convert_with_morphio(src, dst)
            row["derived_swc"] = str(dst)
            row["derived_swc_sha256"] = hashlib.sha256(dst.read_bytes()).hexdigest()

        receipt[label] = row
        print(f"[OK] {label:10s} {len(data):9d} bytes  {observed}")

    receipt_path = args.out / "PROVENANCE.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {receipt_path}")
    if not args.convert_swc:
        print("Tip: add --convert-swc after installing MorphIO for NEAT input files.")


if __name__ == "__main__":
    main()
