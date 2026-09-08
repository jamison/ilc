# SPDX-License-Identifier: AGPL-3.0-only
"""Regression tests for identity-init durable invite nullifier wiring."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from ilc_core.cli.main import _run_identity_subcommand
from ilc_core.genesis import invite_enforcement
from ilc_core.genesis.invitation_provenance_record import (
    build_invite_batch_record,
    derive_agent_id_from_identity_seed,
    validate_invite_redemption_record,
)
from ilc_core.genesis.invite_nullifier_lmdb_store import InviteNullifierLmdbRegistry


IDENTITY_SEED_HEX = "44" * 32
REDEEMER_AGENT_ID = derive_agent_id_from_identity_seed(IDENTITY_SEED_HEX)


def _identity_init_args(invite_path: Path | str = "") -> argparse.Namespace:
    return argparse.Namespace(
        identity_subcommand="init",
        lineage_id="lineage-local",
        key_ref="key-local-0",
        invite=str(invite_path),
        enable_invites=bool(invite_path),
        identity_seed_hex=IDENTITY_SEED_HEX,
        redeemer_pubkey_cid="pubkey:redeemer",
        redemption_epoch=0,
    )


def _invite_batch_file(tmp_path: Path, *, nonce_byte: str = "55") -> Path:
    batch, private_nonces = build_invite_batch_record(
        inviter_cid="genesis_agent:01",
        batch_id=f"batch-fix1-{nonce_byte}",
        count=1,
        created_epoch=0,
        inviter_sig="genesis",
        nonces=(bytes.fromhex(nonce_byte * 32),),
    )
    path = tmp_path / f"invite_batch_{nonce_byte}.json"
    path.write_text(
        json.dumps(
            {
                "invite_batch_record": batch.to_dict(),
                "private_invite_nonces": list(private_nonces),
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return path


def test_identity_init_invite_registers_nullifier_durably_when_enforcement_off(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(invite_enforcement, "INVITE_ENFORCEMENT_ENABLED", False)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    invite_path = _invite_batch_file(tmp_path)

    result = _run_identity_subcommand(_identity_init_args(invite_path), tmp_path / "first_graph.json")
    redemption = validate_invite_redemption_record(result["state"]["invite_redemption_record"])

    with InviteNullifierLmdbRegistry(tmp_path / "home" / ".ilc" / "lmdb" / "nullifiers") as registry:
        assert registry.is_known(redemption.redemption_nullifier)


def test_identity_init_invite_replay_rejected_after_lmdb_restart_when_enforcement_off(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(invite_enforcement, "INVITE_ENFORCEMENT_ENABLED", False)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    invite_path = _invite_batch_file(tmp_path)

    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    first_dir.mkdir()
    second_dir.mkdir()

    _run_identity_subcommand(_identity_init_args(invite_path), first_dir / "graph.json")

    with pytest.raises(ValueError, match="invite_nullifier_already_used_for_enrollment"):
        _run_identity_subcommand(_identity_init_args(invite_path), second_dir / "graph.json")


def test_identity_init_without_invite_does_not_create_nullifier_lmdb_when_enforcement_off(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(invite_enforcement, "INVITE_ENFORCEMENT_ENABLED", False)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))

    result = _run_identity_subcommand(_identity_init_args(""), tmp_path / "graph.json")

    assert result["action"] == "init"
    assert not (tmp_path / "home" / ".ilc" / "lmdb" / "nullifiers").exists()


def test_identity_init_does_not_double_register_when_enforcement_enabled(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(invite_enforcement, "INVITE_ENFORCEMENT_ENABLED", True)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    invite_path = _invite_batch_file(tmp_path, nonce_byte="66")

    def fake_require_invite_for_enrollment(
        agent_id: str,
        invite_redemption_record: object,
        *,
        nullifier_registry: object | None = None,
        register_nullifier: bool = False,
        **_: object,
    ) -> None:
        assert agent_id == REDEEMER_AGENT_ID
        assert nullifier_registry is not None
        assert register_nullifier is True
        redemption = validate_invite_redemption_record(invite_redemption_record)
        assert nullifier_registry.register_if_new(redemption.redemption_nullifier) is True

    monkeypatch.setattr(
        invite_enforcement,
        "require_invite_for_enrollment",
        fake_require_invite_for_enrollment,
    )

    result = _run_identity_subcommand(_identity_init_args(invite_path), tmp_path / "graph.json")

    assert result["action"] == "init"
