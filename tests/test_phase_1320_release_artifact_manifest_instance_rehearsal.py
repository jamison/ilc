from __future__ import annotations

import json
from pathlib import Path

import pytest

from ilc_core.rc.release_artifact_manifest_rehearsal import (
    CLEAN_EXPORT_EVIDENCE_DEPENDENCY_RECORDED_TOKEN,
    PHASE_1321_NEXT_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1320_TOKEN,
    RELEASE_ARTIFACT_MANIFEST_REHEARSAL_VERSION,
    RELEASE_ARTIFACT_PRODUCTION_NOT_AUTHORIZED_TOKEN,
    RELEASE_MANIFEST_SHAPE_REHEARSED_TOKEN,
    build_release_artifact_manifest_rehearsal,
    canonical_release_artifact_manifest_rehearsal_json,
    manifest_hash,
    phase_1320_required_tokens,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = (
    ROOT / "docs/specs/ilc_release_artifact_manifest_instance_rehearsal_1320_v0.1.json"
)
REPORT_MD = (
    ROOT / "docs/specs/ilc_release_artifact_manifest_instance_rehearsal_1320_v0.1.md"
)
WALKTHROUGH = (
    ROOT
    / "docs/phases/phase_1320_release_artifact_manifest_instance_rehearsal_walkthrough.md"
)
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING = ROOT / "docs/PLANNING_INDEX.md"
CAPSULE = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.54.md"
SCHEMA = ROOT / "docs/specs/ilc_release_artifact_manifest_schema_1213_v0.1.md"
CHECKLIST = ROOT / "docs/specs/ilc_distribution_channel_integrity_checklist_1213_v0.1.md"
PHASE_1319 = (
    ROOT / "docs/specs/ilc_deterministic_source_allowlist_export_rehearsal_1319_v0.1.json"
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _seed_inputs(tmp_path: Path) -> None:
    _write(
        tmp_path / "docs/specs/ilc_release_artifact_manifest_schema_1213_v0.1.md",
        SCHEMA.read_text(encoding="utf-8"),
    )
    _write(
        tmp_path / "docs/specs/ilc_distribution_channel_integrity_checklist_1213_v0.1.md",
        CHECKLIST.read_text(encoding="utf-8"),
    )
    _write(
        tmp_path
        / "docs/specs/ilc_deterministic_source_allowlist_export_rehearsal_1319_v0.1.json",
        PHASE_1319.read_text(encoding="utf-8"),
    )


def _load_report() -> dict:
    return json.loads(REPORT_JSON.read_text(encoding="utf-8"))


def _walk_values(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _walk_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_values(item)
    else:
        yield value


def test_phase_1320_current_repo_rehearsal_passes_and_is_canonical() -> None:
    manifest = build_release_artifact_manifest_rehearsal(repo_root=ROOT)
    encoded_once = canonical_release_artifact_manifest_rehearsal_json(manifest)
    encoded_twice = canonical_release_artifact_manifest_rehearsal_json(
        build_release_artifact_manifest_rehearsal(repo_root=ROOT)
    )

    assert encoded_once == encoded_twice
    assert encoded_once == json.dumps(
        json.loads(encoded_once),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    assert manifest["schema_version"] == RELEASE_ARTIFACT_MANIFEST_REHEARSAL_VERSION
    assert manifest["required_tokens"] == phase_1320_required_tokens()
    assert manifest["result"] == "pass"
    assert manifest["mode"] == "dry_run_rehearsal_only"
    assert manifest["signed"] is False
    assert manifest["public_rc_remains_blocked"] is True
    assert manifest["source_tree_rehearsal_input"]["result"] == "pass"
    assert manifest["source_tree_rehearsal_input"]["counts"]["marker_hits"] == 0
    assert manifest["source_tree_rehearsal_input"]["counts"]["dependency_hits"] == 0
    assert manifest["negative_evidence"]["generated_release_artifact_paths"] == []
    assert manifest["negative_evidence"]["generated_release_checksum_paths"] == []
    assert manifest["negative_evidence"]["no_artifact_payloads_created"] is True
    assert manifest["negative_evidence"]["no_artifact_checksums_created"] is True
    assert manifest_hash(manifest) != manifest["hash_algorithm"][
        "phase_1320_rehearsal_manifest_hash"
    ]


def test_phase_1320_checked_in_report_matches_current_rehearsal() -> None:
    report = _load_report()
    current = build_release_artifact_manifest_rehearsal(repo_root=ROOT)

    assert report == current
    assert REPORT_MD.read_text(encoding="utf-8").startswith(
        "# ILC Release Artifact Manifest Instance Rehearsal 1320 v0.1"
    )


def test_phase_1320_dummy_placeholders_cannot_be_real_artifact_manifest_fields() -> None:
    manifest = build_release_artifact_manifest_rehearsal(repo_root=ROOT)
    dummy = manifest["artifact_manifest_shape"]["dry_run_placeholder_instance"]

    assert all(str(value).startswith("DRY_RUN_PLACEHOLDER_") for value in dummy.values())
    assert not dummy["canonical_hash"].startswith("sha256:")
    assert dummy["artifact_id"] != "ilc-artifact:source-release-tarball@phase-1320"
    assert dummy["artifact_type"] not in manifest["artifact_manifest_shape"][
        "allowed_artifact_types"
    ]
    assert dummy["produced_phase"] != 1320
    assert dummy["signing_status"] not in {"signed", "unsigned", "deferred"}


def test_phase_1320_machine_content_has_no_current_timestamp_fields() -> None:
    manifest = build_release_artifact_manifest_rehearsal(repo_root=ROOT)
    forbidden = {"timestamp", "created_at", "updated_at", "generated_at", "now"}

    assert not forbidden.intersection(str(value) for value in _walk_values(manifest))
    assert manifest["hash_algorithm"]["machine_content_must_not_include_current_timestamps"]


def test_phase_1320_phase_1213_schema_token_missing_fails_closed(tmp_path: Path) -> None:
    _seed_inputs(tmp_path)
    schema_path = tmp_path / "docs/specs/ilc_release_artifact_manifest_schema_1213_v0.1.md"
    schema_path.write_text(
        schema_path.read_text(encoding="utf-8").replace(
            "release_artifact_manifest_schema_committed_phase_1213",
            "release_artifact_manifest_schema_SUPERSEDED_TEST",
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="phase_1213_schema_token_missing"):
        build_release_artifact_manifest_rehearsal(repo_root=tmp_path)


def test_phase_1320_phase_1213_schema_artifact_type_drift_fails_closed(
    tmp_path: Path,
) -> None:
    _seed_inputs(tmp_path)
    schema_path = tmp_path / "docs/specs/ilc_release_artifact_manifest_schema_1213_v0.1.md"
    schema_path.write_text(
        schema_path.read_text(encoding="utf-8").replace(
            '"source_release_tarball"',
            '"source_release_zip"',
            1,
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="phase_1213_schema_artifact_types_invalid"):
        build_release_artifact_manifest_rehearsal(repo_root=tmp_path)


def test_phase_1320_phase_1319_non_pass_report_fails_closed(tmp_path: Path) -> None:
    _seed_inputs(tmp_path)
    report_path = (
        tmp_path
        / "docs/specs/ilc_deterministic_source_allowlist_export_rehearsal_1319_v0.1.json"
    )
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["result"] = "fail_closed"
    report_path.write_text(json.dumps(report, sort_keys=True), encoding="utf-8")

    with pytest.raises(ValueError, match="phase_1319_rehearsal_must_pass"):
        build_release_artifact_manifest_rehearsal(repo_root=tmp_path)


def test_phase_1320_phase_1319_marker_hit_report_fails_closed(tmp_path: Path) -> None:
    _seed_inputs(tmp_path)
    report_path = (
        tmp_path
        / "docs/specs/ilc_deterministic_source_allowlist_export_rehearsal_1319_v0.1.json"
    )
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["counts"]["marker_hits"] = 1
    report_path.write_text(json.dumps(report, sort_keys=True), encoding="utf-8")

    with pytest.raises(ValueError, match="phase_1319_clean_export_rehearsal_failed"):
        build_release_artifact_manifest_rehearsal(repo_root=tmp_path)


def test_phase_1320_path_traversal_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="release_schema_path_traversal_rejected"):
        build_release_artifact_manifest_rehearsal(
            repo_root=tmp_path,
            release_schema_path="../escape.md",
        )


def test_phase_1320_status_planning_capsule_and_walkthrough_record_required_tokens() -> None:
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (REPORT_MD, WALKTHROUGH, STATUS, PLANNING, CAPSULE)
    )
    for token in (
        RELEASE_ARTIFACT_MANIFEST_REHEARSAL_VERSION,
        RELEASE_MANIFEST_SHAPE_REHEARSED_TOKEN,
        RELEASE_ARTIFACT_PRODUCTION_NOT_AUTHORIZED_TOKEN,
        CLEAN_EXPORT_EVIDENCE_DEPENDENCY_RECORDED_TOKEN,
        PHASE_1321_NEXT_TOKEN,
        PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1320_TOKEN,
    ):
        assert token in text
