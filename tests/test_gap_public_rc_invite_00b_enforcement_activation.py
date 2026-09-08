# SPDX-License-Identifier: AGPL-3.0-only
"""Public-RC invite enforcement activation regression tests."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from ilc_core.epoch.genesis_settlement_destination import GENESIS_AGENT1_AGENT_ID
from ilc_core.genesis import invite_enforcement
from ilc_core.genesis.invite_nullifier_lmdb_store import InviteNullifierLmdbRegistry
from ilc_core.genesis.invitation_provenance_record import (
    build_invite_batch_record,
    build_invite_redemption_record,
    derive_agent_id_from_identity_seed,
)


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "ilc_core/cli/main.py"
STATUS = ROOT / "docs/phases/STATUS.md"


IDENTITY_SEED_HEX = "77" * 32
REDEEMER_AGENT_ID = derive_agent_id_from_identity_seed(IDENTITY_SEED_HEX)


def _valid_redemption() -> dict[str, object]:
    batch, private_nonces = build_invite_batch_record(
        inviter_cid="genesis_agent:01",
        batch_id="public-rc-00b-activation",
        count=1,
        created_epoch=0,
        inviter_sig="genesis",
        nonces=(bytes.fromhex("88" * 32),),
    )
    redemption = build_invite_redemption_record(
        batch=batch,
        nonce=private_nonces[0],
        nonce_membership_proof=(),
        redeemer_pubkey_cid="pubkey:redeemer",
        identity_seed=IDENTITY_SEED_HEX,
        redemption_epoch=0,
    )
    payload = redemption.to_dict()
    payload["redeemer_key_binding"] = {
        "domain": "ilc-invite-pop-v1",
        "payload_ref": "11" * 48,
        "signature": "22" * 96,
    }
    return payload


def test_enforcement_is_active() -> None:
    assert invite_enforcement.INVITE_ENFORCEMENT_ENABLED is True
    assert invite_enforcement.is_enrollment_invite_enforced() is True


def test_genesis_agent_exempt_when_enforcement_active() -> None:
    invite_enforcement.require_invite_for_enrollment(GENESIS_AGENT1_AGENT_ID, None)


def test_non_genesis_agent_rejected_without_invite() -> None:
    with pytest.raises(ValueError, match="invite_required_for_enrollment"):
        invite_enforcement.require_invite_for_enrollment("agent-without-invite", None)


def test_enforcement_version_token() -> None:
    assert (
        invite_enforcement.INVITE_ENFORCEMENT_RUNTIME_VERSION
        == "invite_enforcement_gate_1576n.v0.1"
    )


def test_valid_invite_registers_lmdb_nullifier(tmp_path: Path) -> None:
    redemption = _valid_redemption()
    with InviteNullifierLmdbRegistry(tmp_path / "nullifiers") as registry:
        invite_enforcement.require_invite_for_enrollment(
            REDEEMER_AGENT_ID,
            redemption,
            nullifier_registry=registry,
            register_nullifier=True,
            require_redeemer_key_binding=False,
        )
        assert registry.is_known(str(redemption["redemption_nullifier"]))


def test_registered_lmdb_nullifier_rejects_replay_after_reopen(tmp_path: Path) -> None:
    redemption = _valid_redemption()
    store = tmp_path / "nullifiers"
    with InviteNullifierLmdbRegistry(store) as registry:
        invite_enforcement.require_invite_for_enrollment(
            REDEEMER_AGENT_ID,
            redemption,
            nullifier_registry=registry,
            register_nullifier=True,
            require_redeemer_key_binding=False,
        )

    with InviteNullifierLmdbRegistry(store) as restarted:
        with pytest.raises(ValueError, match="invite_nullifier_already_used_for_enrollment"):
            invite_enforcement.require_invite_for_enrollment(
                REDEEMER_AGENT_ID,
                redemption,
                nullifier_registry=restarted,
                register_nullifier=True,
                require_redeemer_key_binding=False,
            )


def test_identity_init_and_install_callsites_use_lmdb_registration() -> None:
    source = MAIN.read_text(encoding="utf-8")
    assert "InviteNullifierLmdbRegistry" in source
    assert "register_nullifier=True" in source
    tree = ast.parse(source)
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and getattr(node.func, "id", "") == "require_invite_for_enrollment"
    ]
    guarded_calls = []
    for call in calls:
        kwargs = {keyword.arg: keyword.value for keyword in call.keywords}
        if "nullifier_registry" in kwargs:
            guarded_calls.append(call)
            register_value = kwargs.get("register_nullifier")
            assert isinstance(register_value, ast.Constant)
            assert register_value.value is True
    assert len(guarded_calls) >= 2


def test_status_contains_required_predecessor_tokens() -> None:
    status = STATUS.read_text(encoding="utf-8")
    for token in (
        "invite_bootstrap_profile_committed_GAP_PUBLIC_RC_INVITE_00a",
        "invite_enforcement_fix1_durable_nullifier_wiring_committed_GAP_PUBLIC_RC_INVITE_ENFORCEMENT_FIX1_00",
        "public_rc_published_GAP_PUBLIC_RC_PUBLISH_EXEC_00",
        "genesis_invite_issuer_delegation_complete_GAP_GENESIS_INVITE_ISSUER_00",
    ):
        assert token in status
