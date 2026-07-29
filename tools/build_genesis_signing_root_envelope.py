#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Build the Phase 1142s Genesis signing root envelope."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT = REPO_ROOT / "out" / "genesis_signing_root_envelope_v0.1.json"
CEREMONY_DATE = "2026-05-03"
MANIFESTS: tuple[tuple[str, str], ...] = (
    ("genesis_node_attestation_manifest", "out/genesis_node_attestation_manifest_v0.1.json"),
    ("genesis_bootstrap_toolchain_manifest", "out/genesis_bootstrap_toolchain_manifest_v0.1.json"),
    ("genesis_reference_implementation_manifest", "out/genesis_reference_implementation_manifest_v0.1.json"),
)


def _canonical_bytes(obj: Any) -> bytes:
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_canonical_bytes(obj) + b"\n")


def build_envelope() -> dict[str, Any]:
    manifests = []
    for manifest_type, rel_path in MANIFESTS:
        manifest = _load_json(REPO_ROOT / rel_path)
        if manifest.get("manifest_type") != manifest_type:
            raise ValueError(f"manifest_type_mismatch:{rel_path}")
        manifests.append(
            {
                "manifest_hash": manifest["manifest_hash"],
                "manifest_type": manifest_type,
                "path": rel_path,
            }
        )

    envelope = {
        "envelope_created": CEREMONY_DATE,
        "envelope_hash": None,
        "envelope_type": "genesis_signing_root_envelope",
        "envelope_version": "v0.1",
        "issuer": "genesis_agent:01",
        "manifests": manifests,
        "public_key_ref": "artifact:genesis_agent1_pubkey_record_838a",
        "signing_algorithm": "ML-DSA-65 / FIPS 204",
        "signing_context": "ILC_GENESIS_ROOT_ENVELOPE_V1",
        "star_map_node_count": 32,
        "star_map_version": "v0.1",
    }
    envelope["envelope_hash"] = _sha256_bytes(_canonical_bytes(envelope))
    return envelope


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()

    envelope = build_envelope()
    _write_json(args.out, envelope)
    print(envelope["envelope_hash"])


if __name__ == "__main__":
    main()
