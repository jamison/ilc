from __future__ import annotations

import json
from pathlib import Path

import pytest

from ilc_core.rc.source_allowlist_export_execution_gate import (
    PHASE_1333_EXECUTION_EXCLUDED_ROOTS,
    PUBLIC_RC_EXCLUDE_MARKER_SCAN_REQUIRED_TOKEN,
    SOURCE_ALLOWLIST_EXPORT_EXECUTION_GATE_VERSION,
    build_source_allowlist_export_execution_gate,
    canonical_source_allowlist_export_execution_gate_json,
    phase_1333_required_tokens,
    render_execution_gate_markdown,
    validate_source_allowlist_export_execution_gate,
)


ROOT = Path(__file__).resolve().parents[1]


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_phase_1333_current_repo_materializes_clean_export(tmp_path: Path) -> None:
    manifest = build_source_allowlist_export_execution_gate(
        repo_root=ROOT,
        export_root=tmp_path / "phase_1333_export",
    )

    assert manifest["schema_version"] == SOURCE_ALLOWLIST_EXPORT_EXECUTION_GATE_VERSION
    assert manifest["required_tokens"] == phase_1333_required_tokens()
    assert PUBLIC_RC_EXCLUDE_MARKER_SCAN_REQUIRED_TOKEN in manifest["required_tokens"]
    assert manifest["result"] == "executed_clean_export"
    assert (
        manifest["source_allowlist_export_execution_gate_verdict"]
        == "source_allowlist_export_execution_gate_verdict=pass"
    )
    assert manifest["source_allowlist_export_executed"] is True
    assert manifest["source_publication_authorized"] is False
    assert manifest["public_rc_remains_blocked"] is True
    assert manifest["candidate_scan"]["marker_scan"]["hit_count"] == 0
    assert manifest["candidate_scan"]["dependency_scan"]["stripped_helper_hit_count"] == 0
    assert manifest["candidate_scan"]["legacy_untagged_review"]["ambiguity_count"] == 0
    assert manifest["dirty_worktree_policy"]["dirty_included_files"] == []
    assert not any(
        record["path"].startswith("ilc_core/sim/")
        for record in manifest["candidate_scan"]["included_files"]
    )
    assert any(root == "ilc_core/sim" for root, _ in PHASE_1333_EXECUTION_EXCLUDED_ROOTS)

    tree = Path(manifest["export_materialization"]["tree_path"])
    assert tree.exists()
    assert (tree / "LICENSE").is_file()
    assert (tree / "LICENSING.md").is_file()
    assert (tree / "PATENTS.md").is_file()
    assert (tree / "THIRD_PARTY_NOTICES.md").is_file()
    assert (tree / "pyproject.toml").is_file()
    assert (tree / "ilc_core").is_dir()
    assert not (tree / "ilc_core/sim").exists()
    assert manifest["export_materialization"]["exported_file_count"] == manifest[
        "candidate_scan"
    ]["counts"]["included_files"]
    assert all(not row["triggered"] for row in manifest["rejection_criteria"])

    encoded = canonical_source_allowlist_export_execution_gate_json(manifest)
    assert encoded == json.dumps(
        json.loads(encoded),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def test_phase_1333_blocked_marker_candidate_does_not_materialize(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(repo / "src/marked.py", "# PUBLIC_RC_EXCLUDE: synthetic\nVALUE = 1\n")
    export_root = tmp_path / "export"

    manifest = build_source_allowlist_export_execution_gate(
        repo_root=repo,
        export_root=export_root,
        include_roots=("src",),
        excluded_roots=(),
        force_include_paths=("src/marked.py",),
    )

    assert manifest["result"] == "blocked_with_findings"
    assert (
        manifest["source_allowlist_export_execution_gate_verdict"]
        == "source_allowlist_export_execution_gate_verdict=block"
    )
    assert manifest["source_allowlist_export_executed"] is False
    assert manifest["clean_materialized_public_tree_produced"] is False
    assert manifest["candidate_scan"]["marker_scan"]["hit_count"] == 1
    assert any(
        row["criteria_id"] == "public_rc_exclude_marker_remains_in_exported_tree"
        and row["triggered"]
        for row in manifest["rejection_criteria"]
    )
    assert manifest["export_materialization"]["materialized"] is False
    assert not (export_root / "tree").exists()


def test_phase_1333_helper_dependency_blocks_export(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(
        repo / "src/main.py",
        "from ilc_core.ledger.claimability_proof_binding_runtime import X\n",
    )

    manifest = build_source_allowlist_export_execution_gate(
        repo_root=repo,
        export_root=tmp_path / "export",
        include_roots=("src",),
        excluded_roots=(),
    )

    assert manifest["result"] == "blocked_with_findings"
    assert manifest["candidate_scan"]["dependency_scan"]["stripped_helper_hit_count"] >= 1
    assert manifest["package_profile_internal_helper_check"]["result"] == "fail_closed"
    assert any(
        row["criteria_id"] == "exported_module_imports_stripped_helper"
        and row["triggered"]
        for row in manifest["rejection_criteria"]
    )


def test_phase_1333_manifest_validation_requires_evidence_sections(tmp_path: Path) -> None:
    manifest = build_source_allowlist_export_execution_gate(
        repo_root=ROOT,
        export_root=tmp_path / "phase_1333_export",
    )
    broken = json.loads(canonical_source_allowlist_export_execution_gate_json(manifest))
    broken["manifest_evidence"]["marker_scan_recorded"] = False
    broken["manifest_hash"] = ""

    with pytest.raises(ValueError, match="manifest_hash_invalid|manifest_evidence_incomplete"):
        validate_source_allowlist_export_execution_gate(broken)


def test_phase_1333_markdown_records_non_authorization(tmp_path: Path) -> None:
    manifest = build_source_allowlist_export_execution_gate(
        repo_root=ROOT,
        export_root=tmp_path / "phase_1333_export",
    )

    text = render_execution_gate_markdown(manifest)

    assert "# ILC Source Allowlist Export Execution Gate 1333 v0.1" in text
    assert "Publication:** not authorized" in text
    assert "Public RC:** remains blocked" in text
    assert "no_public_repository_publication" in manifest["non_claims"]
