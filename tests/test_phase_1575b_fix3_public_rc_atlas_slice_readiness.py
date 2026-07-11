from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ilc_core.bundle.atlas_slice_manifest import (
    manifest_from_json_dict,
    verify_atlas_slice_manifest,
)


FIXTURE_DIR = Path("tests/fixtures/starmap")
CORE_FIXTURE = FIXTURE_DIR / "core_public_rc_slice_fixture.json"
ECONOMIC_FIXTURE = FIXTURE_DIR / "economic_soft_rc_slice_fixture.json"

ALLOWED_ORIGIN_MODES = {
    "truth_primitive_submission",
    "cdl_ratified_definition",
    "adr_authority",
    "atlas_manual_intake",
    "repo_file_materialization",
    "generated_evidence",
    "slice_manifest_materialization",
}

ALLOWED_RECIPE_STATUS = {
    "irreducible_primitive",
    "composed_governance_recipe",
    "explicit_exemption",
}

PUBLIC_EXPORT_CATEGORIES = {"public"}
PRIVATE_MARKERS = {
    "PUBLIC_RC_EXCLUDE",
    "excluded_private_material",
    "genesis_private_material",
    "Z_Past_Chats",
    ".gemini",
    ".codex/attachments",
}


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _entries(payload: dict[str, Any]) -> list[dict[str, Any]]:
    entries = payload["content_entries"]
    assert isinstance(entries, list)
    return entries


def _assert_canonical_file(path: Path) -> None:
    payload = _load(path)
    expected = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    assert path.read_text(encoding="utf-8") == expected


def test_phase_1575b_fix3_fixtures_are_manifest_parseable_and_unsigned() -> None:
    for path in (CORE_FIXTURE, ECONOMIC_FIXTURE):
        manifest = manifest_from_json_dict(_load(path))
        assert verify_atlas_slice_manifest(manifest, require_signature=False)
        assert manifest.cose_sign1 == b""
        assert manifest.dev_signed is False
        assert manifest.public_rc_exclude is True
        assert "unsigned_test_fixture_not_publication_artifact" in manifest.semantic_loss_annotations


def test_phase_1575b_fix3_fixtures_are_canonical_json() -> None:
    _assert_canonical_file(CORE_FIXTURE)
    _assert_canonical_file(ECONOMIC_FIXTURE)


def test_phase_1575b_fix3_fixtures_exclude_private_material_markers() -> None:
    for path in (CORE_FIXTURE, ECONOMIC_FIXTURE):
        text = path.read_text(encoding="utf-8")
        assert "PUBLIC_RC_EXCLUDE" not in text
        for entry in _entries(_load(path)):
            serialized_entry = json.dumps(entry, sort_keys=True)
            for marker in PRIVATE_MARKERS - {"PUBLIC_RC_EXCLUDE"}:
                assert marker not in serialized_entry
            assert entry["export_category"] in PUBLIC_EXPORT_CATEGORIES
            assert entry["graph_projection"] != "excluded_private_material"


def test_phase_1575b_fix3_every_entry_has_origin_authority_hash_and_recipe() -> None:
    for path in (CORE_FIXTURE, ECONOMIC_FIXTURE):
        for entry in _entries(_load(path)):
            assert entry["origin_mode"] in ALLOWED_ORIGIN_MODES
            assert isinstance(entry["authority_source"], str) and entry["authority_source"]
            assert entry["export_category"] == "public"
            assert isinstance(entry["record_sha256"], str)
            assert len(entry["record_sha256"]) == 64
            assert set(entry["record_sha256"]) <= set("0123456789abcdef")
            assert entry["recipe_status"] in ALLOWED_RECIPE_STATUS
            if entry["recipe_status"] == "explicit_exemption":
                assert isinstance(entry.get("recipe_exemption"), str)
                assert entry["recipe_exemption"]


def test_phase_1575b_fix3_core_slice_records_required_origin_modes() -> None:
    origins = {entry["origin_mode"] for entry in _entries(_load(CORE_FIXTURE))}
    assert "cdl_ratified_definition" in origins
    assert "adr_authority" in origins
    assert "atlas_manual_intake" in origins
    assert "repo_file_materialization" in origins


def test_phase_1575b_fix3_commit_epoch_is_consensus_layer_exemption() -> None:
    entries = {
        entry["node_id"]: entry
        for entry in _entries(_load(CORE_FIXTURE))
    }
    commit_epoch = entries["truth_primitive:commit.epoch"]
    assert commit_epoch["recipe_status"] == "explicit_exemption"
    assert commit_epoch["recipe_exemption"] == "consensus_layer_only_not_agent_issuable"
    assert commit_epoch["edge_types"] == ["finalizes"]


def test_phase_1575b_fix3_economic_slice_is_not_activation_certificate() -> None:
    payload = _load(ECONOMIC_FIXTURE)
    manifest = manifest_from_json_dict(payload)
    assert manifest.section_label == "bridge"
    assert manifest.projection_filter == "economic_soft_rc_slice"
    assert "fixture_waits_for_sensitive_1575b_activation_certificate" in manifest.semantic_loss_annotations
    assert any(
        entry["recipe_exemption"] == "placeholder_waits_for_sensitive_1575b_certificate"
        for entry in _entries(payload)
        if entry["recipe_status"] == "explicit_exemption"
    )


def test_phase_1575b_fix3_cross_section_ref_count_is_integer_not_bool() -> None:
    payload = _load(ECONOMIC_FIXTURE)
    assert payload["cross_section_ref_count"] == 2
    payload["cross_section_ref_count"] = True
    try:
        manifest_from_json_dict(payload)
    except ValueError as exc:
        assert str(exc) == "atlas_slice_manifest_cross_section_ref_count_invalid"
    else:
        raise AssertionError("bool cross_section_ref_count was accepted")
