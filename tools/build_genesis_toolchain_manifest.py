#!/usr/bin/env python3
"""Build the Phase 1142s Genesis bootstrap toolchain manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT = REPO_ROOT / "out" / "genesis_bootstrap_toolchain_manifest_v0.1.json"
CEREMONY_DATE = "2026-05-03"

FILES: tuple[tuple[str, str], ...] = (
    ("tools/crawl_genesis_node_candidates.py", "tool"),
    ("tools/compare_genesis_star_map_to_repo_graph.py", "tool"),
    ("tools/genesis_compile_coverage_diagnostic.py", "tool"),
    ("tools/build_genesis_attestation_manifest.py", "tool"),
    ("tools/build_genesis_toolchain_manifest.py", "tool"),
    ("tools/build_genesis_implementation_manifest.py", "tool"),
    ("tools/build_genesis_signing_root_envelope.py", "tool"),
    ("ilc_consensus/Cargo.toml", "tool_config"),
    ("ilc_consensus/src/pq_sign_main.rs", "tool"),
    ("docs/sims/sim_spectral_02/genesis_core_star_map_curated_seed_v0.1.json", "input"),
    ("docs/specs/ilc_genesis_intent_attestation_and_init_authority_map_v0.1.md", "input"),
    ("out/genesis_core_star_map_v0.1.json", "generated_output"),
    ("out/genesis_compile_coverage_diagnostic_v0.1.json", "generated_output"),
    ("out/genesis_node_attestation_manifest_v0.1.json", "generated_output"),
)


def _canonical_bytes(obj: Any) -> bytes:
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_canonical_bytes(obj) + b"\n")


def _require_tracked(path: str) -> None:
    subprocess.run(
        ["git", "ls-files", "--error-unmatch", path],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )


def build_manifest() -> dict[str, Any]:
    entries = []
    for rel_path, role in FILES:
        _require_tracked(rel_path)
        path = REPO_ROOT / rel_path
        if not path.is_file():
            raise ValueError(f"toolchain_manifest_missing_file:{rel_path}")
        entries.append(
            {
                "path": rel_path,
                "role": role,
                "sha256": _sha256_file(path),
            }
        )

    manifest = {
        "canonicalization": "json.dumps(sort_keys=True,separators=(',', ':'),allow_nan=False)",
        "files": sorted(entries, key=lambda item: item["path"]),
        "issuer": "genesis_agent:01",
        "manifest_created": CEREMONY_DATE,
        "manifest_hash": None,
        "manifest_type": "genesis_bootstrap_toolchain_manifest",
        "manifest_version": "v0.1",
        "public_key_ref": "artifact:genesis_agent1_pubkey_record_838a",
    }
    manifest["manifest_hash"] = _sha256_bytes(_canonical_bytes(manifest))
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()

    manifest = build_manifest()
    _write_json(args.out, manifest)
    print(manifest["manifest_hash"])


if __name__ == "__main__":
    main()
