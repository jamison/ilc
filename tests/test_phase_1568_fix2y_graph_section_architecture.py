from __future__ import annotations

import importlib.util
from pathlib import Path

from ilc_core.ledger.fix2s_activation_packet_verifier import (
    REQUIRED_ROLLBACK_STEP_COUNT,
    verify_activation_packet,
)


ROOT = Path(__file__).resolve().parents[1]
GRAPH_SPEC = ROOT / "docs/specs/ilc_graph_section_architecture_v0.1.md"
PRIVATE_POLICY = ROOT / "docs/specs/ilc_private_layer_policy_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
FIX2S_TEST = ROOT / "tests/test_phase_1568_fix2s_activation_packet_verifier.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _fix2s_fixture_packet() -> dict:
    spec = importlib.util.spec_from_file_location("fix2s_fixture_module", FIX2S_TEST)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._packet()


def test_graph_section_spec_declares_public_rc_exclusion_and_non_activation() -> None:
    text = _read(GRAPH_SPEC)

    assert "PUBLIC_RC_EXCLUDE: block6_graph_section_architecture_spec" in text
    assert "Runtime effect:** none" in text
    assert "This specification defines names and schemas only" in text
    assert "Activate public P2P or public RC" in text


def test_graph_section_spec_has_required_sections() -> None:
    text = _read(GRAPH_SPEC)

    for section_number in range(1, 10):
        assert f"## Section {section_number} -" in text

    assert "A graph section is a named geometric region" in text
    assert "Every node is classified independently on three axes" in text


def test_graph_section_labels_and_artifact_names_are_defined() -> None:
    text = _read(GRAPH_SPEC)

    for label in (
        "genesis_core_star_map",
        "public_protocol_graph",
        "support_candidate_graph",
        "excluded_private_material",
        "review_required",
    ):
        assert label in text

    for artifact in (
        "ilc_star_map_authority_core_v<N>.<M>.json",
        "ilc_slice_authority_core_v<N>.<M>.lmdb",
        "ilc_star_map_public_implementation_v<N>.<M>.json",
        "ilc_slice_public_support_v<N>.<M>.lmdb",
        "ilc_star_map_private_<name>_v<N>.<M>.json",
    ):
        assert artifact in text


def test_atlas_slice_manifest_schema_fields_are_defined() -> None:
    text = _read(GRAPH_SPEC)

    for field in (
        "slice_id",
        "slice_version",
        "section_label",
        "source_lmdb_root_sha256",
        "projection_filter",
        "root_pointers",
        "included_node_merkle_root",
        "cross_section_ref_count",
        "exclusion_policy",
        "semantic_loss_annotations",
        "privacy_budget",
        "installer_profile",
        "receipt_sha256",
        "signature",
    ):
        assert f'"{field}"' in text

    assert "`public`" in text
    assert "`local_only`" in text
    assert "`owner_signed`" in text


def test_cross_section_ref_edge_schema_and_private_stub_boundary() -> None:
    text = _read(GRAPH_SPEC)

    for field in (
        '"edge_type": "CROSS_SECTION_REF"',
        "source_node_cid",
        "source_section",
        "target_node_cid",
        "target_section",
        "resolved_in_section",
        "stub",
    ):
        assert field in text

    assert "public-to-private reference is forbidden" in text
    assert "not authority to invent target content" in text


def test_star_map_and_slice_manifest_are_distinct_artifact_types() -> None:
    text = _read(GRAPH_SPEC)

    assert "A star map is an advisory navigation result under ADR-0033" in text
    assert "An `AtlasSliceManifest` is an install and hydration receipt" in text
    assert "does not replace signed graph nodes" in text


def test_private_layer_policy_locks_excluded_material_out_of_public_export() -> None:
    text = _read(PRIVATE_POLICY)

    assert "PUBLIC_RC_EXCLUDE: block6_private_layer_policy" in text
    assert "`excluded_private_material` is local-only" in text
    assert "No public star map may include `excluded_private_material`" in text
    assert "No public LMDB slice manifest may include `excluded_private_material`" in text
    assert "No public RC export may include `excluded_private_material`" in text
    assert "No public `CROSS_SECTION_REF` stub may point" in text
    assert "Absence of `PUBLIC_RC_EXCLUDE` markup is not an allowlist grant" in text


def test_private_layer_policy_permits_only_owner_controlled_local_uses() -> None:
    text = _read(PRIVATE_POLICY)

    for permitted in (
        "Local Atlas search and orientation",
        "Owner-authorized private slices",
        "Private-to-public references",
        "Local MemPalace",
    ):
        assert permitted in text

    assert "Private material can inform operator judgment" in text
    assert "public protocol claims must stand on public" in text


def test_fix2s_rollback_step_gap_is_closed_by_existing_verifier() -> None:
    assert REQUIRED_ROLLBACK_STEP_COUNT == 7

    packet = _fix2s_fixture_packet()
    rollback_protocol = packet["rollback_protocol"]
    assert rollback_protocol["minimum_step_count"] == REQUIRED_ROLLBACK_STEP_COUNT
    assert len(rollback_protocol["ordered_steps"]) == REQUIRED_ROLLBACK_STEP_COUNT

    shortened_packet = _fix2s_fixture_packet()
    shortened_packet["rollback_protocol"]["ordered_steps"] = [
        "stop services",
        "export hashes",
        "destroy scratch state",
        "run atlas validation",
    ]

    result = verify_activation_packet(shortened_packet)
    assert result == {
        "ok": False,
        "reason": "rollback_protocol_ordered_steps_below_minimum",
    }


def test_fix2y_status_tokens_recorded() -> None:
    text = _read(STATUS)

    for token in (
        "phase_1568_fix2y_graph_section_architecture_spec_committed",
        "phase_1568_fix2y_private_layer_policy_committed",
        "phase_1568_fix2y_fix2s_rollback_step_gap_closed",
        "phase_1568_fix2y_cross_section_ref_edge_type_defined",
        "phase_1568_fix2y_atlas_slice_manifest_schema_defined",
        "phase_1568_fix2y_no_runtime_activation",
        "public_path_remains_blocked_phase_1568_fix2y",
    ):
        assert token in text

