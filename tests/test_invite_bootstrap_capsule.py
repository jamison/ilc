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
    BOOTSTRAP_FETCH_PEERS_SCHEMA_VERSION,
    GENESIS_ROOT_ENVELOPE_HASH,
    MAX_BOOTSTRAP_FETCH_PEERS,
    MIN_KNOWN_PEERS,
    fetch_distributed_release_peers,
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
                "bootstrap_fetch_bundle_cid": None,
                "bootstrap_fetch_genesis_authority_pubkey_hex": None,
                "bootstrap_fetch_peer_endpoints": [],
                "bootstrap_fetch_peers_count": 0,
                "bootstrap_fetch_peers_path": None,
                "bootstrap_fetch_peers_sha384": None,
                "bootstrap_fetch_peers_written": False,
                "bootstrap_fetch_seed_peer_endpoint": None,
                "bootstrap_fetch_status": "skipped_not_configured",
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


def _bootstrap_bundle() -> dict[str, Any]:
    return {
        "bundle_cid": "bafybootstrap",
        "cdl_version": "cdl_079_bootstrap_bundle_v1",
        "genesis_cid": "bafygenesis",
        "peers": [
            {"endpoint": "https://peer-a.ilc.example:443", "node_id": "node-a"},
            {"endpoint": "https://peer-b.ilc.example:443", "node_id": "node-b"},
        ],
        "schema_version": "bootstrap_bundle_v1",
        "signature": "a" * _MLDSA_SIG_HEX_LENGTH,
        "signed_by": MLDSA_PUBKEY_HEX,
    }


def _fetch_bundle_material() -> dict[str, Any]:
    return {
        "bootstrap_fetch_bundle_cid": "bafybootstrap",
        "bootstrap_fetch_genesis_authority_pubkey_hex": MLDSA_PUBKEY_HEX,
        "bootstrap_fetch_seed_peer_endpoint": "https://seed.ilc.example:443",
    }


def test_fetch_distributed_release_peers_skips_when_known_peer_threshold_met(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_fetch(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("fetch_bootstrap_bundle should not be called")

    from ilc_core.network.d2d import bootstrap_fetch_runtime

    monkeypatch.setattr(bootstrap_fetch_runtime, "fetch_bootstrap_bundle", fail_fetch)

    result = fetch_distributed_release_peers(
        {},
        {"known_peer_hints_verified": MIN_KNOWN_PEERS},
    )

    assert result["bootstrap_fetch_status"] == "skipped_known_peers_sufficient"
    assert result["bootstrap_fetch_peers_count"] == 0


def test_fetch_distributed_release_peers_skips_when_not_configured() -> None:
    result = fetch_distributed_release_peers({}, {"known_peer_hints_verified": 0})

    assert result["bootstrap_fetch_status"] == "skipped_not_configured"
    assert result["bootstrap_fetch_peer_endpoints"] == []


def test_fetch_distributed_release_peers_rejects_partial_material() -> None:
    with pytest.raises(ValueError, match="bootstrap_fetch_material_incomplete"):
        fetch_distributed_release_peers(
            {"bootstrap_fetch_bundle_cid": "bafybootstrap"},
            {"known_peer_hints_verified": 0},
        )


def test_fetch_distributed_release_peers_rejects_missing_bundle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ilc_core.network.d2d import bootstrap_fetch_runtime

    monkeypatch.setattr(
        bootstrap_fetch_runtime,
        "fetch_bootstrap_bundle",
        lambda _seed, _cid: None,
    )

    with pytest.raises(ValueError, match="bootstrap_fetch_bundle_not_found"):
        fetch_distributed_release_peers(
            _fetch_bundle_material(),
            {"known_peer_hints_verified": 0},
            trusted_genesis_authority_pubkey_hex=MLDSA_PUBKEY_HEX,
        )


def test_fetch_distributed_release_peers_rejects_invalid_signature_before_extract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ilc_core.network.d2d import bootstrap_fetch_runtime

    calls: list[str] = []
    monkeypatch.setattr(
        bootstrap_fetch_runtime,
        "fetch_bootstrap_bundle",
        lambda _seed, _cid: _bootstrap_bundle(),
    )

    def fake_verify(_bundle: dict[str, Any], _pubkey: str) -> bool:
        calls.append("verify")
        return False

    def fake_extract(_bundle: dict[str, Any]) -> list[str]:
        calls.append("extract")
        return ["https://peer-a.ilc.example:443"]

    monkeypatch.setattr(bootstrap_fetch_runtime, "verify_bootstrap_bundle_signature", fake_verify)
    monkeypatch.setattr(bootstrap_fetch_runtime, "extract_peer_endpoints", fake_extract)

    with pytest.raises(ValueError, match="bootstrap_fetch_bundle_signature_invalid"):
        fetch_distributed_release_peers(
            _fetch_bundle_material(),
            {"known_peer_hints_verified": 0},
            trusted_genesis_authority_pubkey_hex=MLDSA_PUBKEY_HEX,
        )

    assert calls == ["verify"]


def test_fetch_distributed_release_peers_records_verified_endpoints(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ilc_core.network.d2d import bootstrap_fetch_runtime

    calls: list[str] = []
    monkeypatch.setattr(
        bootstrap_fetch_runtime,
        "fetch_bootstrap_bundle",
        lambda _seed, _cid: _bootstrap_bundle(),
    )

    def fake_verify(_bundle: dict[str, Any], _pubkey: str) -> bool:
        calls.append("verify")
        return True

    def fake_extract(_bundle: dict[str, Any]) -> list[str]:
        calls.append("extract")
        return ["https://peer-a.ilc.example:443", "https://peer-b.ilc.example:443"]

    monkeypatch.setattr(bootstrap_fetch_runtime, "verify_bootstrap_bundle_signature", fake_verify)
    monkeypatch.setattr(bootstrap_fetch_runtime, "extract_peer_endpoints", fake_extract)

    result = fetch_distributed_release_peers(
        _fetch_bundle_material(),
        {"known_peer_hints_verified": 0},
        trusted_genesis_authority_pubkey_hex=MLDSA_PUBKEY_HEX,
    )

    assert calls == ["verify", "extract"]
    assert result["bootstrap_fetch_status"] == "fetched"
    assert result["bootstrap_fetch_peers_count"] == 2
    assert result["bootstrap_fetch_peer_endpoints"] == [
        "https://peer-a.ilc.example:443",
        "https://peer-b.ilc.example:443",
    ]


def test_record_capsule_evidence_persists_distributed_fetch_peers(tmp_path: Path) -> None:
    agent = provision_new_identity(tmp_path, invite_id="invite-a", emit_warning=False)
    evidence = validate_invite_bootstrap_capsule_fields({}, current_epoch=0)
    fetch_evidence = {
        **_fetch_bundle_material(),
        "bootstrap_fetch_peer_endpoints": ["https://peer-a.ilc.example:443"],
        "bootstrap_fetch_peers_count": 1,
        "bootstrap_fetch_status": "fetched",
        "verified_bootstrap_bundle": _bootstrap_bundle(),
    }

    record = record_invite_bootstrap_capsule_evidence(
        tmp_path,
        agent_id=agent["agent_id"],
        current_epoch=0,
        capsule_evidence=evidence,
        distributed_fetch_evidence=fetch_evidence,
    )

    root = identity_root(tmp_path)
    fetch_path = root / "bootstrap_fetch_peers.json"
    fetch_payload = json.loads(fetch_path.read_text(encoding="utf-8"))
    onboarding = json.loads((root / "onboarding_receipt.json").read_text(encoding="utf-8"))
    assert fetch_payload["schema_version"] == BOOTSTRAP_FETCH_PEERS_SCHEMA_VERSION
    assert fetch_payload["peer_endpoints"] == ["https://peer-a.ilc.example:443"]
    assert fetch_payload["bootstrap_fetch_peers_sha384"] == record[
        "invite_bootstrap_capsule_evidence"
    ]["bootstrap_fetch_peers_sha384"]
    assert onboarding["bootstrap_fetch_status"] == "fetched"
    assert onboarding["bootstrap_fetch_peers_path"] == str(fetch_path)


def test_record_capsule_evidence_rejects_float_in_fetch_bundle(tmp_path: Path) -> None:
    agent = provision_new_identity(tmp_path, invite_id="invite-a", emit_warning=False)
    evidence = validate_invite_bootstrap_capsule_fields({}, current_epoch=0)
    fetch_evidence = {
        **_fetch_bundle_material(),
        "bootstrap_fetch_peer_endpoints": ["https://peer-a.ilc.example:443"],
        "bootstrap_fetch_peers_count": 1,
        "bootstrap_fetch_status": "fetched",
        "verified_bootstrap_bundle": {**_bootstrap_bundle(), "weight": 1.25},
    }

    with pytest.raises(ValueError, match="bootstrap_fetch_bundle_float_not_allowed"):
        record_invite_bootstrap_capsule_evidence(
            tmp_path,
            agent_id=agent["agent_id"],
            current_epoch=0,
            capsule_evidence=evidence,
            distributed_fetch_evidence=fetch_evidence,
        )


def test_fetch_distributed_release_peers_rejects_unpinned_trust_root() -> None:
    with pytest.raises(ValueError, match="bootstrap_fetch_trust_root_not_configured"):
        fetch_distributed_release_peers(
            _fetch_bundle_material(),
            {"known_peer_hints_verified": 0},
        )


def test_fetch_distributed_release_peers_rejects_too_many_peers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ilc_core.network.d2d import bootstrap_fetch_runtime

    monkeypatch.setattr(
        bootstrap_fetch_runtime,
        "fetch_bootstrap_bundle",
        lambda _seed, _cid: _bootstrap_bundle(),
    )
    monkeypatch.setattr(
        bootstrap_fetch_runtime,
        "verify_bootstrap_bundle_signature",
        lambda _bundle, _pubkey: True,
    )
    monkeypatch.setattr(
        bootstrap_fetch_runtime,
        "extract_peer_endpoints",
        lambda _bundle: [
            f"https://peer-{index}.ilc.example:443"
            for index in range(MAX_BOOTSTRAP_FETCH_PEERS + 1)
        ],
    )

    with pytest.raises(ValueError, match="bootstrap_fetch_peer_endpoints_too_many"):
        fetch_distributed_release_peers(
            _fetch_bundle_material(),
            {"known_peer_hints_verified": 0},
            trusted_genesis_authority_pubkey_hex=MLDSA_PUBKEY_HEX,
        )


def test_record_capsule_evidence_rejects_invalid_fetch_endpoint(tmp_path: Path) -> None:
    agent = provision_new_identity(tmp_path, invite_id="invite-a", emit_warning=False)
    evidence = validate_invite_bootstrap_capsule_fields({}, current_epoch=0)
    fetch_evidence = {
        **_fetch_bundle_material(),
        "bootstrap_fetch_peer_endpoints": ["http://peer-a.ilc.example:443"],
        "bootstrap_fetch_peers_count": 1,
        "bootstrap_fetch_status": "fetched",
        "verified_bootstrap_bundle": _bootstrap_bundle(),
    }

    with pytest.raises(ValueError, match="bootstrap_fetch_peer_endpoint_invalid"):
        record_invite_bootstrap_capsule_evidence(
            tmp_path,
            agent_id=agent["agent_id"],
            current_epoch=0,
            capsule_evidence=evidence,
            distributed_fetch_evidence=fetch_evidence,
        )


def test_record_capsule_evidence_leaves_pending_marker_on_split_write_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    agent = provision_new_identity(tmp_path, invite_id="invite-a", emit_warning=False)
    evidence = validate_invite_bootstrap_capsule_fields({}, current_epoch=0)
    root = identity_root(tmp_path)
    original_atomic_write_json = provisioning._atomic_write_json  # noqa: SLF001

    def fail_on_onboarding_update(path: Path, payload: dict[str, Any], *, mode: int) -> None:
        if path.name == "onboarding_receipt.json" and "bootstrap_fetch_status" in payload:
            raise OSError("simulated split write")
        original_atomic_write_json(path, payload, mode=mode)

    monkeypatch.setattr(provisioning, "_atomic_write_json", fail_on_onboarding_update)

    with pytest.raises(OSError, match="simulated split write"):
        record_invite_bootstrap_capsule_evidence(
            tmp_path,
            agent_id=agent["agent_id"],
            current_epoch=0,
            capsule_evidence=evidence,
        )

    assert (root / "invite_bootstrap_capsule_evidence.pending.json").is_file()


def test_read_json_object_rejects_non_finite_json(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text('{"agent_id":NaN}', encoding="utf-8")

    with pytest.raises(ValueError, match="onboarding_receipt_invalid"):
        provisioning._read_json_object(path, "onboarding_receipt_invalid")  # noqa: SLF001
