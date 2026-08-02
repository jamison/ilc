# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1576r-Fix1 durable invite-nullifier LMDB persistence tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from ilc_core.genesis import invite_enforcement
from ilc_core.genesis.invite_nullifier_lmdb_store import (
    INVITE_NULLIFIER_LMDB_STORE_VERSION,
    InviteNullifierLmdbRegistry,
)
from ilc_core.genesis.invite_nullifier_registry import InviteNullifierError
from ilc_core.network.d2d.invite_nullifier_gossip import (
    build_nullifier_gossip_message,
    handle_nullifier_gossip_message,
)
from tests.test_invite_chain_integration_1576r import (
    LEFT_AGENT_ID,
    _build_single_redemption,
)


NULLIFIER_A = "a" * 64
NULLIFIER_B = "b" * 64


def test_lmdb_nullifier_survives_registry_restart(tmp_path: Path) -> None:
    store_path = tmp_path / "invite-nullifiers.lmdb"
    with InviteNullifierLmdbRegistry(store_path) as registry:
        registry.register_nullifier(NULLIFIER_A)
        assert registry.is_known(NULLIFIER_A) is True
        assert len(registry) == 1

    with InviteNullifierLmdbRegistry(store_path) as restarted:
        assert restarted.is_known(NULLIFIER_A) is True
        assert len(restarted) == 1


def test_lmdb_register_if_new_rejects_duplicate_after_restart(tmp_path: Path) -> None:
    store_path = tmp_path / "invite-nullifiers.lmdb"
    with InviteNullifierLmdbRegistry(store_path) as registry:
        assert registry.register_if_new(NULLIFIER_A) is True

    with InviteNullifierLmdbRegistry(store_path) as restarted:
        assert restarted.register_if_new(NULLIFIER_A) is False
        assert restarted.register_if_new(NULLIFIER_B) is True
        assert len(restarted) == 2


def test_invite_enforcement_rejects_lmdb_persisted_replay_after_restart(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(invite_enforcement, "INVITE_ENFORCEMENT_ENABLED", True)
    _batch, redemption = _build_single_redemption(batch_id="batch-1576r-fix1-restart")
    store_path = tmp_path / "invite-nullifiers.lmdb"
    with InviteNullifierLmdbRegistry(store_path) as registry:
        invite_enforcement.require_invite_for_enrollment(
            LEFT_AGENT_ID,
            redemption,
            nullifier_registry=registry,
            register_nullifier=True,
        )

    with InviteNullifierLmdbRegistry(store_path) as restarted:
        with pytest.raises(ValueError, match="invite_nullifier_already_used_for_enrollment"):
            invite_enforcement.require_invite_for_enrollment(
                LEFT_AGENT_ID,
                redemption,
                nullifier_registry=restarted,
                register_nullifier=True,
            )


def test_d2d_gossip_handler_persists_nullifier_to_lmdb(tmp_path: Path) -> None:
    store_path = tmp_path / "invite-nullifiers.lmdb"
    message = build_nullifier_gossip_message(NULLIFIER_A, claimed_actor="agent-a")
    with InviteNullifierLmdbRegistry(store_path) as registry:
        assert handle_nullifier_gossip_message(message, registry) == "registered"

    with InviteNullifierLmdbRegistry(store_path) as restarted:
        assert restarted.is_known(NULLIFIER_A) is True
        assert handle_nullifier_gossip_message(message, restarted) == "duplicate_discarded"


def test_lmdb_registry_capacity_counts_persisted_entries(tmp_path: Path) -> None:
    store_path = tmp_path / "invite-nullifiers.lmdb"
    with InviteNullifierLmdbRegistry(store_path, max_registry_size=1) as registry:
        registry.register_nullifier(NULLIFIER_A)

    with InviteNullifierLmdbRegistry(store_path, max_registry_size=1) as restarted:
        with pytest.raises(InviteNullifierError, match="invite_nullifier_registry_full"):
            restarted.register_nullifier(NULLIFIER_B)


def test_lmdb_discard_removes_persisted_nullifier(tmp_path: Path) -> None:
    store_path = tmp_path / "invite-nullifiers.lmdb"
    with InviteNullifierLmdbRegistry(store_path) as registry:
        registry.register_nullifier(NULLIFIER_A)
        registry.discard_nullifier(NULLIFIER_A)

    with InviteNullifierLmdbRegistry(store_path) as restarted:
        assert restarted.is_known(NULLIFIER_A) is False
        assert len(restarted) == 0


def test_lmdb_payload_corruption_fails_closed(tmp_path: Path) -> None:
    store_path = tmp_path / "invite-nullifiers.lmdb"
    with InviteNullifierLmdbRegistry(store_path) as registry:
        registry.register_nullifier(NULLIFIER_A)
        with registry.env.begin(write=True, db=registry._nullifiers_db) as txn:
            txn.put(NULLIFIER_A.encode("ascii"), b'{"seen":false}')

    with InviteNullifierLmdbRegistry(store_path) as restarted:
        with pytest.raises(InviteNullifierError, match="invite_nullifier_lmdb_payload_invalid"):
            restarted.is_known(NULLIFIER_A)


def test_lmdb_store_version_is_named_for_status_token() -> None:
    assert INVITE_NULLIFIER_LMDB_STORE_VERSION == "invite_nullifier_lmdb_store_1576r_fix1.v0.1"
