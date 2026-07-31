# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1576n invite enforcement gate tests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from ilc_core.cli.main import _run_identity_subcommand
from ilc_core.epoch.genesis_settlement_destination import GENESIS_AGENT1_AGENT_ID
from ilc_core.genesis import invite_enforcement
from ilc_core.genesis.invitation_provenance_record import (
    InviteRedemptionRecord,
    build_invite_batch_record,
    build_invite_redemption_record,
    derive_agent_id_from_identity_seed,
    validate_invite_redemption_record,
)
from ilc_core.genesis.invite_nullifier_registry import InviteNullifierRegistry


IDENTITY_SEED_HEX = "22" * 32
REDEEMER_AGENT_ID = derive_agent_id_from_identity_seed(IDENTITY_SEED_HEX)


def _valid_redemption(*, batch_id: str = "batch-1576n") -> InviteRedemptionRecord:
    batch, private_nonces = build_invite_batch_record(
        inviter_cid="genesis_agent:01",
        batch_id=batch_id,
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


def _invite_batch_file(tmp_path: Path) -> Path:
    batch, private_nonces = build_invite_batch_record(
        inviter_cid="genesis_agent:01",
        batch_id="batch-cli-1576n",
        count=1,
        created_epoch=0,
        inviter_sig="genesis",
        nonces=(bytes.fromhex("33" * 32),),
    )
    path = tmp_path / "invite_batch.json"
    payload = {
        "invite_batch_record": batch.to_dict(),
        "private_invite_nonces": list(private_nonces),
    }
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    return path


def test_enforcement_disabled_no_invite_required(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(invite_enforcement, "INVITE_ENFORCEMENT_ENABLED", False)

    invite_enforcement.require_invite_for_enrollment("agent:without-invite", None)


def test_enforcement_enabled_none_invite_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(invite_enforcement, "INVITE_ENFORCEMENT_ENABLED", True)

    with pytest.raises(ValueError, match="invite_required_for_enrollment"):
        invite_enforcement.require_invite_for_enrollment("agent:without-invite", None)


def test_enforcement_enabled_invalid_invite_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(invite_enforcement, "INVITE_ENFORCEMENT_ENABLED", True)

    with pytest.raises(ValueError):
        invite_enforcement.require_invite_for_enrollment(
            "agent:bad-invite",
            {"batch_id": "missing-required-fields"},
        )


def test_enforcement_enabled_valid_invite_passes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(invite_enforcement, "INVITE_ENFORCEMENT_ENABLED", True)
    redemption = _valid_redemption()

    invite_enforcement.require_invite_for_enrollment(REDEEMER_AGENT_ID, redemption.to_dict())


def test_genesis_agent_bypass_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(invite_enforcement, "INVITE_ENFORCEMENT_ENABLED", False)

    invite_enforcement.require_invite_for_enrollment(GENESIS_AGENT1_AGENT_ID, None)


def test_genesis_agent_bypass_when_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(invite_enforcement, "INVITE_ENFORCEMENT_ENABLED", True)

    invite_enforcement.require_invite_for_enrollment(GENESIS_AGENT1_AGENT_ID, None)


def test_is_enrollment_invite_enforced_returns_bool(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(invite_enforcement, "INVITE_ENFORCEMENT_ENABLED", True)

    assert isinstance(invite_enforcement.is_enrollment_invite_enforced(), bool)
    assert invite_enforcement.is_enrollment_invite_enforced() is True


def test_invite_enforcement_module_guard_is_false_by_default() -> None:
    assert invite_enforcement.INVITE_ENFORCEMENT_ENABLED is False


def test_validate_invite_redemption_record_accepts_dict_and_dataclass() -> None:
    redemption = _valid_redemption(batch_id="batch-validator-wrapper")

    assert validate_invite_redemption_record(redemption) == redemption
    assert validate_invite_redemption_record(redemption.to_dict()) == redemption


def test_redeemer_agent_id_mismatch_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(invite_enforcement, "INVITE_ENFORCEMENT_ENABLED", True)
    redemption = _valid_redemption()

    with pytest.raises(ValueError, match="invite_redeemer_agent_id_mismatch"):
        invite_enforcement.require_invite_for_enrollment("not-the-redeemer", redemption.to_dict())


def test_missing_agent_id_rejected_for_valid_invite(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(invite_enforcement, "INVITE_ENFORCEMENT_ENABLED", True)
    redemption = _valid_redemption(batch_id="batch-missing-agent")

    with pytest.raises(ValueError, match="invite_enrollment_agent_id_required"):
        invite_enforcement.require_invite_for_enrollment("", redemption)


def test_nullifier_already_used_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(invite_enforcement, "INVITE_ENFORCEMENT_ENABLED", True)
    redemption = _valid_redemption(batch_id="batch-nullifier-replay")
    registry = InviteNullifierRegistry()
    registry.register_nullifier(redemption.redemption_nullifier)

    with pytest.raises(ValueError, match="invite_nullifier_already_used_for_enrollment"):
        invite_enforcement.require_invite_for_enrollment(
            REDEEMER_AGENT_ID,
            redemption,
            nullifier_registry=registry,
        )


def test_register_nullifier_requires_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(invite_enforcement, "INVITE_ENFORCEMENT_ENABLED", True)
    redemption = _valid_redemption(batch_id="batch-nullifier-register")

    with pytest.raises(ValueError, match="invite_nullifier_registry_required_for_registration"):
        invite_enforcement.require_invite_for_enrollment(
            REDEEMER_AGENT_ID,
            redemption,
            register_nullifier=True,
        )


def test_cli_identity_init_rejects_missing_invite_when_enforcement_enabled(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(invite_enforcement, "INVITE_ENFORCEMENT_ENABLED", True)
    args = argparse.Namespace(
        identity_subcommand="init",
        lineage_id="lineage-local",
        key_ref="key-local-0",
        invite="",
        enable_invites=False,
        identity_seed_hex=IDENTITY_SEED_HEX,
        redeemer_pubkey_cid="",
        redemption_epoch=0,
    )

    with pytest.raises(ValueError, match="invite_required_for_enrollment"):
        _run_identity_subcommand(args, tmp_path / "graph.json")


def test_cli_identity_init_disabled_ignores_optional_bad_seed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(invite_enforcement, "INVITE_ENFORCEMENT_ENABLED", False)
    args = argparse.Namespace(
        identity_subcommand="init",
        lineage_id="lineage-local",
        key_ref="key-local-0",
        invite="",
        enable_invites=False,
        identity_seed_hex="not-hex",
        redeemer_pubkey_cid="",
        redemption_epoch=0,
    )

    result = _run_identity_subcommand(args, tmp_path / "graph.json")

    assert result["action"] == "init"
    assert "invite_redemption_record" not in result["state"]


def test_cli_identity_init_with_valid_invite_passes_when_enforcement_enabled(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(invite_enforcement, "INVITE_ENFORCEMENT_ENABLED", True)
    invite_path = _invite_batch_file(tmp_path)
    args = argparse.Namespace(
        identity_subcommand="init",
        lineage_id="lineage-local",
        key_ref="key-local-0",
        invite=str(invite_path),
        enable_invites=True,
        identity_seed_hex=IDENTITY_SEED_HEX,
        redeemer_pubkey_cid="pubkey:redeemer",
        redemption_epoch=0,
    )

    result = _run_identity_subcommand(args, tmp_path / "graph.json")

    assert result["action"] == "init"
    state = result["state"]
    assert state["production_graph_write"] is False
    assert state["invite_redemption_record"]["redeemer_agent_id"] == REDEEMER_AGENT_ID
