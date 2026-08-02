from __future__ import annotations

import hashlib
import importlib.util
import json
from dataclasses import fields
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

import ilc_core.consensus.production_bridge as production_bridge_module
from ilc_core.consensus.production_bridge import (
    VALIDATOR_CERT_GRAPH_BINDING_NOT_ACTIVATED,
    ConsensusBridgeConfig,
    ILCConsensusGrpcReadAdapter,
    verify_validator_cert_against_graph,
)
from ilc_core.consensus.validator_endpoint_assertion import (
    MAX_ASSERTION_ATLAS_SCAN_NODES,
    VALIDATOR_ENDPOINT_ASSERTION_NODE_KIND,
    VALIDATOR_ENDPOINT_ASSERTION_SCHEMA_VERSION,
    ValidatorEndpointAssertion,
    assertion_content_sha256,
    assertion_valid_at,
    canonical_assertion_payload,
    load_from_atlas,
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


class EdgeAtlas:
    def __init__(
        self,
        assertion: ValidatorEndpointAssertion,
        edges: list[dict[str, object]],
    ) -> None:
        self.assertion = assertion
        self.edges = edges

    def get_node(self, candidate_id: str) -> dict[str, object] | None:
        if candidate_id == validator_assertion_candidate_id(self.assertion.validator_agent_id):
            return self.assertion.to_dict()
        return None

    def iter_edges(self) -> list[dict[str, object]]:
        return self.edges


class IterNodeAtlas:
    def __init__(self, nodes: list[dict[str, object]]) -> None:
        self.nodes = nodes

    def iter_nodes(self) -> list[dict[str, object]]:
        return self.nodes


class RecordingRpc:
    def __init__(self, response: object) -> None:
        self.response = response
        self.calls: list[tuple[object, int]] = []

    def __call__(self, request: object, *, timeout: int) -> object:
        self.calls.append((request, timeout))
        return self.response


class FakeReadStub:
    def __init__(self) -> None:
        self.GetEpoch = RecordingRpc(SimpleNamespace(current_epoch=9))


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


def test_verify_superseded_assertion_fails_from_revision_edge() -> None:
    old_candidate_id = validator_assertion_candidate_id(AGENT)
    atlas = EdgeAtlas(
        _assertion(),
        [
            {
                "edge_type": "REVISED_BY",
                "source_candidate_id": old_candidate_id,
                "target_candidate_id": "validator_grpc_endpoint_assertion:revision",
            }
        ],
    )
    with pytest.raises(ValueError, match="validator_cert_assertion_superseded"):
        verify_validator_cert_against_graph(
            validator_agent_id=AGENT,
            presented_cert_der=CERT_DER,
            atlas_reader=atlas,
            expected_bls_public_key_hex=BLS_KEY,
            network_id="ilc-testnet",
            bls_verifier=lambda *_args: True,
            graph_binding_guard=False,
            now_utc=datetime(2026, 6, 1, tzinfo=timezone.utc),
        )


def test_content_hash_scoped_revision_edge_does_not_supersede_new_assertion() -> None:
    new_cert_der = b"new-cert"
    old_assertion = _assertion(tls_cert_sha256_fingerprint="1" * 64)
    new_assertion = _assertion(
        tls_cert_sha256_fingerprint=hashlib.sha256(new_cert_der).hexdigest()
    )
    atlas = EdgeAtlas(
        new_assertion,
        [
            {
                "edge_type": "REVISED_BY",
                "source_assertion_sha256": assertion_content_sha256(old_assertion),
                "source_candidate_id": validator_assertion_candidate_id(AGENT),
                "target_assertion_sha256": assertion_content_sha256(new_assertion),
                "target_candidate_id": validator_assertion_candidate_id(AGENT),
            }
        ],
    )

    assert (
        verify_validator_cert_against_graph(
            validator_agent_id=AGENT,
            presented_cert_der=new_cert_der,
            atlas_reader=atlas,
            expected_bls_public_key_hex=BLS_KEY,
            network_id="ilc-testnet",
            bls_verifier=lambda *_args: True,
            graph_binding_guard=False,
            now_utc=datetime(2026, 6, 1, tzinfo=timezone.utc),
        )
        is True
    )


def test_iter_node_scan_selects_unsuperseded_current_head_for_same_epoch_revision() -> None:
    old_assertion = _assertion(tls_cert_sha256_fingerprint="1" * 64)
    new_assertion = _assertion(tls_cert_sha256_fingerprint="2" * 64)
    revision_edge = {
        "edge_type": "REVISED_BY",
        "source_assertion_sha256": assertion_content_sha256(old_assertion),
        "source_candidate_id": validator_assertion_candidate_id(AGENT),
        "target_assertion_sha256": assertion_content_sha256(new_assertion),
        "target_candidate_id": validator_assertion_candidate_id(AGENT),
    }

    class IterNodeEdgeAtlas(IterNodeAtlas):
        def iter_edges(self) -> list[dict[str, object]]:
            return [revision_edge]

    for nodes in ([old_assertion.to_dict(), new_assertion.to_dict()], [new_assertion.to_dict(), old_assertion.to_dict()]):
        selected = load_from_atlas(IterNodeEdgeAtlas(nodes), AGENT)
        assert assertion_content_sha256(selected) == assertion_content_sha256(new_assertion)


def test_verify_expired_assertion_fails() -> None:
    with pytest.raises(ValueError, match="validator_cert_assertion_expired"):
        verify_validator_cert_against_graph(
            validator_agent_id=AGENT,
            presented_cert_der=CERT_DER,
            atlas_reader=_atlas(_assertion(tls_cert_not_after_utc="2026-05-20T09:26:12Z")),
            expected_bls_public_key_hex=BLS_KEY,
            network_id="ilc-testnet",
            bls_verifier=lambda *_args: True,
            graph_binding_guard=False,
            now_utc=datetime(2026, 8, 1, tzinfo=timezone.utc),
        )


def test_verify_not_yet_valid_assertion_fails() -> None:
    with pytest.raises(ValueError, match="validator_cert_assertion_not_yet_valid"):
        assertion_valid_at(
            _assertion(tls_cert_not_before_utc="2026-09-01T00:00:00Z"),
            now_utc=datetime(2026, 8, 1, tzinfo=timezone.utc),
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
            now_utc=datetime(2026, 6, 1, tzinfo=timezone.utc),
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
            now_utc=datetime(2026, 6, 1, tzinfo=timezone.utc),
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
            now_utc=datetime(2026, 6, 1, tzinfo=timezone.utc),
        )


def test_graph_binding_requires_explicit_verification_instant() -> None:
    with pytest.raises(ValueError, match="validator_assertion_now_utc_required_phase_1577b_fix1"):
        verify_validator_cert_against_graph(
            validator_agent_id=AGENT,
            presented_cert_der=CERT_DER,
            atlas_reader=_atlas(_assertion()),
            expected_bls_public_key_hex=BLS_KEY,
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


def test_adapter_fails_closed_if_graph_binding_guard_is_cleared_without_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(production_bridge_module, "VALIDATOR_CERT_GRAPH_BINDING_NOT_ACTIVATED", False)
    stub = FakeReadStub()
    adapter = ILCConsensusGrpcReadAdapter(
        ConsensusBridgeConfig(target="validator.example:7101"),
        stub=stub,
    )
    with pytest.raises(
        ValueError,
        match="validator_cert_graph_binding_config_missing_phase_1577b_fix1",
    ):
        adapter.get_epoch()
    assert stub.GetEpoch.calls == []


def test_adapter_verifies_graph_binding_once_when_guard_is_cleared(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(production_bridge_module, "VALIDATOR_CERT_GRAPH_BINDING_NOT_ACTIVATED", False)
    stub = FakeReadStub()
    cert_calls = 0

    def cert_provider() -> bytes:
        nonlocal cert_calls
        cert_calls += 1
        return CERT_DER

    adapter = ILCConsensusGrpcReadAdapter(
        ConsensusBridgeConfig(
            target="validator.example:7101",
            graph_binding_validator_agent_id=AGENT,
            graph_binding_expected_bls_public_key_hex=BLS_KEY,
            graph_binding_network_id="ilc-testnet",
        ),
        stub=stub,
        validator_graph_binding_atlas_reader=_atlas(_assertion()),
        validator_graph_binding_cert_der_provider=cert_provider,
        validator_graph_binding_bls_verifier=lambda *_args: True,
        validator_graph_binding_now_utc=datetime(2026, 6, 1, tzinfo=timezone.utc),
    )

    assert adapter.get_epoch() == 9
    assert adapter.get_epoch() == 9
    assert cert_calls == 1


def test_assertion_from_dict_rejects_unknown_fields_and_short_signature() -> None:
    payload = _assertion().to_dict()
    payload["unexpected_field"] = "silent-drift"
    with pytest.raises(ValueError, match="validator_assertion_unknown_field_phase_1577b_fix1"):
        ValidatorEndpointAssertion.from_dict(payload)

    with pytest.raises(ValueError, match="validator_assertion_bls_signature_invalid_phase_1577b"):
        _assertion(bls_signature_hex="d" * 190)


def test_iter_node_scan_is_bounded() -> None:
    filler = {"node_kind": "other", "validator_agent_id": AGENT}
    atlas = IterNodeAtlas([filler.copy() for _ in range(MAX_ASSERTION_ATLAS_SCAN_NODES + 1)])
    with pytest.raises(
        ValueError,
        match="validator_cert_assertion_scan_limit_exceeded_phase_1577b_fix1",
    ):
        load_from_atlas(atlas, AGENT)


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
    assert "ILC_VALIDATOR_ENDPOINT_ASSERTION_V1" in module.DEFAULT_BLS_COMMAND or module.DEFAULT_BLS_COMMAND
