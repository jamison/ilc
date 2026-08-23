# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1576r invite-chain integration tests.

These tests exercise the multi-module path from invite batch creation through
redemption, nullifier replay prevention, D2D propagation, and invite-init
PROVENANCE edge creation. They do not activate invite enforcement globally.
"""

from __future__ import annotations

import hashlib
from typing import Any

import pytest

from ilc_core.genesis import invite_enforcement
from ilc_core.genesis.invitation_provenance_record import (
    INVITE_NONCE_LEAF_DOMAIN,
    INVITE_NONCE_NODE_DOMAIN,
    InvitationProvenanceError,
    build_invite_batch_record,
    build_invite_redemption_record,
    derive_agent_id_from_identity_seed,
    derive_invite_redemption_nullifier,
    verify_nonce_membership_proof,
)
from ilc_core.genesis.invite_nullifier_registry import InviteNullifierRegistry
from ilc_core.genesis import invite_provenance_wiring
from ilc_core.genesis.invite_provenance_wiring import (
    build_invite_provenance_edge_from_redemption,
    write_invite_provenance_edge,
)
from ilc_core.network.d2d.invite_nullifier_gossip import (
    build_nullifier_gossip_message,
    handle_nullifier_gossip_message,
)
from ilc_core.sidecars.openclaw_invite_bootstrap import verify_invite_bootstrap


PROFILE = "openclaw_public_rc_bootstrap"
INVITER_CID = "genesis_agent:01"
LEFT_NONCE = bytes.fromhex("11" * 32)
RIGHT_NONCE = bytes.fromhex("22" * 32)
LEFT_IDENTITY_SEED = bytes.fromhex("33" * 32)
RIGHT_IDENTITY_SEED = bytes.fromhex("44" * 32)
LEFT_AGENT_ID = derive_agent_id_from_identity_seed(LEFT_IDENTITY_SEED)
RIGHT_AGENT_ID = derive_agent_id_from_identity_seed(RIGHT_IDENTITY_SEED)


class PutEdgesWriter:
    def __init__(self) -> None:
        self.edges: list[dict[str, Any]] = []

    def put_edges(self, edges: list[dict[str, Any]]) -> dict[str, Any]:
        self.edges.extend(edges)
        return {"accepted_edges": len(edges)}


def _leaf(nonce: bytes) -> bytes:
    return hashlib.sha256(INVITE_NONCE_LEAF_DOMAIN + nonce).digest()


def _root(left: bytes, right: bytes) -> str:
    return hashlib.sha256(INVITE_NONCE_NODE_DOMAIN + left + right).hexdigest()


def _left_proof_dict() -> tuple[dict[str, object], ...]:
    return ({"sibling": _leaf(RIGHT_NONCE).hex(), "position": "right"},)


def _right_proof_dict() -> tuple[dict[str, object], ...]:
    return ({"sibling": _leaf(LEFT_NONCE).hex(), "position": "left"},)


def _left_proof_hash_tuple() -> tuple[str, ...]:
    return (_leaf(RIGHT_NONCE).hex(),)


def _build_two_nonce_batch(*, batch_id: str = "batch-1576r-two"):
    return build_invite_batch_record(
        inviter_cid=INVITER_CID,
        batch_id=batch_id,
        count=2,
        created_epoch=0,
        inviter_sig="genesis",
        nonces=(LEFT_NONCE, RIGHT_NONCE),
    )


def _build_single_redemption(*, batch_id: str = "batch-1576r-single"):
    batch, private_nonces = build_invite_batch_record(
        inviter_cid=INVITER_CID,
        batch_id=batch_id,
        count=1,
        created_epoch=0,
        inviter_sig="genesis",
        nonces=(LEFT_NONCE,),
    )
    redemption = build_invite_redemption_record(
        batch=batch,
        nonce=private_nonces[0],
        nonce_membership_proof=(),
        redeemer_pubkey_cid="pubkey:redeemer-left",
        identity_seed=LEFT_IDENTITY_SEED,
        redemption_epoch=0,
    )
    return batch, redemption


def test_batch_creation_and_single_redemption_end_to_end(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(invite_enforcement, "INVITE_ENFORCEMENT_ENABLED", True)
    _batch, redemption = _build_single_redemption()
    registry = InviteNullifierRegistry()
    remote_registry = InviteNullifierRegistry()
    writer = PutEdgesWriter()

    invite_enforcement.require_invite_for_enrollment(
        LEFT_AGENT_ID,
        redemption,
        nullifier_registry=registry,
        register_nullifier=True,
        require_redeemer_key_binding=False,
    )
    message = build_nullifier_gossip_message(
        redemption.redemption_nullifier,
        claimed_actor="agent-alpha",
    )
    gossip_result = handle_nullifier_gossip_message(message, remote_registry)
    edge = build_invite_provenance_edge_from_redemption(
        redemption,
        source_node_id=f"init:{LEFT_AGENT_ID}",
    )
    write_receipt = write_invite_provenance_edge(edge, writer)

    assert registry.is_known(redemption.redemption_nullifier) is True
    assert gossip_result == "registered"
    assert remote_registry.is_known(redemption.redemption_nullifier) is True
    assert len(writer.edges) == 1
    assert writer.edges[0]["edge_type"] == "PROVENANCE"
    assert writer.edges[0]["target"] == INVITER_CID
    assert write_receipt["no_credit_computed"] is True
    assert write_receipt["no_settlement_activated"] is True


def test_batch_creation_and_redemption_nonce_membership_verified() -> None:
    batch, private_nonces = _build_two_nonce_batch()

    verify_nonce_membership_proof(
        nonce_bytes=LEFT_NONCE,
        nonce_merkle_root=batch.nonce_merkle_root,
        count=batch.count,
        proof=_left_proof_dict(),
    )
    redemption = build_invite_redemption_record(
        batch=batch,
        nonce=private_nonces[0],
        nonce_membership_proof=_left_proof_hash_tuple(),
        redeemer_pubkey_cid="pubkey:redeemer-left",
        identity_seed=LEFT_IDENTITY_SEED,
        redemption_epoch=0,
    )

    assert redemption.redemption_nullifier == derive_invite_redemption_nullifier(
        batch.batch_id,
        private_nonces[0],
    )
    assert redemption.inviter_cid == INVITER_CID


def test_single_nonce_batch_no_proof_required() -> None:
    batch, redemption = _build_single_redemption(batch_id="batch-1576r-single-proof")

    verify_nonce_membership_proof(
        nonce_bytes=LEFT_NONCE,
        nonce_merkle_root=batch.nonce_merkle_root,
        count=batch.count,
        proof=(),
    )

    assert redemption.nonce_membership_proof == ()
    assert redemption.redeemer_agent_id == LEFT_AGENT_ID


def test_double_redemption_rejected_by_nullifier_registry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(invite_enforcement, "INVITE_ENFORCEMENT_ENABLED", True)
    _batch, redemption = _build_single_redemption(batch_id="batch-1576r-replay")
    registry = InviteNullifierRegistry()

    invite_enforcement.require_invite_for_enrollment(
        LEFT_AGENT_ID,
        redemption,
        nullifier_registry=registry,
        register_nullifier=True,
        require_redeemer_key_binding=False,
    )

    with pytest.raises(ValueError, match="invite_nullifier_already_used_for_enrollment"):
        invite_enforcement.require_invite_for_enrollment(
            LEFT_AGENT_ID,
            redemption,
            nullifier_registry=registry,
            register_nullifier=True,
            require_redeemer_key_binding=False,
        )


def test_different_nonce_from_same_batch_accepted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(invite_enforcement, "INVITE_ENFORCEMENT_ENABLED", True)
    batch, private_nonces = _build_two_nonce_batch(batch_id="batch-1576r-distinct")
    registry = InviteNullifierRegistry()
    left = build_invite_redemption_record(
        batch=batch,
        nonce=private_nonces[0],
        nonce_membership_proof=_left_proof_hash_tuple(),
        redeemer_pubkey_cid="pubkey:redeemer-left",
        identity_seed=LEFT_IDENTITY_SEED,
        redemption_epoch=0,
    )
    right = build_invite_redemption_record(
        batch=batch,
        nonce=private_nonces[1],
        nonce_membership_proof=(_leaf(LEFT_NONCE).hex(),),
        redeemer_pubkey_cid="pubkey:redeemer-right",
        identity_seed=RIGHT_IDENTITY_SEED,
        redemption_epoch=0,
    )

    invite_enforcement.require_invite_for_enrollment(
        LEFT_AGENT_ID,
        left,
        nullifier_registry=registry,
        register_nullifier=True,
        require_redeemer_key_binding=False,
    )
    invite_enforcement.require_invite_for_enrollment(
        RIGHT_AGENT_ID,
        right,
        nullifier_registry=registry,
        register_nullifier=True,
        require_redeemer_key_binding=False,
    )

    assert left.redemption_nullifier != right.redemption_nullifier
    assert registry.is_known(left.redemption_nullifier) is True
    assert registry.is_known(right.redemption_nullifier) is True
    assert len(registry) == 2


def test_enforcement_disabled_allows_enrollment_without_invite(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(invite_enforcement, "INVITE_ENFORCEMENT_ENABLED", False)

    invite_enforcement.require_invite_for_enrollment("agent-without-invite", None)


def test_enforcement_enabled_blocks_enrollment_without_invite(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(invite_enforcement, "INVITE_ENFORCEMENT_ENABLED", True)

    with pytest.raises(ValueError, match="invite_required_for_enrollment"):
        invite_enforcement.require_invite_for_enrollment("agent-without-invite", None)


def test_provenance_edge_inviter_cid_matches_batch_inviter() -> None:
    batch, redemption = _build_single_redemption(batch_id="batch-1576r-edge")
    edge = build_invite_provenance_edge_from_redemption(
        redemption.to_dict(),
        source_node_id=f"init:{LEFT_AGENT_ID}",
    )

    assert edge.target_node_id == batch.inviter_cid
    assert edge.to_atlas_edge()["target"] == batch.inviter_cid
    assert edge.to_backward_attribution_edge() == {
        "edge_confidence": "1",
        "edge_type": "PROVENANCE",
        "source_node_id": f"init:{LEFT_AGENT_ID}",
        "target_node_id": batch.inviter_cid,
    }


def test_no_hardcoded_fraction_in_integration_path() -> None:
    _batch, redemption = _build_single_redemption(batch_id="batch-1576r-no-fraction")
    writer = PutEdgesWriter()
    edge = build_invite_provenance_edge_from_redemption(
        redemption,
        source_node_id=f"init:{LEFT_AGENT_ID}",
    )
    receipt = write_invite_provenance_edge(edge, writer)

    assert not hasattr(invite_provenance_wiring, "compute_inviter_ecu_credit")
    assert edge.no_fixed_invite_fraction is True
    assert edge.invite_credit_model == "organic_cdl_108_backward_attribution"
    assert receipt["no_credit_computed"] is True
    assert receipt["no_settlement_activated"] is True


def test_invalid_merkle_proof_rejects_redemption_before_nullifier_registered() -> None:
    batch, private_nonces = _build_two_nonce_batch(batch_id="batch-1576r-bad-proof")
    nullifier = derive_invite_redemption_nullifier(batch.batch_id, private_nonces[0])
    registry = InviteNullifierRegistry()
    bundle = {
        "intended_epoch": 0,
        "intended_profile": PROFILE,
        "invite_batch_record": batch.to_dict(),
        "nonce_membership_proof": [
            {"sibling": _leaf(RIGHT_NONCE).hex(), "position": "left"}
        ],
        "private_invite_nonce": private_nonces[0],
    }

    decision = verify_invite_bootstrap(
        bundle,
        expected_profile=PROFILE,
        current_epoch=0,
        local_nullifier_registry=registry,
        persist_nullifier=False,
    )

    assert decision.bootstrap_allowed is False
    assert decision.defect_token == "nonce_membership_mismatch"
    assert registry.is_known(nullifier) is False


def test_valid_merkle_proof_reaches_openclaw_acceptance_and_local_registration() -> None:
    batch, private_nonces = _build_two_nonce_batch(batch_id="batch-1576r-openclaw-proof")
    nullifier = derive_invite_redemption_nullifier(batch.batch_id, private_nonces[0])
    registry = InviteNullifierRegistry()
    bundle = {
        "intended_epoch": 0,
        "intended_profile": PROFILE,
        "invite_batch_record": batch.to_dict(),
        "nonce_membership_proof": list(_left_proof_dict()),
        "private_invite_nonce": private_nonces[0],
    }

    decision = verify_invite_bootstrap(
        bundle,
        expected_profile=PROFILE,
        current_epoch=0,
        local_nullifier_registry=registry,
        persist_nullifier=False,
    )

    assert decision.bootstrap_allowed is True
    assert decision.nonce_membership_status == "verified"
    assert decision.redemption_nullifier == nullifier
    assert registry.is_known(nullifier) is True
