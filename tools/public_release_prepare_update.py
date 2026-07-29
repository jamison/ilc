#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Prepare a no-push public release propagation receipt.

This tool is local-only. It records the source commit, source-export rehearsal
result, optional sanitized mirror generation result, and forward-compatible
graph-native fields. It never pushes to a remote or changes repository
visibility.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "ilc_public_release_propagation_receipt.v0.1"
PHASE = "1575e"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _run_git(args: list[str], *, cwd: Path) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, sort_keys=True, separators=(",", ":"), allow_nan=False)
            handle.write("\n")
        os.replace(tmp_path, path)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def _run_source_export(repo_root: Path) -> tuple[dict[str, Any], str]:
    fd, tmp_name = tempfile.mkstemp(prefix="ilc-1575e-source-export.", suffix=".json")
    os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        subprocess.run(
            [
                str(repo_root / ".venv/bin/python"),
                "ilc_core/rc/source_allowlist_export_rehearsal.py",
                "--json-out",
                str(tmp_path),
            ],
            cwd=repo_root,
            check=True,
        )
        return json.loads(tmp_path.read_text(encoding="utf-8")), _sha256_file(tmp_path)
    finally:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass


def _run_mirror_generation(
    repo_root: Path,
    *,
    mirror_output_dir: Path | None,
) -> dict[str, Any]:
    output_dir = mirror_output_dir or Path(
        f"/tmp/ilc-public-mirror-1575e-{_run_git(['rev-parse', '--short', 'HEAD'], cwd=repo_root)}"
    )
    proc = subprocess.run(
        [
            "bash",
            "tools/scripts/generate_public_mirror.sh",
            str(repo_root),
            str(output_dir),
        ],
        cwd=repo_root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return json.loads(proc.stdout)


def _changed_files(repo_root: Path, baseline_commit: str | None) -> tuple[list[str], str]:
    if baseline_commit is None:
        return [], "requires_explicit_baseline_commit"
    try:
        _run_git(["cat-file", "-e", f"{baseline_commit}^{{commit}}"], cwd=repo_root)
    except subprocess.CalledProcessError:
        return [], "baseline_commit_not_found"
    files = _run_git(["diff", "--name-only", f"{baseline_commit}..HEAD"], cwd=repo_root)
    return sorted(line for line in files.splitlines() if line), "computed_from_explicit_baseline_commit"


def build_receipt(
    *,
    source_private_commit: str | None = None,
    baseline_commit: str | None = None,
    generate_mirror: bool = False,
    mirror_output_dir: Path | None = None,
) -> dict[str, Any]:
    repo_root = _repo_root()
    commit = source_private_commit or _run_git(["rev-parse", "HEAD"], cwd=repo_root)
    branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root)
    status_short = _run_git(["status", "--short"], cwd=repo_root)
    changed_files, baseline_status = _changed_files(repo_root, baseline_commit)
    source_export_manifest, manifest_sha256 = _run_source_export(repo_root)
    counts = source_export_manifest.get("counts", {})
    mirror_manifest: dict[str, Any] | None = None
    if generate_mirror:
        mirror_manifest = _run_mirror_generation(repo_root, mirror_output_dir=mirror_output_dir)

    receipt: dict[str, Any] = {
        "changed_file_baseline_status": baseline_status,
        "changed_files_since_last_public_release": changed_files,
        "graph_accounting": {
            "coverage_status": "checked_or_deferred_with_named_gap",
            "missing_records": [],
            "mode": "fix38_or_atlas_candidate",
        },
        "homoiconic_forward_fields": {
            "atlas_lmdb_root": None,
            "atlas_slice_manifest_id": None,
            "content_availability_layer_status": "post_rc_target",
            "graph_native_exporter_status": "not_activated",
            "package_profile_id": None,
        },
        "non_claims": [
            "no_public_push",
            "no_repository_visibility_change",
            "no_package_publication",
            "no_graph_native_exporter_activation",
            "no_guard_clearance",
            "no_ecu_minting",
            "no_ilc_settlement",
            "no_production_wallet_write",
            "no_epoch_transition",
        ],
        "phase": PHASE,
        "private_worktree_clean": status_short == "",
        "public_push_authorized": False,
        "sanitized_mirror": {
            "archive_sha256": None,
            "denylist_scan_result": None,
            "filtered_public_head_sha": None,
            "generated": False,
            "public_rc_exclude_scan_result": None,
            "staging_dir": None,
        },
        "schema_version": SCHEMA_VERSION,
        "source_export": {
            "blocked_ambiguities": int(counts.get("blocked_ambiguities", 0)),
            "excluded_files": int(counts.get("excluded_files", 0)),
            "included_files": int(counts.get("included_files", 0)),
            "manifest_sha256": manifest_sha256,
            "result": source_export_manifest.get("result"),
        },
        "source_private_branch": branch,
        "source_private_commit": commit,
    }
    if mirror_manifest is not None:
        receipt["sanitized_mirror"] = {
            "archive_sha256": mirror_manifest.get("canonical_hash"),
            "denylist_scan_result": mirror_manifest.get("denylist_scan_result"),
            "filtered_public_head_sha": mirror_manifest.get("filtered_public_head_sha"),
            "generated": True,
            "public_rc_exclude_scan_result": mirror_manifest.get("public_rc_exclude_scan_result"),
            "staging_dir": mirror_manifest.get("staging_dir"),
        }
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", required=True, type=Path)
    parser.add_argument("--source-private-commit")
    parser.add_argument("--last-public-release-commit")
    parser.add_argument("--generate-mirror", action="store_true")
    parser.add_argument("--mirror-output-dir", type=Path)
    args = parser.parse_args(argv)
    receipt = build_receipt(
        source_private_commit=args.source_private_commit,
        baseline_commit=args.last_public_release_commit,
        generate_mirror=args.generate_mirror,
        mirror_output_dir=args.mirror_output_dir,
    )
    if receipt.get("public_push_authorized") is not False:
        raise ValueError("public_push_authorized_must_be_false")
    _write_json_atomic(args.json_out, receipt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
