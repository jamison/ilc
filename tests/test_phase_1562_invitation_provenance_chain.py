"""Phase 1562 invitation provenance chain evidence tests.

PUBLIC_RC_EXCLUDE: phase_1562_private_invitation_provenance_selftest
PUBLIC_RC_EXCLUDE_REASON: Private pre-RC invitation provenance evidence validation. Does not activate invitation economics or public serving.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ilc_core.genesis.invitation_provenance_record import (
    INVITATION_PROVENANCE_RUNTIME_VERSION,
    InvitationProvenanceError,
    InvitationProvenanceRecord,
    build_invitation_record,
    invitation_record_from_dict,
    verify_chain_depth,
    verify_record_hash,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out/invitation_provenance"
RECORD_FILES = [
    OUT / "genesis_to_ilc_node_2_validator_a1_1562.json",
    OUT / "genesis_to_ilc_node_2_validator_a2_1562.json",
    OUT / "genesis_to_ilc_node_3_validator_b1_1562.json",
    OUT / "genesis_to_ilc_node_3_validator_b2_1562.json",
]
NODE6_BOUNDARY = OUT / "node6_receiver_only_boundary_1562.json"


def _load(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _records() -> list[InvitationProvenanceRecord]:
    return [invitation_record_from_dict(_load(path)) for path in RECORD_FILES]


def test_build_and_verify_depth_one_record_hash_round_trip() -> None:
    record = build_invitation_record(
        "genesis_agent:01",
        "agent_fixture_01",
        "serving_receipt:fixture",
        timestamp_epoch=0,
    )

    assert record.invite_depth == 1
    assert record.parent_invite_id is None
    assert record.invite_id == record.record_hash
    assert verify_record_hash(record) is True
    assert verify_chain_depth([record]) is True


def test_invite_depth_is_not_user_supplied_to_builder() -> None:
    with pytest.raises(TypeError):
        build_invitation_record(  # type: ignore[call-arg]
            "genesis_agent:01",
            "agent_fixture_01",
            "serving_receipt:fixture",
            timestamp_epoch=0,
            invite_depth=2,
        )


def test_nested_parent_context_fails_closed_in_phase_1562_builder() -> None:
    with pytest.raises(InvitationProvenanceError, match="parent_context_required"):
        build_invitation_record(
            "agent_a",
            "agent_b",
            "serving_receipt:nested",
            timestamp_epoch=0,
            parent_invite_id="a" * 64,
        )


def test_cycle_detection_raises_machine_token() -> None:
    record_a = InvitationProvenanceRecord(
        invite_id="a" * 64,
        inviter_agent_id="agent_a",
        invitee_agent_id="agent_b",
        serving_receipt_id="serving_receipt:a",
        invite_depth=2,
        timestamp_epoch=0,
        record_hash="a" * 64,
        rule_version=INVITATION_PROVENANCE_RUNTIME_VERSION,
        parent_invite_id="b" * 64,
    )
    record_b = InvitationProvenanceRecord(
        invite_id="b" * 64,
        inviter_agent_id="agent_b",
        invitee_agent_id="agent_c",
        serving_receipt_id="serving_receipt:b",
        invite_depth=2,
        timestamp_epoch=0,
        record_hash="b" * 64,
        rule_version=INVITATION_PROVENANCE_RUNTIME_VERSION,
        parent_invite_id="a" * 64,
    )

    with pytest.raises(InvitationProvenanceError, match="cycle_detected"):
        verify_chain_depth([record_a, record_b])


def test_inconsistent_depth_rejected_without_exception() -> None:
    record = InvitationProvenanceRecord(
        invite_id="c" * 64,
        inviter_agent_id="genesis_agent:01",
        invitee_agent_id="agent_c",
        serving_receipt_id="serving_receipt:c",
        invite_depth=2,
        timestamp_epoch=0,
        record_hash="c" * 64,
        rule_version=INVITATION_PROVENANCE_RUNTIME_VERSION,
        parent_invite_id=None,
    )

    assert verify_chain_depth([record]) is False


def test_phase_1562_output_files_exist_and_node6_boundary_is_explicit() -> None:
    for path in RECORD_FILES:
        assert path.exists(), path
    assert NODE6_BOUNDARY.exists()
    assert not (OUT / "genesis_to_vps_node6_1562.json").exists()

    boundary = _load(NODE6_BOUNDARY)
    assert boundary["receiver_only"] is True
    assert boundary["agents"] == []
    assert boundary["reason"] == "missing_invitee_agent_id_node6_receiver_only"
    assert boundary["no_invitation_provenance_record_created_phase_1562"] is True


def test_phase_1562_output_schema_no_floats_no_economics() -> None:
    forbidden = {"ecu_credit", "inviter_reward", "attribution_credit"}
    for path in RECORD_FILES:
        payload = _load(path)
        assert set(payload) == {
            "invite_depth",
            "invite_id",
            "invitee_agent_id",
            "inviter_agent_id",
            "parent_invite_id",
            "record_hash",
            "rule_version",
            "serving_receipt_id",
            "timestamp_epoch",
        }
        assert payload["invite_depth"] == 1
        assert payload["parent_invite_id"] is None
        assert payload["rule_version"] == INVITATION_PROVENANCE_RUNTIME_VERSION
        assert forbidden.isdisjoint(payload)
        assert all(not isinstance(value, float) for value in payload.values())


def test_phase_1562_records_verify_as_depth_one_chain() -> None:
    records = _records()

    assert len(records) == 4
    assert verify_chain_depth(records) is True
    assert {record.inviter_agent_id for record in records} == {"genesis_agent:01"}
    assert {record.invite_depth for record in records} == {1}
