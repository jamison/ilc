from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from ilc_core.cli import main as cli_main
from ilc_core.crypto.pq_signature_verify import _MLDSA_PK_HEX_LENGTH, _MLDSA_SIG_HEX_LENGTH
from ilc_core.identity import first_run_provisioning as provisioning
from ilc_core.identity.bls_backend import verify_invitee_install_receipt_digest
from ilc_core.identity.first_run_provisioning import (
    GENESIS_ROOT_ENVELOPE_HASH,
    identity_root,
    provision_new_identity,
    record_invite_bootstrap_capsule_evidence,
    validate_invite_bootstrap_capsule_fields,
    write_invitee_install_receipt,
)
from ilc_core.network.d2d import gossip_peer_registry
from ilc_core.network.d2d.gossip_peer_registry import GossipPeerRegistry


MLDSA_PUBKEY_HEX = "b" * _MLDSA_PK_HEX_LENGTH
MLDSA_SIGNATURE_HEX = "a" * _MLDSA_SIG_HEX_LENGTH


def _peer_advertisement(
    *,
    agent_id: str = "1" * 96,
    endpoint_host: str = "peer-a.ilc.example",
    key_binding_ref: str = "mldsa:key:peer-a",
    peer_timestamp_epoch: int = 0,
    ttl_epochs: int = 4,
) -> dict[str, Any]:
    return {
        "body": {
            "agent_id": agent_id,
            "content_availability_count": 0,
            "installed_slices_digest": "2" * 96,
            "peer_timestamp_epoch": peer_timestamp_epoch,
            "protocol_version": "ilc-d2d-testnet-v1",
            "transport_endpoint": {
                "host": endpoint_host,
                "port": 443,
                "scheme": "https",
            },
            "ttl_epochs": ttl_epochs,
        },
        "key_binding_ref": key_binding_ref,
        "ml_dsa_signature": MLDSA_SIGNATURE_HEX,
        "schema_version": "peer_advertisement_cdl103.v0.1",
    }


def _connectivity_receipt() -> dict[str, Any]:
    return {
        "connectivity_mode": "local_only",
        "connectivity_receipt_sha384": "3" * 96,
    }


def _receipt_digest(receipt: dict[str, Any]) -> str:
    body = dict(receipt)
    body.pop("created_at_unix")
    body.pop("signature")
    body.pop("signature_payload_ref")
    return hashlib.sha384(
        json.dumps(body, sort_keys=True, separators=(",", ":"), allow_nan=False).encode(
            "utf-8"
        )
    ).hexdigest()


def test_validate_capsule_accepts_absent_optional_fields() -> None:
    evidence = validate_invite_bootstrap_capsule_fields({}, current_epoch=0)

    assert evidence["genesis_state_root"] == GENESIS_ROOT_ENVELOPE_HASH
    assert evidence["genesis_state_root_status"] == "absent_using_package_root"
    assert evidence["known_peer_hints_verified"] == 0


def test_validate_capsule_rejects_genesis_state_root_mismatch() -> None:
    with pytest.raises(ValueError, match="invite_bootstrap_genesis_state_root_mismatch"):
        validate_invite_bootstrap_capsule_fields(
            {"genesis_state_root": "sha256:" + ("0" * 64)},
            current_epoch=0,
        )


def test_validate_capsule_rejects_more_than_eight_peer_hints() -> None:
    with pytest.raises(ValueError, match="invite_bootstrap_known_peer_hints_too_many"):
        validate_invite_bootstrap_capsule_fields(
            {"known_peer_hints": [_peer_advertisement() for _ in range(9)]},
            current_epoch=0,
        )


def test_validate_capsule_verifies_peer_hints_with_key_binding(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[bytes, str, str]] = []

    def fake_verify(message: bytes, signature_hex: str, pubkey_hex: str) -> bool:
        calls.append((message, signature_hex, pubkey_hex))
        return True

    monkeypatch.setattr(provisioning, "verify_mldsa65_signature", fake_verify)

    evidence = validate_invite_bootstrap_capsule_fields(
        {
            "genesis_state_root": GENESIS_ROOT_ENVELOPE_HASH,
            "inviter_connectivity_mode": "outbound_only",
            "known_peer_hint_key_bindings": {"mldsa:key:peer-a": MLDSA_PUBKEY_HEX},
            "known_peer_hints": [_peer_advertisement()],
        },
        current_epoch=0,
    )

    assert evidence["inviter_connectivity_mode"] == "outbound_only"
    assert evidence["known_peer_hints_verified"] == 1
    assert evidence["known_peer_hints_dropped_unverifiable"] == 0
    assert calls and calls[0][1] == MLDSA_SIGNATURE_HEX
    assert calls[0][2] == MLDSA_PUBKEY_HEX


def test_validate_capsule_drops_unverifiable_and_expired_hints(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        provisioning,
        "verify_mldsa65_signature",
        lambda _message, _signature, _pubkey: False,
    )

    evidence = validate_invite_bootstrap_capsule_fields(
        {
            "known_peer_hint_key_bindings": {
                "mldsa:key:peer-a": MLDSA_PUBKEY_HEX,
                "mldsa:key:peer-b": MLDSA_PUBKEY_HEX,
            },
            "known_peer_hints": [
                _peer_advertisement(key_binding_ref="mldsa:key:peer-a"),
                _peer_advertisement(
                    agent_id="4" * 96,
                    endpoint_host="peer-b.ilc.example",
                    key_binding_ref="mldsa:key:peer-b",
                    peer_timestamp_epoch=0,
                    ttl_epochs=1,
                ),
            ],
        },
        current_epoch=1,
    )

    assert evidence["known_peer_hints_verified"] == 0
    assert evidence["known_peer_hints_dropped_unverifiable"] == 1
    assert evidence["known_peer_hints_dropped_expired"] == 1


def test_record_capsule_evidence_persists_self_verifiable_hints(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        provisioning,
        "verify_mldsa65_signature",
        lambda _message, _signature, _pubkey: True,
    )
    agent = provision_new_identity(tmp_path, invite_id="invite-a", emit_warning=False)
    evidence = validate_invite_bootstrap_capsule_fields(
        {
            "known_peer_hint_key_bindings": {"mldsa:key:peer-a": MLDSA_PUBKEY_HEX},
            "known_peer_hints": [_peer_advertisement()],
        },
        current_epoch=0,
    )

    record = record_invite_bootstrap_capsule_evidence(
        tmp_path,
        agent_id=agent["agent_id"],
        current_epoch=0,
        capsule_evidence=evidence,
    )

    root = identity_root(tmp_path)
    hints_path = root / "bootstrap_peer_hints.json"
    hints = json.loads(hints_path.read_text(encoding="utf-8"))
    onboarding = json.loads((root / "onboarding_receipt.json").read_text(encoding="utf-8"))
    assert record["invite_bootstrap_capsule_evidence"]["bootstrap_peer_hints_count"] == 1
    assert hints["schema_version"] == "bootstrap_peer_hints.v0.1"
    assert hints["known_peer_hint_key_bindings"] == {"mldsa:key:peer-a": MLDSA_PUBKEY_HEX}
    assert onboarding["bootstrap_peer_hints_path"] == str(hints_path)


def test_gossip_registry_loads_persisted_bootstrap_hints_after_reverification(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        provisioning,
        "verify_mldsa65_signature",
        lambda _message, _signature, _pubkey: True,
    )
    monkeypatch.setattr(
        gossip_peer_registry,
        "verify_mldsa65_signature",
        lambda _message, _signature, _pubkey: True,
    )
    agent = provision_new_identity(tmp_path, invite_id="invite-a", emit_warning=False)
    evidence = validate_invite_bootstrap_capsule_fields(
        {
            "known_peer_hint_key_bindings": {"mldsa:key:peer-a": MLDSA_PUBKEY_HEX},
            "known_peer_hints": [_peer_advertisement()],
        },
        current_epoch=0,
    )
    record_invite_bootstrap_capsule_evidence(
        tmp_path,
        agent_id=agent["agent_id"],
        current_epoch=0,
        capsule_evidence=evidence,
    )

    registry = GossipPeerRegistry([])

    assert registry.load_bootstrap_hints(
        identity_root(tmp_path) / "bootstrap_peer_hints.json",
        current_epoch=0,
    ) == 1
    assert registry.get_peers() == ["https://peer-a.ilc.example:443"]


def test_gossip_registry_rejects_tampered_bootstrap_hint_signature(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        gossip_peer_registry,
        "verify_mldsa65_signature",
        lambda _message, _signature, _pubkey: False,
    )
    hints_path = tmp_path / "bootstrap_peer_hints.json"
    hints_path.write_text(
        json.dumps(
            {
                "known_peer_hint_key_bindings": {"mldsa:key:peer-a": MLDSA_PUBKEY_HEX},
                "known_peer_hints": [_peer_advertisement()],
                "schema_version": "bootstrap_peer_hints.v0.1",
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="bootstrap_peer_hint_signature_invalid"):
        GossipPeerRegistry([]).load_bootstrap_hints(hints_path, current_epoch=0)


def test_write_invitee_install_receipt_signs_without_secret_echo(tmp_path: Path) -> None:
    agent = provision_new_identity(tmp_path, invite_id="invite-a", emit_warning=False)
    root = identity_root(tmp_path)
    onboarding = json.loads((root / "onboarding_receipt.json").read_text(encoding="utf-8"))

    receipt = write_invitee_install_receipt(
        tmp_path,
        agent_id=agent["agent_id"],
        invite_id="invite-a",
        invite_nullifier="4" * 64,
        install_epoch=0,
        genesis_state_root=GENESIS_ROOT_ENVELOPE_HASH,
        connectivity_receipt=_connectivity_receipt(),
        onboarding_receipt=onboarding,
        installed_release_artifact_id="test-slice",
        installed_release_canonical_hash="sha256:" + ("5" * 64),
    )

    assert receipt["signature_domain"] == "ILC_INVITEE_INSTALL_RECEIPT_V1"
    assert receipt["signature_payload_ref"] == _receipt_digest(receipt)
    assert "private_invite_nonce" not in json.dumps(receipt, sort_keys=True)
    assert verify_invitee_install_receipt_digest(
        public_key_hex=agent["agent_id"],
        digest_hex=receipt["signature_payload_ref"],
        signature_hex=receipt["signature"],
    )
    assert (root / "invitee_install_receipt.json").is_file()


def test_write_invitee_install_receipt_rejects_blank_release_fields(tmp_path: Path) -> None:
    agent = provision_new_identity(tmp_path, invite_id="invite-a", emit_warning=False)
    root = identity_root(tmp_path)
    onboarding = json.loads((root / "onboarding_receipt.json").read_text(encoding="utf-8"))

    with pytest.raises(ValueError, match="invitee_install_receipt_artifact_id_invalid"):
        write_invitee_install_receipt(
            tmp_path,
            agent_id=agent["agent_id"],
            invite_id="invite-a",
            invite_nullifier="4" * 64,
            install_epoch=0,
            genesis_state_root=GENESIS_ROOT_ENVELOPE_HASH,
            connectivity_receipt=_connectivity_receipt(),
            onboarding_receipt=onboarding,
            installed_release_artifact_id="",
        )


def test_install_receipt_records_resolved_invitee_receipt_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(cli_main.Path, "home", lambda: tmp_path)
    receipt = cli_main._install_invite_bootstrap_capsule_fields(
        {
            "invite_bootstrap_capsule_evidence": {
                "bootstrap_peer_hints_count": 0,
                "bootstrap_peer_hints_path": None,
                "bootstrap_peer_hints_sha384": None,
                "bootstrap_peer_hints_written": False,
                "genesis_state_root": GENESIS_ROOT_ENVELOPE_HASH,
                "genesis_state_root_status": "absent_using_package_root",
                "invite_bootstrap_capsule_schema_version": (
                    "invite_bootstrap_capsule_GAP_INVITE_BOOTSTRAP_CAPSULE_IMPL_00.v0.1"
                ),
                "inviter_connectivity_mode": None,
                "known_peer_hints_dropped_expired": 0,
                "known_peer_hints_dropped_invalid": 0,
                "known_peer_hints_dropped_unverifiable": 0,
                "known_peer_hints_offered": 0,
                "known_peer_hints_verified": 0,
            }
        },
        {"schema_version": "invitee_install_receipt.v0.1"},
    )

    assert receipt["invitee_install_receipt_path"] == str(
        tmp_path / ".ilc" / "identity" / "invitee_install_receipt.json"
    )
