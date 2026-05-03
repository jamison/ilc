#!/usr/bin/env python3
"""Build the Phase 1142s Genesis reference implementation manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT = REPO_ROOT / "out" / "genesis_reference_implementation_manifest_v0.1.json"
CEREMONY_DATE = "2026-05-03"


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


def _git_ls_files(patterns: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", *patterns],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return sorted(line for line in result.stdout.splitlines() if line)


def _require_tracked(path: str) -> None:
    subprocess.run(
        ["git", "ls-files", "--error-unmatch", path],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )


def _role(path: str) -> str:
    if path.endswith(".proto"):
        return "proto"
    if path.endswith(".toml") or path.endswith(".lock"):
        return "config"
    if path.endswith(".py") or path.endswith(".rs"):
        return "source"
    return "source"


def _implementation_paths() -> list[str]:
    paths = set()
    paths.add("pyproject.toml")
    paths.update(_git_ls_files(["ilc_core/**/*.py"]))
    paths.add("ilc_consensus/Cargo.toml")
    paths.add("ilc_consensus/Cargo.lock")
    paths.update(
        path for path in _git_ls_files(["ilc_consensus/src"]) if path.endswith(".rs")
    )
    paths.update(
        path for path in _git_ls_files(["ilc_consensus/proto"]) if path.endswith(".proto")
    )
    excluded_parts = {"__pycache__", "target", "dist"}
    filtered = []
    for path in paths:
        parts = set(Path(path).parts)
        if parts & excluded_parts:
            continue
        if path.endswith(".pyc") or path.endswith(".egg-info"):
            continue
        filtered.append(path)
    return sorted(filtered)


def build_manifest() -> dict[str, Any]:
    entries = []
    for rel_path in _implementation_paths():
        _require_tracked(rel_path)
        path = REPO_ROOT / rel_path
        if not path.is_file():
            raise ValueError(f"implementation_manifest_missing_file:{rel_path}")
        entries.append(
            {
                "path": rel_path,
                "role": _role(rel_path),
                "sha256": _sha256_file(path),
            }
        )

    manifest = {
        "canonicalization": "json.dumps(sort_keys=True,separators=(',', ':'),allow_nan=False)",
        "files": entries,
        "implementation_scope": "ilc_core v0.1 + ilc_consensus v0.1",
        "issuer": "genesis_agent:01",
        "manifest_created": CEREMONY_DATE,
        "manifest_hash": None,
        "manifest_type": "genesis_reference_implementation_manifest",
        "manifest_version": "v0.1",
        "public_key_ref": "artifact:genesis_agent1_pubkey_record_838a",
        "release_key_binding": None,
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
