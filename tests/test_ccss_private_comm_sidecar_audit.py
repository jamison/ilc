"""Regression tests for CCSS private communication sidecar hardening."""

from __future__ import annotations

import pytest

from tools.ccss_send.ccss_chat_ui import (
    _build_sent_record as build_chat_sent_record,
    _contact_public_view,
)
from tools.ccss_send.ccss_cli import _build_sent_record as build_cli_sent_record
from tools.ccss_send.ccss_encrypt import seal_message
from tools.ccss_send.ccss_identity import generate_identity
from tools.ccss_send.ccss_transport import DirectTransport, TorTransport
from tools.ccss_send.ccss_unseal import CCSSUnsealError, unseal_message


def test_cli_sent_record_redacts_plaintext_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CCSS_STORE_SENT_PLAINTEXT", raising=False)
    record = build_cli_sent_record(
        ts=1,
        contact_id="genesis",
        message="sensitive note",
        receipt="r" * 64,
        transport="tor",
    )
    assert "message" not in record
    assert record["plaintext_stored"] is False
    assert record["message_bytes"] == len("sensitive note".encode("utf-8"))
    assert len(record["message_sha256"]) == 64


def test_chat_sent_record_plaintext_requires_explicit_opt_in(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CCSS_STORE_SENT_PLAINTEXT", "1")
    record = build_chat_sent_record(
        ts=1,
        contact_id="genesis",
        message="debug note",
        receipt="r" * 64,
        transport="direct",
    )
    assert record["plaintext_stored"] is True
    assert record["message"] == "debug note"


def test_contact_public_view_treats_direct_endpoint_as_configured() -> None:
    contact = {
        "id": "agent-a",
        "name": "Agent A",
        "agent_id": "AGENT_ID_PLACEHOLDER",
        "ccss_recipient_pubkey": "ab" * 32,
        "ccss_contact_onion": "ONION_ADDRESS_PLACEHOLDER",
        "ccss_peer_endpoint": "127.0.0.1:9001",
    }
    view = _contact_public_view(contact)
    assert view["configured"] is True
    assert view["peer_endpoint"] == "127.0.0.1:9001"
    assert view["transports"] == ["direct"]


def test_direct_transport_rejects_invalid_port_before_connect() -> None:
    with pytest.raises(ValueError, match="invalid direct endpoint port"):
        DirectTransport().send(b"\0" * 4156, "127.0.0.1:70000")


def test_tor_transport_rejects_non_onion_before_socket_use() -> None:
    with pytest.raises(ValueError, match="\\.onion"):
        TorTransport().send(b"\0" * 4156, "example.com")


def test_contact_protocol_does_not_claim_live_endpoint_activation() -> None:
    text = open(
        "docs/contact/genesis_agent_contact_protocol_v0.1.md",
        encoding="utf-8",
    ).read()
    assert "public contact endpoint activated" not in text
    assert "activation remains pending concrete deployment-time values" in text


def test_private_identity_round_trip_unseals_ccss_envelope(tmp_path) -> None:
    identity_path = tmp_path / "identity.json"
    contact_path = tmp_path / "contact.json"
    result = generate_identity(
        contact_id="vps-user",
        name="VPS User",
        description="private test user",
        identity_path=identity_path,
        contact_path=contact_path,
        peer_endpoint="100.72.17.38:9001",
    )
    assert result["ok"] is True
    assert identity_path.stat().st_mode & 0o777 == 0o600

    import json

    identity = json.loads(identity_path.read_text())
    contact = json.loads(contact_path.read_text())
    assert "ccss_private_key_hex" not in contact
    assert contact["ccss_peer_endpoint"] == "100.72.17.38:9001"

    envelope = seal_message("hello private CCSS", contact["ccss_recipient_pubkey"])
    opened = unseal_message(envelope, identity["ccss_private_key_hex"])
    assert opened["message"] == "hello private CCSS"
    assert opened["message_bytes"] == len("hello private CCSS".encode("utf-8"))
    assert len(opened["envelope_sha256"]) == 64


def test_unseal_fails_with_wrong_private_key(tmp_path) -> None:
    recipient_identity = tmp_path / "recipient_identity.json"
    recipient_contact = tmp_path / "recipient_contact.json"
    wrong_identity = tmp_path / "wrong_identity.json"
    wrong_contact = tmp_path / "wrong_contact.json"
    generate_identity(
        contact_id="recipient",
        name="Recipient",
        description="recipient",
        identity_path=recipient_identity,
        contact_path=recipient_contact,
    )
    generate_identity(
        contact_id="wrong",
        name="Wrong",
        description="wrong",
        identity_path=wrong_identity,
        contact_path=wrong_contact,
    )

    import json

    recipient = json.loads(recipient_contact.read_text())
    wrong = json.loads(wrong_identity.read_text())
    envelope = seal_message("not for wrong key", recipient["ccss_recipient_pubkey"])
    with pytest.raises(CCSSUnsealError, match="ccss_layer_authentication_failed"):
        unseal_message(envelope, wrong["ccss_private_key_hex"])
