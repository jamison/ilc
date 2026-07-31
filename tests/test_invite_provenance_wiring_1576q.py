# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1576q invite provenance edge wiring tests."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.economics.backward_attribution_traversal import (
    BackwardAttributionTraversal,
)
from ilc_core.genesis.invitation_provenance_record import (
    build_invite_batch_record,
    build_invite_redemption_record,
    derive_agent_id_from_identity_seed,
)
from ilc_core.genesis.invite_provenance_wiring import (
    INVITE_CREDIT_MODEL,
    INVITE_PROVENANCE_EDGE_TYPE,
    INVITE_PROVENANCE_NO_ACTIVATION,
    INVITE_PROVENANCE_OUTPUT_TOKEN,
    INVITE_PROVENANCE_SUBTYPE,
    INVITE_PROVENANCE_WIRING_VERSION,
    InviteProvenanceWiringError,
    build_invite_provenance_edge_from_redemption,
    build_invite_provenance_edge_record,
    write_invite_provenance_edge,
)
from ilc_core.sidecars.openclaw_invite_bootstrap import (
    InviteNullifierStore,
    build_synthetic_invite_bundle,
    derive_redemption_nullifier,
    verify_invite_bootstrap,
)


AGENT_A = "a" * 96
AGENT_B = "b" * 96
IDENTITY_SEED_HEX = "22" * 32
REDEEMER_AGENT_ID = derive_agent_id_from_identity_seed(IDENTITY_SEED_HEX)
NULLIFIER = "1" * 64
PROFILE = "openclaw_public_rc_bootstrap"


class PutEdgesWriter:
    def __init__(self) -> None:
        self.edges: list[dict[str, object]] = []

    def put_edges(self, edges: list[dict[str, object]]) -> None:
        self.edges.extend(edges)


class ApplyPlanWriter:
    def __init__(self) -> None:
        self.plan = None

    def apply_plan(self, plan: object) -> dict[str, object]:
        self.plan = plan
        return {
            "accepted_edge_count": len(plan.edges_to_add),  # type: ignore[attr-defined]
            "status": "PASS",
        }


class FailingWriter:
    def put_edges(self, edges: list[dict[str, object]]) -> None:
        raise ValueError("atlas_writer_validation_failed")


def _redemption():
    batch, private_nonces = build_invite_batch_record(
        inviter_cid="inviter-node",
        batch_id="batch-1576q",
        count=1,
        created_epoch=0,
        inviter_sig="genesis",
        nonces=(bytes.fromhex("11" * 32),),
    )
    return build_invite_redemption_record(
        batch=batch,
        nonce=private_nonces[0],
        nonce_membership_proof=(),
        redeemer_pubkey_cid="pubkey:redeemer",
        identity_seed=IDENTITY_SEED_HEX,
        redemption_epoch=0,
    )


def _record():
    return build_invite_provenance_edge_record(
        source_node_id="redeemer-init-node",
        target_node_id="inviter-node",
        redemption_nullifier=NULLIFIER,
        batch_id="batch-1576q",
        inviter_cid="inviter-node",
        redeemer_agent_id=REDEEMER_AGENT_ID,
        redemption_epoch=0,
    )


def test_edge_record_is_deterministic_and_declares_no_fixed_fraction() -> None:
    first = _record()
    second = _record()
    payload = first.to_dict()

    assert first.canonical_json() == second.canonical_json()
    assert json.loads(first.canonical_json()) == payload
    assert payload["schema_version"] == INVITE_PROVENANCE_WIRING_VERSION
    assert payload["edge_type"] == INVITE_PROVENANCE_EDGE_TYPE
    assert payload["provenance_subtype"] == INVITE_PROVENANCE_SUBTYPE
    assert payload["invite_credit_model"] == INVITE_CREDIT_MODEL
    assert payload["no_fixed_invite_fraction"] is True
    assert payload["no_cdl084_explicit_chain_settlement"] is True
    assert payload["non_recursive_invite_credit"] is True
    assert len(first.record_hash()) == 64


def test_record_from_invite_redemption_uses_inviter_cid_as_default_target() -> None:
    redemption = _redemption()

    record = build_invite_provenance_edge_from_redemption(
        redemption,
        source_node_id="redeemer-init-node",
    )

    assert record.target_node_id == redemption.inviter_cid
    assert record.redemption_nullifier == redemption.redemption_nullifier
    assert record.batch_id == redemption.batch_id
    assert record.redeemer_agent_id == redemption.redeemer_agent_id


def test_invalid_or_self_edges_fail_closed() -> None:
    with pytest.raises(InviteProvenanceWiringError, match="invite_provenance_redemption_nullifier_invalid"):
        build_invite_provenance_edge_record(
            source_node_id="redeemer-init-node",
            target_node_id="inviter-node",
            redemption_nullifier="A" * 64,
            batch_id="batch-1576q",
            inviter_cid="inviter-node",
            redeemer_agent_id=REDEEMER_AGENT_ID,
            redemption_epoch=0,
        )

    with pytest.raises(InviteProvenanceWiringError, match="invite_provenance_self_edge_rejected"):
        build_invite_provenance_edge_record(
            source_node_id="same-node",
            target_node_id="same-node",
            redemption_nullifier=NULLIFIER,
            batch_id="batch-1576q",
            inviter_cid="same-node",
            redeemer_agent_id=REDEEMER_AGENT_ID,
            redemption_epoch=0,
        )


def test_writer_put_edges_receives_atlas_provenance_edge() -> None:
    writer = PutEdgesWriter()
    record = _record()

    receipt = write_invite_provenance_edge(record, writer)

    assert receipt["write_method"] == "put_edges"
    assert receipt["no_credit_computed"] is True
    assert receipt["no_settlement_activated"] is True
    assert writer.edges == [record.to_atlas_edge()]
    assert writer.edges[0]["edge_type"] == "PROVENANCE"
    assert writer.edges[0]["metadata"]["invite_credit_model"] == INVITE_CREDIT_MODEL  # type: ignore[index]


def test_writer_apply_plan_receives_non_dry_run_edge_plan() -> None:
    writer = ApplyPlanWriter()
    record = _record()

    receipt = write_invite_provenance_edge(record, writer)

    assert receipt["write_method"] == "apply_plan"
    assert receipt["writer_receipt"] == {"accepted_edge_count": 1, "status": "PASS"}
    assert writer.plan is not None
    assert writer.plan.dry_run is False
    assert writer.plan.phase == "1576q"
    assert writer.plan.edges_to_add == [record.to_atlas_edge()]


def test_edge_record_feeds_backward_attribution_traversal_without_fixed_credit() -> None:
    record = _record()
    traversal = BackwardAttributionTraversal(
        {
            "redeemer-init-node": {
                "artifact_type": "claim",
                "created_epoch": 0,
                "novelty_score": "1",
                "recipient_agent_id": AGENT_B,
                "status_quality_weight": "1",
            },
            "inviter-node": {
                "artifact_type": "claim",
                "created_epoch": 0,
                "novelty_score": "1",
                "recipient_agent_id": AGENT_A,
                "status_quality_weight": "1",
            },
        },
        [record.to_backward_attribution_edge()],
    )

    result = traversal.traverse(
        "redeemer-init-node",
        event_id="invite-init-event",
        event_budget_ecu=Decimal("100"),
        event_epoch=0,
        apply_antigaming_caps=True,
    )

    assert result.final_credits[0].recipient_agent_id == AGENT_A
    assert result.final_credits[0].upstream_artifact_id == "inviter-node"
    assert result.final_credits[0].final_credit_ecu == result.node_cap_amount_ecu
    assert result.final_credits[0].final_credit_ecu != Decimal("100")


def test_openclaw_defers_edge_when_writer_present_but_init_node_missing(tmp_path: Path) -> None:
    writer = PutEdgesWriter()
    bundle = build_synthetic_invite_bundle(intended_profile=PROFILE)
    bundle["redeemer_agent_id"] = REDEEMER_AGENT_ID

    decision = verify_invite_bootstrap(
        bundle,
        expected_profile=PROFILE,
        current_epoch=0,
        nullifier_store=InviteNullifierStore(tmp_path / "nullifiers.json"),
        invite_provenance_atlas_writer=writer,
    )

    assert decision.bootstrap_allowed is True
    assert decision.invite_provenance_edge_status == "deferred_redeemer_init_node_required"
    assert decision.invite_provenance_edge is None
    assert writer.edges == []


def test_openclaw_writes_invite_provenance_edge_when_configured(tmp_path: Path) -> None:
    writer = PutEdgesWriter()
    bundle = build_synthetic_invite_bundle(intended_profile=PROFILE)
    bundle["redeemer_agent_id"] = REDEEMER_AGENT_ID
    nullifier = derive_redemption_nullifier(
        "openclaw-fix2d-batch",
        str(bundle["private_invite_nonce"]),
    )

    decision = verify_invite_bootstrap(
        bundle,
        expected_profile=PROFILE,
        current_epoch=0,
        nullifier_store=InviteNullifierStore(tmp_path / "nullifiers.json"),
        invite_provenance_atlas_writer=writer,
        invite_provenance_source_node_id="redeemer-init-node",
    )

    assert decision.bootstrap_allowed is True
    assert decision.invite_provenance_edge_status == "written"
    assert decision.invite_provenance_edge is not None
    assert decision.invite_provenance_edge["redemption_nullifier"] == nullifier
    assert decision.invite_provenance_write_receipt is not None
    assert decision.invite_provenance_write_receipt["write_method"] == "put_edges"
    assert writer.edges[0]["source"] == "redeemer-init-node"
    assert writer.edges[0]["target"] == "genesis_agent:01"


def test_openclaw_reports_edge_write_failure_without_malformed_invite(tmp_path: Path) -> None:
    bundle = build_synthetic_invite_bundle(intended_profile=PROFILE)
    bundle["redeemer_agent_id"] = REDEEMER_AGENT_ID

    decision = verify_invite_bootstrap(
        bundle,
        expected_profile=PROFILE,
        current_epoch=0,
        nullifier_store=InviteNullifierStore(tmp_path / "nullifiers.json"),
        invite_provenance_atlas_writer=FailingWriter(),
        invite_provenance_source_node_id="redeemer-init-node",
    )

    assert decision.bootstrap_allowed is True
    assert decision.defect_token == "invite_signature_authority_gap_recorded_phase_1575b_fix2d"
    assert decision.invite_provenance_edge_status == "write_failed:ValueError"
    assert decision.invite_provenance_edge is None
    assert decision.invite_provenance_write_receipt is None


def test_no_settlement_activation_or_compute_inviter_credit_surface() -> None:
    import ilc_core.genesis.invite_provenance_wiring as wiring

    assert INVITE_PROVENANCE_NO_ACTIVATION == "no_invite_ecu_settlement_activation_phase_1576q"
    assert INVITE_PROVENANCE_OUTPUT_TOKEN == "invite_ecu_credit_runtime_committed_phase_1576q"
    assert not hasattr(wiring, "compute_inviter_ecu_credit")
