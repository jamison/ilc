from __future__ import annotations

import json
from pathlib import Path

import pytest

from ilc_core.rc.release_key_envelope_rehearsal import (
    DRY_RUN_DIGEST_PLACEHOLDER,
    DRY_RUN_ENVELOPE_ID,
    DRY_RUN_KEY_ID,
    DRY_RUN_PUBLIC_KEY_PLACEHOLDER,
    DRY_RUN_SIGNATURE_PLACEHOLDER,
    PHASE_1322_NEXT_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1321_TOKEN,
    RELEASE_ENVELOPE_PRODUCTION_NOT_AUTHORIZED_TOKEN,
    RELEASE_KEY_ENVELOPE_REHEARSAL_VERSION,
    RELEASE_KEY_GENERATION_NOT_AUTHORIZED_TOKEN,
    SIGNING_PROCEDURE_REHEARSED_NO_REAL_SIGNING_TOKEN,
    build_release_key_envelope_rehearsal,
    canonical_release_key_envelope_rehearsal_json,
    manifest_hash,
    phase_1321_required_tokens,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = (
    ROOT / "docs/specs/ilc_release_key_envelope_procedure_rehearsal_1321_v0.1.json"
)
REPORT_MD = (
    ROOT / "docs/specs/ilc_release_key_envelope_procedure_rehearsal_1321_v0.1.md"
)
WALKTHROUGH = (
    ROOT / "docs/phases/phase_1321_release_key_envelope_procedure_rehearsal_walkthrough.md"
)
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING = ROOT / "docs/PLANNING_INDEX.md"
CAPSULE = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.54.md"
PHASE_1320 = (
    ROOT / "docs/specs/ilc_release_artifact_manifest_instance_rehearsal_1320_v0.1.json"
)
ADR_0036 = ROOT / "docs/adr/ADR_0036_Operational_Release_Key_Genesis_Binding.md"
PHASE_1287 = (
    ROOT / "docs/specs/ilc_release_publication_signing_authorization_preflight_1287_v0.1.md"
)
ATLAS_009 = ROOT / "docs/antigravity_tasks/antigravity_prompt__atlas_g_009_signing_root_envelope_prep.md"
ATLAS_010 = ROOT / "docs/antigravity_tasks/antigravity_prompt__atlas_g_010_v0_2_signing_ceremony.md"
FORWARD_PLAN = (
    ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.1.md"
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _seed_inputs(tmp_path: Path) -> None:
    for source in (PHASE_1320, ADR_0036, PHASE_1287, ATLAS_009, ATLAS_010, FORWARD_PLAN):
        _write(tmp_path / source.relative_to(ROOT), source.read_text(encoding="utf-8"))


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


def test_phase_1321_current_repo_rehearsal_passes_and_is_canonical() -> None:
    manifest = build_release_key_envelope_rehearsal(repo_root=ROOT)
    encoded_once = canonical_release_key_envelope_rehearsal_json(manifest)
    encoded_twice = canonical_release_key_envelope_rehearsal_json(
        build_release_key_envelope_rehearsal(repo_root=ROOT)
    )

    assert encoded_once == encoded_twice
    assert encoded_once == json.dumps(
        json.loads(encoded_once),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    assert manifest["schema_version"] == RELEASE_KEY_ENVELOPE_REHEARSAL_VERSION
    assert manifest["required_tokens"] == phase_1321_required_tokens()
    assert manifest["result"] == "pass"
    assert manifest["mode"] == "dry_run_rehearsal_only"
    assert manifest["public_rc_remains_blocked"] is True
    assert manifest["phase_1320_rehearsal_input"]["result"] == "pass"
    assert manifest["authority_boundary"]["phase_1321_satisfies_future_authority_checkpoint"] is False
    assert manifest["signing_gate_context"]["phase_1321_satisfies_atlas_g_009"] is False
    assert manifest["signing_gate_context"]["phase_1321_satisfies_atlas_g_010"] is False
    assert manifest["credential_observation_policy"]["credential_like_environment_values_read"] is False
    assert manifest["credential_observation_policy"]["operator_key_paths_read"] == []
    assert manifest["procedure"]["signing_binaries_called"] == []
    assert manifest_hash(manifest) != manifest["hash_algorithm"][
        "phase_1321_rehearsal_manifest_hash"
    ]


def test_phase_1321_checked_in_report_matches_current_rehearsal() -> None:
    report = _load_report()
    current = build_release_key_envelope_rehearsal(repo_root=ROOT)

    assert report == current
    assert REPORT_MD.read_text(encoding="utf-8").startswith(
        "# ILC Release Key Envelope Procedure Rehearsal 1321 v0.1"
    )


def test_phase_1321_dummy_identifiers_cannot_be_real_key_envelope_or_signature() -> None:
    manifest = build_release_key_envelope_rehearsal(repo_root=ROOT)
    dummy = manifest["dry_run_envelope_shape"]

    assert dummy["dry_run_release_key_id"] == DRY_RUN_KEY_ID
    assert dummy["dry_run_envelope_id"] == DRY_RUN_ENVELOPE_ID
    assert dummy["public_key_placeholder"] == DRY_RUN_PUBLIC_KEY_PLACEHOLDER
    assert dummy["signed_payload_digest_placeholder"] == DRY_RUN_DIGEST_PLACEHOLDER
    assert dummy["signature_placeholder"] == DRY_RUN_SIGNATURE_PLACEHOLDER
    assert not dummy["signed_payload_digest_placeholder"].startswith("sha256:")
    assert dummy["signing_status"] == "not_signed_rehearsal_only"


def test_phase_1321_future_real_ceremony_inventory_proves_no_outputs() -> None:
    manifest = build_release_key_envelope_rehearsal(repo_root=ROOT)
    inventory = manifest["procedure"]["future_real_ceremony_file_inventory"]

    assert inventory
    assert all(item["produced_in_phase_1321"] is False for item in inventory)
    assert all(item["path"] is None for item in inventory)
    assert all(item["status"] == "not_produced_dry_run_only" for item in inventory)


def test_phase_1321_machine_content_has_no_current_timestamp_fields() -> None:
    manifest = build_release_key_envelope_rehearsal(repo_root=ROOT)
    forbidden = {"timestamp", "created_at", "updated_at", "generated_at", "now"}

    assert not forbidden.intersection(str(value) for value in _walk_values(manifest))
    assert manifest["hash_algorithm"]["machine_content_must_not_include_current_timestamps"]


def test_phase_1321_phase_1320_non_pass_report_fails_closed(tmp_path: Path) -> None:
    _seed_inputs(tmp_path)
    report_path = tmp_path / PHASE_1320.relative_to(ROOT)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["result"] = "fail_closed"
    report_path.write_text(json.dumps(report, sort_keys=True), encoding="utf-8")

    with pytest.raises(ValueError, match="phase_1320_rehearsal_must_pass"):
        build_release_key_envelope_rehearsal(repo_root=tmp_path)


def test_phase_1321_phase_1320_artifact_paths_fail_closed(tmp_path: Path) -> None:
    _seed_inputs(tmp_path)
    report_path = tmp_path / PHASE_1320.relative_to(ROOT)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["negative_evidence"]["generated_release_artifact_paths"] = [
        "dist/ilc-test.tar.gz"
    ]
    report_path.write_text(json.dumps(report, sort_keys=True), encoding="utf-8")

    with pytest.raises(ValueError, match="phase_1320_artifact_paths_must_be_empty"):
        build_release_key_envelope_rehearsal(repo_root=tmp_path)


def test_phase_1321_adr_0036_missing_authority_phrase_fails_closed(tmp_path: Path) -> None:
    _seed_inputs(tmp_path)
    adr_path = tmp_path / ADR_0036.relative_to(ROOT)
    adr_path.write_text(
        adr_path.read_text(encoding="utf-8")
        .replace("It does not create the key", "TEST_REMOVED_KEY_BOUNDARY")
        .replace("authorize any signing ceremony", "TEST_REMOVED_SIGNING_BOUNDARY"),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="adr_0036_required_phrase_missing"):
        build_release_key_envelope_rehearsal(repo_root=tmp_path)


def test_phase_1321_path_traversal_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="phase_1320_report_path_traversal_rejected"):
        build_release_key_envelope_rehearsal(
            repo_root=tmp_path,
            phase_1320_report_path="../escape.json",
        )


def test_phase_1321_status_planning_capsule_and_walkthrough_record_required_tokens() -> None:
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (REPORT_MD, WALKTHROUGH, STATUS, PLANNING, CAPSULE)
    )
    for token in (
        RELEASE_KEY_ENVELOPE_REHEARSAL_VERSION,
        RELEASE_KEY_GENERATION_NOT_AUTHORIZED_TOKEN,
        RELEASE_ENVELOPE_PRODUCTION_NOT_AUTHORIZED_TOKEN,
        SIGNING_PROCEDURE_REHEARSED_NO_REAL_SIGNING_TOKEN,
        PHASE_1322_NEXT_TOKEN,
        PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1321_TOKEN,
    ):
        assert token in text
