from __future__ import annotations

import hashlib
import importlib.util
import json
from dataclasses import fields
from pathlib import Path

import pytest

from ilc_core.consensus.production_bridge import (
    VALIDATOR_CERT_GRAPH_BINDING_NOT_ACTIVATED,
    ConsensusBridgeConfig,
    ILCConsensusGrpcReadAdapter,
    verify_validator_cert_against_graph,
)
from ilc_core.consensus.validator_endpoint_assertion import (
    VALIDATOR_ENDPOINT_ASSERTION_NODE_KIND,
    VALIDATOR_ENDPOINT_ASSERTION_SCHEMA_VERSION,
    ValidatorEndpointAssertion,
    canonical_assertion_payload,
    validator_assertion_candidate_id,
    verify_bls_signature,
)


AGENT = "a" * 96
BLS_KEY = "b" * 96
OTHER_BLS_KEY = "c" * 96
SIGNATURE = "d" * 192
CERT_DER = b"phase-1577b-validator-cert-der"
FINGERPRINT = hashlib.sha256(CERT_DER).hexdigest()


def _assertion(**overrides: object) -> ValidatorEndpointAssertion:
    payload = {
        "asserted_at_epoch": 0,
        "bls_public_key_hex": BLS_KEY,
        "bls_signature_hex": SIGNATURE,
        "genesis_witness": True,
        "grpc_endpoint": "validator.example:7101",
        "node_kind": VALIDATOR_ENDPOINT_ASSERTION_NODE_KIND,
        "schema_version": VALIDATOR_ENDPOINT_ASSERTION_SCHEMA_VERSION,
        "tls_cert_not_after_utc": "2036-01-01T00:00:00Z",
        "tls_cert_not_before_utc": "2026-01-01T00:00:00Z",
        "tls_cert_sha256_fingerprint": FINGERPRINT,
        "validator_agent_id": AGENT,
        "revised_by": None,
    }
    payload.update(overrides)
    return ValidatorEndpointAssertion(**payload)


def _atlas(assertion: ValidatorEndpointAssertion) -> dict[str, dict[str, object]]:
    return {validator_assertion_candidate_id(assertion.validator_agent_id): assertion.to_dict()}


def test_assertion_dataclass_fields_match_spec() -> None:
    expected = {
        "asserted_at_epoch",
        "bls_public_key_hex",
        "bls_signature_hex",
        "genesis_witness",
        "grpc_endpoint",
        "node_kind",
        "schema_version",
        "tls_cert_not_after_utc",
        "tls_cert_not_before_utc",
        "tls_cert_sha256_fingerprint",
        "validator_agent_id",
        "revised_by",
    }
    assert {field.name for field in fields(ValidatorEndpointAssertion)} == expected


def test_canonical_payload_excludes_signature_and_witness() -> None:
    payload = json.loads(canonical_assertion_payload(_assertion()).decode("utf-8"))
    assert "bls_signature_hex" not in payload
    assert "genesis_witness" not in payload
    assert payload["validator_agent_id"] == AGENT


def test_canonical_payload_is_sort_keys_json() -> None:
    payload = canonical_assertion_payload(_assertion())
    assert payload == (
        b'{"asserted_at_epoch":0,"bls_public_key_hex":"'
        + BLS_KEY.encode("ascii")
        + b'","grpc_endpoint":"validator.example:7101","node_kind":"validator_grpc_endpoint_assertion",'
        b'"schema_version":"validator_grpc_endpoint_assertion.v0.1",'
        b'"tls_cert_not_after_utc":"2036-01-01T00:00:00Z",'
        b'"tls_cert_not_before_utc":"2026-01-01T00:00:00Z","tls_cert_sha256_fingerprint":"'
        + FINGERPRINT.encode("ascii")
        + b'","validator_agent_id":"'
        + AGENT.encode("ascii")
        + b'"}'
    )


def test_load_from_atlas_missing_raises_fail_closed() -> None:
    with pytest.raises(ValueError, match="validator_cert_assertion_not_found"):
        verify_validator_cert_against_graph(
            validator_agent_id=AGENT,
            presented_cert_der=CERT_DER,
            atlas_reader={},
            expected_bls_public_key_hex=BLS_KEY,
            network_id="ilc-testnet",
            bls_verifier=lambda *_args: True,
            graph_binding_guard=False,
        )


def test_verify_superseded_assertion_fails() -> None:
    with pytest.raises(ValueError, match="validator_cert_assertion_superseded"):
        verify_validator_cert_against_graph(
            validator_agent_id=AGENT,
            presented_cert_der=CERT_DER,
            atlas_reader=_atlas(_assertion(revised_by="revision-node-1")),
            expected_bls_public_key_hex=BLS_KEY,
            network_id="ilc-testnet",
            bls_verifier=lambda *_args: True,
            graph_binding_guard=False,
        )


def test_fingerprint_mismatch_raises() -> None:
    with pytest.raises(ValueError, match="validator_cert_fingerprint_mismatch"):
        verify_validator_cert_against_graph(
            validator_agent_id=AGENT,
            presented_cert_der=b"wrong-cert",
            atlas_reader=_atlas(_assertion()),
            expected_bls_public_key_hex=BLS_KEY,
            network_id="ilc-testnet",
            bls_verifier=lambda *_args: True,
            graph_binding_guard=False,
        )


def test_bls_invalid_raises() -> None:
    with pytest.raises(ValueError, match="validator_cert_assertion_bls_invalid"):
        verify_validator_cert_against_graph(
            validator_agent_id=AGENT,
            presented_cert_der=CERT_DER,
            atlas_reader=_atlas(_assertion()),
            expected_bls_public_key_hex=BLS_KEY,
            network_id="ilc-testnet",
            bls_verifier=lambda *_args: False,
            graph_binding_guard=False,
        )


def test_key_identity_mismatch_raises() -> None:
    with pytest.raises(ValueError, match="validator_cert_bls_key_identity_mismatch"):
        verify_validator_cert_against_graph(
            validator_agent_id=AGENT,
            presented_cert_der=CERT_DER,
            atlas_reader=_atlas(_assertion()),
            expected_bls_public_key_hex=OTHER_BLS_KEY,
            network_id="ilc-testnet",
            bls_verifier=lambda *_args: True,
            graph_binding_guard=False,
        )


def test_guard_not_activated_skips_verification() -> None:
    assert VALIDATOR_CERT_GRAPH_BINDING_NOT_ACTIVATED is True
    assert (
        verify_validator_cert_against_graph(
            validator_agent_id="not-even-hex",
            presented_cert_der=b"",
            atlas_reader=None,
            expected_bls_public_key_hex="also-bad",
            network_id="ilc-testnet",
        )
        is True
    )
    adapter = ILCConsensusGrpcReadAdapter(
        ConsensusBridgeConfig(target="validator.example:7101"),
        stub=object(),
    )
    assert (
        adapter.verify_validator_cert_against_graph(
            validator_agent_id="not-even-hex",
            presented_cert_der=b"",
            atlas_reader=None,
            expected_bls_public_key_hex="also-bad",
            network_id="ilc-testnet",
        )
        is True
    )


def test_verify_bls_signature_default_fails_closed_without_subprocess(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ILC_VALIDATOR_ENDPOINT_ASSERTION_BLS_VERIFY_COMMAND", raising=False)
    assert verify_bls_signature(_assertion(), network_id="ilc-testnet") is False


def test_generate_assertions_script_exists_and_is_importable() -> None:
    path = Path("tools/testbed/generate_validator_endpoint_assertions.py")
    assert path.exists()
    spec = importlib.util.spec_from_file_location("generate_validator_endpoint_assertions", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.DEFAULT_CONFIG_ROOT == Path("config/mysticeti_testnet_M009")
