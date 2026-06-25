# SPDX-License-Identifier: AGPL-3.0-only
"""Fix83 public-RC materialization bootstrap regression tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from ilc_core.distribution.materialization import (
    GENESIS_ROOT,
    PROFILE_NAME,
    RECONSTRUCTION_NOTES,
    FetchSources,
    MaterializationError,
    bootstrap,
    fetch_file_bytes,
    generate_materialization_manifest,
    materialize_tree,
    sha256_bytes,
    verify_materialized_tree,
    write_json_atomic,
)


PROFILE_PATH = Path("docs/specs/ilc_public_rc_package_profile_v0.1.json")


def _tiny_profile(tmp_path: Path) -> tuple[Path, dict[str, object]]:
    repo_root = tmp_path / "repo"
    source = repo_root / "ilc_core" / "tiny.py"
    source.parent.mkdir(parents=True)
    source.write_text("VALUE = 'fix83'\n", encoding="utf-8")
    digest = sha256_bytes(source.read_bytes())
    profile = {
        "file_count": 1,
        "files": [
            {
                "content_node_id": "repo:file:test:ilc_core_tiny_py",
                "node_id": "repo:file_ref:ilc_core_tiny_py",
                "package_membership": True,
                "size_bytes": source.stat().st_size,
                "source_path": "ilc_core/tiny.py",
                "source_sha256": digest,
            }
        ],
        "genesis_root": GENESIS_ROOT,
        "graph_root": "out/genesis_base_graph_v0.4_unified.lmdb",
        "non_claims": ["not_behavioral_spec_conformance"],
        "package_manifest_sha256": "0" * 64,
        "package_merkle_root_m0": "1" * 64,
        "profile_name": PROFILE_NAME,
        "schema_version": "test_profile",
        "signed": False,
    }
    profile_path = tmp_path / "profile.json"
    write_json_atomic(profile_path, profile)
    return profile_path, {"profile": profile, "repo_root": repo_root}


def test_public_rc_profile_is_unsigned_and_file_ref_oriented() -> None:
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    assert profile["profile_name"] == "ilc-public-rc"
    assert profile["signed"] is False
    assert profile["file_count"] == len(profile["files"]) >= 400
    assert all(row["node_id"].startswith("repo:file_ref:") for row in profile["files"])
    assert all(row["content_node_id"].startswith("repo:file:") for row in profile["files"])


def test_manifest_generation_is_stable_and_unsigned() -> None:
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    manifest = generate_materialization_manifest(profile)
    assert manifest["signed"] is False
    assert manifest["file_count"] == profile["file_count"]
    assert len(manifest["manifest_sha256"]) == 64
    assert [row["destination_path"] for row in manifest["files"]] == sorted(
        row["destination_path"] for row in manifest["files"]
    )


def test_materializer_rejects_path_traversal(tmp_path: Path) -> None:
    profile_path, context = _tiny_profile(tmp_path)
    manifest = generate_materialization_manifest(context["profile"])  # type: ignore[arg-type]
    manifest["files"][0]["destination_path"] = "../escape.py"
    with pytest.raises(MaterializationError, match="path_traversal_forbidden"):
        materialize_tree(
            manifest,
            out_dir=tmp_path / "out",
            sources=FetchSources(repo_root=context["repo_root"]),  # type: ignore[arg-type]
        )
    assert profile_path.exists()


def test_fetch_requires_matching_hash(tmp_path: Path) -> None:
    _profile_path, context = _tiny_profile(tmp_path)
    entry = context["profile"]["files"][0]  # type: ignore[index]
    data = fetch_file_bytes(
        entry,  # type: ignore[arg-type]
        sources=FetchSources(repo_root=context["repo_root"]),  # type: ignore[arg-type]
        max_file_bytes=1024,
    )
    assert sha256_bytes(data) == entry["source_sha256"]  # type: ignore[index]
    bad = dict(entry)  # type: ignore[arg-type]
    bad["source_sha256"] = "f" * 64
    with pytest.raises(MaterializationError, match="bytes_not_found_with_matching_hash"):
        fetch_file_bytes(
            bad,
            sources=FetchSources(repo_root=context["repo_root"]),  # type: ignore[arg-type]
            max_file_bytes=1024,
        )


def test_bootstrap_cli_writes_unsigned_reconstruction_receipt(tmp_path: Path) -> None:
    profile_path, context = _tiny_profile(tmp_path)
    out_dir = tmp_path / "materialized"
    receipt_path = tmp_path / "receipt.json"
    payload = bootstrap(
        profile_path=profile_path,
        out_dir=out_dir,
        receipt_path=receipt_path,
        verify=True,
        repo_root=context["repo_root"],  # type: ignore[arg-type]
    )
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert payload["verification"]["ok"] is True
    assert receipt["signed"] is False
    assert receipt["notes"] == RECONSTRUCTION_NOTES
    assert receipt["files_verified"] == 1
    assert (out_dir / "ilc_core" / "tiny.py").read_text(encoding="utf-8") == "VALUE = 'fix83'\n"


def test_native_ilc_bootstrap_command_smoke(tmp_path: Path) -> None:
    profile_path, context = _tiny_profile(tmp_path)
    out_dir = tmp_path / "cli-out"
    receipt_path = tmp_path / "cli-receipt.json"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "ilc_core.cli.main",
            "bootstrap",
            "--profile",
            str(profile_path),
            "--out",
            str(out_dir),
            "--verify",
            "--receipt",
            str(receipt_path),
            "--repo-root",
            str(context["repo_root"]),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert payload["ok"] is True
    assert payload["data"]["verification"]["ok"] is True
    assert receipt["signed"] is False
    assert receipt["notes"] == RECONSTRUCTION_NOTES


def test_verify_reports_missing_file(tmp_path: Path) -> None:
    _profile_path, context = _tiny_profile(tmp_path)
    manifest = generate_materialization_manifest(context["profile"])  # type: ignore[arg-type]
    result = verify_materialized_tree(manifest, root=tmp_path / "missing-root")
    assert result["ok"] is False
    assert result["files_missing"] == 1
