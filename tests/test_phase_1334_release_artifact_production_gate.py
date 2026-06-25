import json
from pathlib import Path

import pytest

from ilc_core.rc import release_artifact_production_gate as gate


def _write_clean_export(tmp_path: Path) -> tuple[Path, list[dict[str, object]], str]:
    tree = tmp_path / "out/public_rc/source_allowlist_export_phase_1333/tree"
    (tree / "ilc_core").mkdir(parents=True)
    (tree / "README.md").write_text("ILC public export candidate\n", encoding="utf-8")
    (tree / "ilc_core/__init__.py").write_text("", encoding="utf-8")
    file_hashes = gate._hash_tree_files(tree)
    return tree, file_hashes, gate._tree_hash(file_hashes)


def _write_phase_1333_manifest(
    tmp_path: Path,
    *,
    marker_hits: int = 0,
    result: str = "executed_clean_export",
) -> Path:
    tree, file_hashes, tree_hash = _write_clean_export(tmp_path)
    manifest = {
        "candidate_scan": {
            "dependency_scan": {"stripped_helper_hit_count": 0},
            "legacy_untagged_review": {"ambiguity_count": 0},
            "marker_scan": {"hit_count": marker_hits},
        },
        "clean_materialized_public_tree_produced": result == "executed_clean_export",
        "dirty_worktree_policy": {"dirty_included_files": []},
        "export_materialization": {
            "exported_file_count": len(file_hashes),
            "file_hashes": file_hashes,
            "materialized": result == "executed_clean_export",
            "tree_path": tree.as_posix(),
            "tree_sha256": tree_hash,
        },
        "manifest_hash": "a" * 64,
        "result": result,
        "source_allowlist_export_execution_gate_verdict": (
            "source_allowlist_export_execution_gate_verdict=pass"
            if result == "executed_clean_export"
            else "source_allowlist_export_execution_gate_verdict=block"
        ),
    }
    path = tmp_path / gate.PHASE_1333_MANIFEST_PATH
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")
    return path


def test_phase_1334_produces_deterministic_unsigned_source_tarball(tmp_path: Path) -> None:
    _write_phase_1333_manifest(tmp_path)

    first = gate.build_release_artifact_production_gate(
        repo_root=tmp_path,
        artifact_root=Path("out/release_artifacts/phase_1334"),
    )
    second = gate.build_release_artifact_production_gate(
        repo_root=tmp_path,
        artifact_root=Path("out/release_artifacts/phase_1334"),
    )

    assert first["result"] == "artifacts_produced_unsigned"
    assert first["release_artifact_production_gate_verdict"] == (
        "release_artifact_production_gate_verdict=pass"
    )
    assert first["artifact_manifests"][0]["signing_status"] == "unsigned"
    assert first["artifact_manifests"][0]["artifact_type"] == "source_release_tarball"
    assert first["artifacts"][0]["canonical_hash"] == second["artifacts"][0]["canonical_hash"]
    assert first["signed"] is False
    assert first["public_rc_remains_blocked"] is True
    assert first["non_authorization_floor"]["signing_authorized"] is False


def test_phase_1334_blocks_when_phase_1333_marker_scan_is_not_clean(tmp_path: Path) -> None:
    _write_phase_1333_manifest(tmp_path, marker_hits=1)

    manifest = gate.build_release_artifact_production_gate(
        repo_root=tmp_path,
        artifact_root=Path("out/release_artifacts/phase_1334"),
    )

    assert manifest["result"] == "blocked_with_findings"
    assert manifest["artifact_manifests"] == []
    assert manifest["artifacts"] == []
    assert manifest["clean_source_export_dependency"]["dependency_result"] == "block"
    assert manifest["non_authorization_floor"][
        "release_artifact_production_authorized_by_go_phase_1334"
    ] is False


def test_phase_1334_rejects_phase_1333_tree_hash_drift(tmp_path: Path) -> None:
    _write_phase_1333_manifest(tmp_path)
    tree = tmp_path / "out/public_rc/source_allowlist_export_phase_1333/tree"
    (tree / "README.md").write_text("drifted\n", encoding="utf-8")

    with pytest.raises(ValueError, match="phase_1334_phase_1333_tree_hash_drift"):
        gate.build_release_artifact_production_gate(repo_root=tmp_path)


def test_phase_1213_artifact_manifest_shape_is_enforced() -> None:
    valid = {
        "artifact_id": "ilc-artifact:source-release-tarball@phase-1334",
        "artifact_type": "source_release_tarball",
        "canonical_hash": "sha256:" + "b" * 64,
        "lineage_reference": "genesis:v0.1",
        "produced_phase": 1334,
        "ratification_token": gate.RELEASE_ARTIFACT_PRODUCTION_GATE_VERSION,
        "signing_status": "unsigned",
    }
    assert gate.validate_phase_1213_artifact_manifest(valid) == valid

    invalid = dict(valid)
    invalid["canonical_hash"] = "sha512:" + "b" * 128
    with pytest.raises(ValueError, match="phase_1334_phase_1213_canonical_hash_invalid"):
        gate.validate_phase_1213_artifact_manifest(invalid)


def test_phase_1334_markdown_keeps_publication_and_signing_blocked(tmp_path: Path) -> None:
    _write_phase_1333_manifest(tmp_path)
    manifest = gate.build_release_artifact_production_gate(repo_root=tmp_path)

    markdown = gate.render_markdown_report(manifest)

    assert "does not generate release keys" in markdown
    assert "sign artifacts" in markdown
    assert "publish a repository or package" in markdown
    assert "claim public RC" in markdown
