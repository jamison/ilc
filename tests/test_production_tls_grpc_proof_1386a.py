from __future__ import annotations

import concurrent.futures
import datetime as dt
import hashlib
import ipaddress
import sys
from pathlib import Path
from types import SimpleNamespace

import grpc
import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from ilc_core.consensus.production_bridge import (
    MAX_EPOCH_CHAIN_RECEIVE_BYTES,
    ConsensusBridgeConfig,
    ILCConsensusGrpcReadAdapter,
    build_secure_grpc_read_stub,
)
from ilc_core.consensus.validator_endpoint_assertion import (
    VALIDATOR_ENDPOINT_ASSERTION_NODE_KIND,
    VALIDATOR_ENDPOINT_ASSERTION_SCHEMA_VERSION,
    validator_assertion_candidate_id,
)


REPO = Path(__file__).resolve().parents[1]
PRODUCTION_BRIDGE = REPO / "ilc_core/consensus/production_bridge.py"
RUST_MAIN = REPO / "ilc_consensus/src/main.rs"
RUST_CONFIG = REPO / "ilc_consensus/src/config.rs"
PROOF = REPO / "docs/specs/ilc_production_tls_grpc_proof_1386a_v0.1.md"
WALKTHROUGH = REPO / "docs/phases/phase_1386a_production_tls_grpc_proof_walkthrough.md"
GRAPH_BINDING_AGENT_ID = "a" * 96
GRAPH_BINDING_BLS_KEY = "b" * 96
GRAPH_BINDING_CERT_DER = b"phase-1386a-test-validator-cert"


def _atlas_for_cert(cert_der: bytes) -> dict[str, dict[str, object]]:
    return {
        validator_assertion_candidate_id(GRAPH_BINDING_AGENT_ID): {
            "asserted_at_epoch": 0,
            "bls_public_key_hex": GRAPH_BINDING_BLS_KEY,
            "bls_signature_hex": "c" * 192,
            "genesis_witness": True,
            "grpc_endpoint": "validator.testnet.invalid:50162",
            "node_kind": VALIDATOR_ENDPOINT_ASSERTION_NODE_KIND,
            "schema_version": VALIDATOR_ENDPOINT_ASSERTION_SCHEMA_VERSION,
            "tls_cert_not_after_utc": "2036-01-01T00:00:00Z",
            "tls_cert_not_before_utc": "2026-01-01T00:00:00Z",
            "tls_cert_sha256_fingerprint": hashlib.sha256(cert_der).hexdigest(),
            "validator_agent_id": GRAPH_BINDING_AGENT_ID,
        }
    }


def _graph_bound_config(target: str, **overrides: object) -> ConsensusBridgeConfig:
    return ConsensusBridgeConfig(
        target=target,
        graph_binding_validator_agent_id=GRAPH_BINDING_AGENT_ID,
        graph_binding_expected_bls_public_key_hex=GRAPH_BINDING_BLS_KEY,
        graph_binding_network_id="ilc-testnet",
        **overrides,
    )


class _RecordingChannel:
    def __init__(self) -> None:
        self.paths: list[str] = []

    def unary_unary(self, path: str, **kwargs: object) -> object:
        self.paths.append(path)
        assert "request_serializer" in kwargs
        assert "response_deserializer" in kwargs
        return object()


def _localhost_cert() -> tuple[bytes, bytes]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
    now = dt.datetime.now(dt.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - dt.timedelta(minutes=1))
        .not_valid_after(now + dt.timedelta(hours=1))
        .add_extension(
            x509.SubjectAlternativeName(
                [
                    x509.DNSName("localhost"),
                    x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
                ]
            ),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )
    cert_pem = cert.public_bytes(serialization.Encoding.PEM)
    key_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    return cert_pem, key_pem


def test_secure_stub_uses_tls_roots_and_channel_receive_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: dict[str, object] = {}
    channel = _RecordingChannel()

    class FakeGrpc:
        @staticmethod
        def ssl_channel_credentials(root_certificates: bytes | None = None) -> str:
            calls["roots"] = root_certificates
            return "tls-creds"

        @staticmethod
        def secure_channel(
            target: str,
            credentials: str,
            options: tuple[tuple[str, int], ...] = (),
        ) -> _RecordingChannel:
            calls["target"] = target
            calls["credentials"] = credentials
            calls["options"] = options
            return channel

    monkeypatch.setitem(sys.modules, "grpc", FakeGrpc)

    config = ConsensusBridgeConfig(
        target="validator.testnet.invalid:50162",
        tls_root_certificates=b"test-root-ca",
        max_epoch_chain_receive_bytes=123_456,
    )
    stub = build_secure_grpc_read_stub(config)

    assert stub.GetEpoch is not None
    assert calls["roots"] == b"test-root-ca"
    assert calls["target"] == "validator.testnet.invalid:50162"
    assert calls["credentials"] == "tls-creds"
    assert ("grpc.max_receive_message_length", 123_456) in calls["options"]
    assert "/ilc_app.ILCAppReadService/GetEpochChain" in channel.paths
    assert not hasattr(FakeGrpc, "insecure_channel")


def test_epoch_chain_receive_limit_config_validation() -> None:
    assert MAX_EPOCH_CHAIN_RECEIVE_BYTES == 1_048_576
    with pytest.raises(ValueError, match="consensus_bridge_max_receive_bytes_invalid_phase_1386a"):
        ConsensusBridgeConfig(
            target="validator.testnet.invalid:50162",
            max_epoch_chain_receive_bytes=0,
        )
    with pytest.raises(ValueError, match="consensus_bridge_max_receive_bytes_invalid_phase_1386a"):
        ConsensusBridgeConfig(
            target="validator.testnet.invalid:50162",
            max_epoch_chain_receive_bytes=True,
        )


def test_epoch_chain_response_records_are_bounded_before_materialization() -> None:
    source = PRODUCTION_BRIDGE.read_text()
    assert "records = list(" not in source
    assert "for record in getattr(response, \"records\", ())" in source
    assert "len(records) >= self.config.max_epoch_chain_records" in source


class _RecordingRpc:
    def __init__(self, response: object) -> None:
        self.response = response
        self.calls: list[tuple[object, float]] = []

    def __call__(self, request: object, *, timeout: float) -> object:
        self.calls.append((request, timeout))
        return self.response


class _SentinelStub:
    def __init__(self) -> None:
        self.GetEpochChain = _RecordingRpc(
            SimpleNamespace(chain_complete=True, records=())
        )


def test_epoch_0_sentinel_reconciliation_python_sends_rust_sentinel_range() -> None:
    stub = _SentinelStub()
    adapter = ILCConsensusGrpcReadAdapter(
        _graph_bound_config("validator.testnet.invalid:50162"),
        stub=stub,
        validator_graph_binding_atlas_reader=_atlas_for_cert(GRAPH_BINDING_CERT_DER),
        validator_graph_binding_cert_der_provider=lambda: GRAPH_BINDING_CERT_DER,
        validator_graph_binding_bls_verifier=lambda *_args: True,
        validator_graph_binding_now_utc=dt.datetime(2026, 6, 1, tzinfo=dt.timezone.utc),
    )
    chain = adapter.get_epoch_chain(0, 0)

    assert len(stub.GetEpochChain.calls) == 1
    request, timeout = stub.GetEpochChain.calls[0]
    assert request.from_epoch == 0
    assert request.to_epoch == 0
    assert timeout == adapter.config.grpc_timeout_seconds
    assert chain.chain_complete is True
    assert chain.records == ()

    rust = (REPO / "ilc_consensus/src/app_interface.rs").read_text()
    assert "let from = if req.from_epoch == 0" in rust
    assert "let to = if req.to_epoch == 0 || req.to_epoch > current" in rust
    assert "let expected_count = if from <= to { to - from + 1 } else { 0 }" in rust


def test_rust_validator_grpc_server_is_tls_configured() -> None:
    main = RUST_MAIN.read_text()
    config = RUST_CONFIG.read_text()
    assert "use tonic::transport::{" in main
    assert "Identity" in main
    assert "ServerTlsConfig" in main
    assert "TLS gRPC server listening" in main
    assert ".tls_config(tls_config)" in main
    assert "Identity::from_pem(cfg.my_cert_pem.clone(), cfg.my_key_pem.clone())" in main
    assert "pub my_cert_pem: Vec<u8>" in config
    assert "pub my_key_pem: Vec<u8>" in config


def test_secure_stub_reaches_local_tls_endpoint() -> None:
    cert_pem, key_pem = _localhost_cert()
    server_credentials = grpc.ssl_server_credentials(((key_pem, cert_pem),))
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=1))
    port = server.add_secure_port("127.0.0.1:0", server_credentials)
    assert port > 0
    messages = ILCConsensusGrpcReadAdapter(
        ConsensusBridgeConfig(target="unused"),
        stub=object(),
    ).messages

    def get_epoch(request: object, context: grpc.ServicerContext) -> object:
        return messages.GetEpochResponse(current_epoch=0)

    handler = grpc.method_handlers_generic_handler(
        "ilc_app.ILCAppReadService",
        {
            "GetEpoch": grpc.unary_unary_rpc_method_handler(
                get_epoch,
                request_deserializer=messages.GetEpochRequest.FromString,
                response_serializer=messages.GetEpochResponse.SerializeToString,
            )
        },
    )
    server.add_generic_rpc_handlers((handler,))
    server.start()
    try:
        cert_der = x509.load_pem_x509_certificate(cert_pem).public_bytes(
            serialization.Encoding.DER
        )
        config = _graph_bound_config(
            target=f"127.0.0.1:{port}",
            tls_root_certificates=cert_pem,
            grpc_timeout_seconds=3,
        )
        adapter = ILCConsensusGrpcReadAdapter(
            config,
            validator_graph_binding_atlas_reader=_atlas_for_cert(cert_der),
            validator_graph_binding_cert_der_provider=lambda: cert_der,
            validator_graph_binding_bls_verifier=lambda *_args: True,
            validator_graph_binding_now_utc=dt.datetime.now(dt.timezone.utc),
        )
        assert adapter.get_epoch() == 0
    finally:
        server.stop(grace=None)


def test_phase_1386a_proof_tokens_and_non_authorizations_recorded() -> None:
    text = PROOF.read_text() + "\n" + WALKTHROUGH.read_text()
    for token in (
        "production_tls_grpc_path_proven_phase_1386a",
        "epoch_0_sentinel_reconciliation_verified_phase_1386a",
        "get_epoch_chain_channel_limit_added_phase_1386a",
    ):
        assert token in text
    for non_claim in (
        "no production activation",
        "no live ECU transfers",
        "no CDL mutation",
    ):
        assert non_claim in text


def test_production_bridge_source_has_no_insecure_channel() -> None:
    source = PRODUCTION_BRIDGE.read_text()
    assert "grpc.insecure_channel" not in source
    assert "secure_channel" in source
    assert "grpc.max_receive_message_length" in source
    assert "records = list(" not in source
