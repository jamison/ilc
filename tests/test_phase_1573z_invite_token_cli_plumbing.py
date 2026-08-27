# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1573z invite token CLI plumbing tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from ilc_core.genesis.invitation_provenance_record import (
    DEFAULT_SIGNING_LEVEL,
    INVITE_BATCH_RUNTIME_VERSION,
    InviteRedemptionRecord,
    SigningLevel,
    build_invite_batch_record,
    build_invite_redemption_record,
    derive_invite_redemption_nullifier,
    invite_record_canonical_json,
)


def test_invite_batch_record_single_node_regardless_of_count() -> None:
    record, private_nonces = build_invite_batch_record(
        inviter_cid="genesis_agent:01",
        batch_id="batch-1573z",
        count=3,
        created_epoch=0,
        inviter_sig="genesis",
        nonces=(b"a" * 32, b"b" * 32, b"c" * 32),
    )

    assert record.count == 3
    assert len(private_nonces) == 3
    assert len(record.canonical_cid()) == 64
    assert "nonce_merkle_root" in record.to_dict()
    assert "private_invite_nonces" not in record.to_dict()
    serialized = json.dumps(record.to_dict(), sort_keys=True)
    assert "private_invite_nonces" not in serialized
    assert private_nonces[0] not in serialized


def test_same_nonce_produces_same_nullifier_and_redemption_cid() -> None:
    batch, _private_nonces = build_invite_batch_record(
        inviter_cid="genesis_agent:01",
        batch_id="batch-idempotent",
        count=1,
        created_epoch=0,
        inviter_sig="genesis",
        nonces=(bytes.fromhex("11" * 32),),
    )

    kwargs = {
        "batch": batch,
        "nonce": "11" * 32,
        "nonce_membership_proof": (),
        "redeemer_pubkey_cid": "pubkey:redeemer",
        "identity_seed": "22" * 32,
        "redemption_epoch": 0,
    }
    first = build_invite_redemption_record(**kwargs)
    second = build_invite_redemption_record(**kwargs)

    assert first.redemption_nullifier == second.redemption_nullifier
    assert first.canonical_cid() == second.canonical_cid()
    assert first.redemption_nullifier == derive_invite_redemption_nullifier("batch-idempotent", "11" * 32)


def test_inviter_chain_preserved_from_batch_to_redemption() -> None:
    batch, _private_nonces = build_invite_batch_record(
        inviter_cid="agent:trusted-inviter",
        batch_id="batch-chain",
        count=1,
        created_epoch=0,
        inviter_sig="sig",
        nonces=(b"z" * 32,),
    )
    redemption = build_invite_redemption_record(
        batch=batch,
        nonce=b"z" * 32,
        nonce_membership_proof=(),
        redeemer_pubkey_cid="pubkey:redeemer",
        identity_seed=b"i" * 32,
        redemption_epoch=1,
    )

    assert redemption.inviter_cid == "agent:trusted-inviter"
    assert redemption.batch_id == "batch-chain"


def test_raw_nonce_absent_from_redemption_and_canonical_json() -> None:
    record = InviteRedemptionRecord(
        batch_id="batch-private",
        redemption_nullifier="0" * 64,
        nonce_membership_proof=({"position": "right", "sibling": "1" * 64},),
        redeemer_pubkey_cid="pubkey:redeemer",
        redeemer_agent_id="2" * 96,
        redemption_epoch=0,
        inviter_cid="genesis_agent:01",
    )
    serialized = invite_record_canonical_json(record)

    assert "raw_nonce" not in record.to_dict()
    assert "private_invite_nonces" not in serialized
    assert "nonce_membership_proof" in serialized


def test_record_creation_does_not_create_identity_node() -> None:
    batch, _private_nonces = build_invite_batch_record(
        inviter_cid="genesis_agent:01",
        batch_id="batch-no-identity",
        count=1,
        created_epoch=0,
        inviter_sig="genesis",
        nonces=(b"n" * 32,),
    )
    redemption = build_invite_redemption_record(
        batch=batch,
        nonce=b"n" * 32,
        nonce_membership_proof=(),
        redeemer_pubkey_cid="pubkey:redeemer",
        identity_seed=b"s" * 32,
        redemption_epoch=0,
    )

    assert "agent_node" not in batch.to_dict()
    assert "identity_node" not in redemption.to_dict()
    assert "new_agent_node" not in redemption.to_dict()


def test_signing_level_autonomous_default() -> None:
    assert INVITE_BATCH_RUNTIME_VERSION == "invite_batch_runtime_1573z.v0.1"
    assert DEFAULT_SIGNING_LEVEL is SigningLevel.AUTONOMOUS
    assert [level.value for level in SigningLevel] == ["autonomous", "session", "manual"]


def test_identity_invite_create_help_exposes_existing_hierarchy() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ilc_core.cli.main", "identity", "invite", "create", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--enable-invites" in result.stdout
    assert "--count" in result.stdout
    assert "--output" in result.stdout


def test_identity_init_help_exposes_invite_redemption_flags() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ilc_core.cli.main", "identity", "init", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--invite" in result.stdout
    assert "--enable-invites" in result.stdout
    assert "--identity-seed-hex" in result.stdout
    assert "--redeemer-pubkey-cid" in result.stdout


def test_identity_invite_create_is_default_off(tmp_path: Path) -> None:
    output = tmp_path / "invite_batch.json"
    graph_state = tmp_path / "graph.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ilc_core.cli.main",
            "--graph-state",
            str(graph_state),
            "identity",
            "invite",
            "create",
            "--count",
            "1",
            "--output",
            str(output),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "invite_cli_not_enabled_use_enable_invites" in result.stderr
    assert not output.exists()


def test_identity_invite_create_enabled_writes_local_artifact_only(tmp_path: Path) -> None:
    output = tmp_path / "invite_batch.json"
    graph_state = tmp_path / "graph.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ilc_core.cli.main",
            "--graph-state",
            str(graph_state),
            "identity",
            "invite",
            "create",
            "--enable-invites",
            "--count",
            "1",
            "--output",
            str(output),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["production_graph_write"] is False
    assert len(payload["private_invite_nonces"]) == 1
    assert "private_invite_nonces" not in payload["invite_batch_record"]


def test_identity_init_with_invite_writes_local_redemption_record_only(tmp_path: Path) -> None:
    invite_path = tmp_path / "invite_batch.json"
    graph_state = tmp_path / "graph.json"
    create_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ilc_core.cli.main",
            "--graph-state",
            str(graph_state),
            "identity",
            "invite",
            "create",
            "--enable-invites",
            "--count",
            "1",
            "--output",
            str(invite_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert create_result.returncode == 0, create_result.stderr

    init_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ilc_core.cli.main",
            "--graph-state",
            str(graph_state),
            "identity",
            "init",
            "--enable-invites",
            "--invite",
            str(invite_path),
            "--identity-seed-hex",
            "44" * 32,
            "--redeemer-pubkey-cid",
            "pubkey:redeemer",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert init_result.returncode == 0, init_result.stderr
    payload = json.loads(init_result.stdout)
    state = payload["data"]["state"]
    assert state["production_graph_write"] is False
    assert state["invite_runtime_version"] == INVITE_BATCH_RUNTIME_VERSION
    assert "invite_redemption_record" in state
    assert "private_invite_nonces" not in state["invite_redemption_record"]
    assert "identity_node" not in state
