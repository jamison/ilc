# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any

import pytest

from ilc_core.network.d2d import spectral_route_token as srt
from ilc_core.network.d2d.spectral_beacon import (
    CCSS_SPECTRAL_ROUTE_TOKEN_ENVELOPE_VERSION,
    SealedSpectralBeaconEnvelope,
    SpectralBeaconValidationError,
    _sanitize_h013_transport_headers,
    build_h013_gossip_envelope,
    build_spectral_route_token_envelope,
    validate_relay_envelope,
)
from ilc_core.network.d2d.spectral_sigma_policy import SIGMA_POLICY_STATUS


REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = REPO_ROOT / "docs" / "phases" / "STATUS.md"
HTTP_RUNTIME_PATH = REPO_ROOT / "ilc_core" / "network" / "d2d" / "http_gossip_transport_runtime.py"
SPECTRAL_BEACON_PATH = REPO_ROOT / "ilc_core" / "network" / "d2d" / "spectral_beacon.py"
SPECTRAL_ROUTE_TOKEN_PATH = REPO_ROOT / "ilc_core" / "network" / "d2d" / "spectral_route_token.py"

STRICTLY_FORBIDDEN_RELAY_KEYS = {
    "lambda_local",
    "lambda_vector",
    "eigenvalue",
    "eigenvalues",
    "spectral_fingerprint",
    "noise_sigma",
    "sigma",
    "agent_id",
    "sender_agent_id",
    "recipient_agent_id",
    "recipient_public_key",
    "raw_contact_capability_id",
    "commitment_salt",
}


def _assert_forbidden_keys_absent(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            assert key not in STRICTLY_FORBIDDEN_RELAY_KEYS
            _assert_forbidden_keys_absent(nested)
    elif isinstance(value, list):
        for nested in value:
            _assert_forbidden_keys_absent(nested)


def test_phase_1573p_spectral_route_token_envelope_has_only_allowed_relay_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(srt, "CCSS_SPECTRAL_01_NOT_ACTIVATED", False)

    recipient_public_key, _recipient_private_key = srt.generate_hybrid_recipient_keypair()
    envelope = build_spectral_route_token_envelope(
        lambda_local=[0.125, 0.25, 0.375],
        recipient_pk_bytes=recipient_public_key,
        epoch=11,
        epoch_root=b"phase-1573p-epoch-root",
        raw_cap_id="capability:receiver:phase-1573p",
        route_purpose=b"direct-message",
    )

    assert set(envelope) == {
        "capability_context_commitment",
        "ccss_spectral_version",
        "epoch",
        "hiding_commitment",
        "kem_ciphertext",
        "message_nonce",
        "route_purpose",
        "route_token",
        "sender_ephemeral_pubkey",
    }
    assert set(envelope).issubset(srt.CCSS_SPECTRAL_ALLOWED_CLEARTEXT_FIELDS)
    assert envelope["ccss_spectral_version"] == CCSS_SPECTRAL_ROUTE_TOKEN_ENVELOPE_VERSION
    assert envelope["epoch"] == 11
    assert envelope["route_purpose"] == "direct-message"
    _assert_forbidden_keys_absent(envelope)
    validate_relay_envelope(envelope)


def test_phase_1573p_relay_validator_rejects_nested_identity_and_spectral_fields() -> None:
    forbidden_examples = [
        {"outer": [{"lambda_local": [0.1, 0.2]}]},
        {"headers": {"recipient_public_key": "not-allowed"}},
        {"payload": {"sender_agent_id": "agent:sender"}},
        {"payload": {"recipient_agent_id": "agent:recipient"}},
        {"payload": {"raw_contact_capability_id": "cap:raw"}},
        {"payload": {"commitment_salt": "00" * 32}},
    ]

    for envelope in forbidden_examples:
        with pytest.raises(SpectralBeaconValidationError) as exc:
            validate_relay_envelope(envelope)
        assert exc.value.token == "ccss_spectral_forbidden_wire_field_present"


def test_phase_1573p_route_purpose_is_coarse_enum_only() -> None:
    assert srt.CCSS_SPECTRAL_ROUTE_PURPOSE_VALUES == {
        "bootstrap",
        "direct-message",
        "query",
        "relay",
    }
    assert "agent" not in srt.CCSS_SPECTRAL_ROUTE_PURPOSE_VALUES
    assert "recipient" not in srt.CCSS_SPECTRAL_ROUTE_PURPOSE_VALUES
    assert "topic" not in srt.CCSS_SPECTRAL_ROUTE_PURPOSE_VALUES


def test_phase_1573p_h013_transport_header_aliases_fail_closed() -> None:
    forbidden_headers = [
        "lambda_local",
        "noise-sigma",
        "agent.id",
        "sender-peer-id",
        "schema-ref",
        "raw_spectral_coordinates",
        "route-history",
        "cluster.membership",
        "topic",
    ]

    for header in forbidden_headers:
        with pytest.raises(SpectralBeaconValidationError) as exc:
            _sanitize_h013_transport_headers({header: "x"})
        assert exc.value.token == "h013_transport_header_forbidden"

    assert _sanitize_h013_transport_headers({"X-Trace-Class": "coarse"}) == {
        "x-trace-class": "coarse"
    }


def test_phase_1573p_h013_gossip_envelope_has_no_spectral_or_agent_forbidden_fields() -> None:
    sealed = SealedSpectralBeaconEnvelope(
        relay_peer_id="peer:relay-1573p",
        channel_id="cid:1573abcdefabcdefabcdefabcdefabcd",
        emission_id="h013-emission-1573p",
        sealed_outer=b"opaque-sealed-bytes",
    )

    envelope = build_h013_gossip_envelope(
        sealed_envelope=sealed,
        payload_cid="bafyphase1573pmetadataaudit",
        transport_headers={"X-Trace-Class": "coarse"},
    )

    assert envelope["sender_peer_id"] == "peer:relay-1573p"
    assert envelope["transport_headers"]["schema_ref"] == "h013_sealed_spectral_beacon.v0.1"
    assert envelope["transport_headers"]["topic"] == "spectral.beacon.sealed"
    _assert_forbidden_keys_absent(envelope)
    validate_relay_envelope(envelope)


def test_phase_1573p_http_log_surface_does_not_record_route_token_internals() -> None:
    source = HTTP_RUNTIME_PATH.read_text(encoding="utf-8")
    forbidden_log_terms = {
        "lambda_local",
        "lambda_vector",
        "eigenvalue",
        "eigenvalues",
        "spectral_fingerprint",
        "noise_sigma",
        "raw_contact_capability_id",
        "commitment_salt",
        "recipient_public_key",
        "recipient_agent_id",
        "sender_agent_id",
        "route_token",
        "hiding_commitment",
        "kem_ciphertext",
    }

    for term in forbidden_log_terms:
        assert term not in source
    assert "payload_sha256" in source
    assert "signature_sha256" in source
    assert "content_length" in source


def test_phase_1573p_source_validators_remain_guarded_and_guard_independent() -> None:
    beacon_source = SPECTRAL_BEACON_PATH.read_text(encoding="utf-8")
    route_source = SPECTRAL_ROUTE_TOKEN_PATH.read_text(encoding="utf-8")

    assert "if srt.CCSS_SPECTRAL_01_NOT_ACTIVATED:" in beacon_source
    assert "validate_relay_envelope" in beacon_source
    assert "srt.validate_no_forbidden_fields(envelope)" in beacon_source
    assert "CCSS_SPECTRAL_01_NOT_ACTIVATED = True" in route_source
    assert list(inspect.signature(validate_relay_envelope).parameters) == ["envelope"]
    assert SIGMA_POLICY_STATUS == "sigma_local_simulation_only_cdl_sigma_01_ratified"


def test_phase_1573p_status_tokens_record_metadata_leakage_audit() -> None:
    text = STATUS_PATH.read_text(encoding="utf-8")
    assert "ccss_metadata_leakage_audit_committed_phase_1573p" in text
    assert "ccss_relay_visible_field_inventory_committed_phase_1573p" in text
    assert "ccss_no_lambda_or_identity_wire_leak_tests_pass_phase_1573p" in text
    assert "ccss_log_surface_privacy_review_committed_phase_1573p" in text
    assert "public_path_remains_blocked_phase_1573p" in text
