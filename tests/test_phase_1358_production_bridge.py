from __future__ import annotations

import hashlib
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest

from ilc_core.consensus import (
    ADR_0028_PRODUCTION_BRIDGE_PARTIAL_TOKEN,
    GET_EPOCH_GET_BALANCE_GET_EPOCH_RECORD_GET_EPOCH_CHAIN_TOKEN,
    ILC_CORE_CONSENSUS_GRPC_ADAPTER_VERSION,
    LIVE_ECU_TRANSFER_NOT_ACTIVATED_TOKEN,
    MAX_PROPOSAL_BODY_BYTES,
    MAX_PROPOSAL_GRPC_OVERHEAD_BYTES,
    PRODUCTION_BRIDGE_ACTIVE,
    PRODUCTION_BRIDGE_ACTIVATED_PHASE_1587_TOKEN,
    QUIC_ECU_TRANSFER_SUBMISSION_PATH_TOKEN,
    SUBMIT_EPOCH_PROPOSAL_ACCEPTED_TOKEN,
    TESTBED_STUBS_REPLACED_PRODUCTION_PATH_TOKEN,
    ConsensusBridgeConfig,
    EpochSettlementProposalSubmission,
    ILCConsensusGrpcReadAdapter,
    build_epoch_settlement_proposal_submission,
    build_quic_ecu_transfer_submission_path,
    build_secure_grpc_proposal_ingress_stub,
    build_secure_grpc_read_stub,
    quote_to_canonical_json,
    submit_ecu_transfer_via_quic,
)
from ilc_core.consensus.validator_endpoint_assertion import (
    VALIDATOR_ENDPOINT_ASSERTION_NODE_KIND,
    VALIDATOR_ENDPOINT_ASSERTION_SCHEMA_VERSION,
    validator_assertion_candidate_id,
)


GRAPH_BINDING_AGENT_ID = "a" * 96
GRAPH_BINDING_BLS_KEY = "b" * 96
GRAPH_BINDING_CERT_DER = b"phase-1358-test-validator-cert"
GRAPH_BINDING_ASSERTION = {
    "asserted_at_epoch": 0,
    "bls_public_key_hex": GRAPH_BINDING_BLS_KEY,
    "bls_signature_hex": "c" * 192,
    "genesis_witness": True,
    "grpc_endpoint": "validator.example:443",
    "node_kind": VALIDATOR_ENDPOINT_ASSERTION_NODE_KIND,
    "schema_version": VALIDATOR_ENDPOINT_ASSERTION_SCHEMA_VERSION,
    "tls_cert_not_after_utc": "2036-01-01T00:00:00Z",
    "tls_cert_not_before_utc": "2026-01-01T00:00:00Z",
    "tls_cert_sha256_fingerprint": hashlib.sha256(GRAPH_BINDING_CERT_DER).hexdigest(),
    "validator_agent_id": GRAPH_BINDING_AGENT_ID,
}


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
        self.GetBalance = RecordingRpc(
            SimpleNamespace(amount_micro_ecu=1234567, version=4, epoch=8)
        )
        self.GetEpochRecord = RecordingRpc(
            SimpleNamespace(
                epoch=3,
                found=True,
                state_root=b"r" * 36,
                agg_sig=b"s" * 96,
            )
        )
        self.GetEpochChain = RecordingRpc(
            SimpleNamespace(
                chain_complete=True,
                records=[
                    SimpleNamespace(
                        epoch=1,
                        found=True,
                        state_root=b"a" * 36,
                        agg_sig=b"b" * 96,
                    ),
                    SimpleNamespace(
                        epoch=2,
                        found=True,
                        state_root=b"c" * 36,
                        agg_sig=b"d" * 96,
                    ),
                ],
            )
        )


class FakeProposalStub:
    def __init__(self, response: object) -> None:
        self.SubmitEpochProposal = RecordingRpc(response)


def _adapter(stub: FakeReadStub, *, timeout: int = 7) -> ILCConsensusGrpcReadAdapter:
    return ILCConsensusGrpcReadAdapter(
        ConsensusBridgeConfig(
            target="validator.example:443",
            grpc_timeout_seconds=timeout,
            max_epoch_chain_records=4,
            graph_binding_validator_agent_id=GRAPH_BINDING_AGENT_ID,
            graph_binding_expected_bls_public_key_hex=GRAPH_BINDING_BLS_KEY,
            graph_binding_network_id="ilc-testnet",
        ),
        stub=stub,
        validator_graph_binding_atlas_reader={
            validator_assertion_candidate_id(GRAPH_BINDING_AGENT_ID): GRAPH_BINDING_ASSERTION
        },
        validator_graph_binding_cert_der_provider=lambda: GRAPH_BINDING_CERT_DER,
        validator_graph_binding_bls_verifier=lambda *_args: True,
        validator_graph_binding_now_utc=datetime(2026, 6, 1, tzinfo=timezone.utc),
    )


def test_phase_1358_tokens_and_phase_1587_activation_exported() -> None:
    assert (
        ILC_CORE_CONSENSUS_GRPC_ADAPTER_VERSION
        == "ilc_core_consensus_grpc_read_adapter_phase_1358.v0.1"
    )
    assert (
        GET_EPOCH_GET_BALANCE_GET_EPOCH_RECORD_GET_EPOCH_CHAIN_TOKEN
        == "get_epoch_get_balance_get_epoch_record_get_epoch_chain_phase_1358"
    )
    assert (
        QUIC_ECU_TRANSFER_SUBMISSION_PATH_TOKEN
        == "quic_ecu_transfer_submission_path_phase_1358"
    )
    assert (
        TESTBED_STUBS_REPLACED_PRODUCTION_PATH_TOKEN
        == "testbed_stubs_replaced_production_path_phase_1358"
    )
    assert LIVE_ECU_TRANSFER_NOT_ACTIVATED_TOKEN == "live_ecu_transfer_not_activated_phase_1358"
    assert ADR_0028_PRODUCTION_BRIDGE_PARTIAL_TOKEN == "adr_0028_production_bridge_partial_phase_1358"
    assert PRODUCTION_BRIDGE_ACTIVE is True
    assert (
        PRODUCTION_BRIDGE_ACTIVATED_PHASE_1587_TOKEN
        == "production_bridge_activated_phase_1587"
    )


def test_get_epoch_and_balance_use_explicit_timeout_and_decimal_amounts() -> None:
    stub = FakeReadStub()
    adapter = _adapter(stub)

    assert adapter.get_epoch() == 9
    assert stub.GetEpoch.calls[0][1] == 7

    quote = adapter.get_balance(bytes([1]) * 48)
    request, timeout = stub.GetBalance.calls[0]
    assert timeout == 7
    assert request.agent_id == bytes([1]) * 48
    assert quote.agent_id_length_bytes == 48
    assert quote.amount_micro_ecu == Decimal("1234567")
    assert quote.amount_ecu == Decimal("1.234567")
    assert quote.version == 4
    assert quote.epoch == 8
    assert quote.production_bridge_active is True
    assert quote_to_canonical_json(quote) == (
        '{"agent_id_length_bytes":48,"amount_ecu":"1.234567",'
        '"amount_micro_ecu":"1234567","epoch":8,'
        '"production_bridge_active":true,"version":4}'
    )


def test_get_balance_rejects_bad_agent_id_and_nonfinite_amount() -> None:
    stub = FakeReadStub()
    adapter = _adapter(stub)
    with pytest.raises(ValueError, match="agent_id_must_be_48_bytes_phase_1358"):
        adapter.get_balance(bytes([1]) * 47)

    stub.GetBalance.response = SimpleNamespace(
        amount_micro_ecu=Decimal("NaN"),
        version=1,
        epoch=1,
    )
    with pytest.raises(ValueError, match="invalid_amount_non_finite"):
        adapter.get_balance(bytes([2]) * 48)


def test_epoch_record_and_epoch_chain_are_bounded_and_timeout_explicit() -> None:
    stub = FakeReadStub()
    adapter = _adapter(stub)

    record = adapter.get_epoch_record(3)
    assert stub.GetEpochRecord.calls[0][1] == 7
    assert record.epoch == 3
    assert record.found is True
    assert record.state_root == b"r" * 36
    assert record.agg_sig == b"s" * 96

    chain = adapter.get_epoch_chain(1, 2)
    request, timeout = stub.GetEpochChain.calls[0]
    assert timeout == 7
    assert request.from_epoch == 1
    assert request.to_epoch == 2
    assert request.include_edges is False
    assert chain.chain_complete is True
    assert [entry.epoch for entry in chain.records] == [1, 2]

    fresh_stub = FakeReadStub()
    fresh_adapter = _adapter(fresh_stub)
    with pytest.raises(ValueError, match="get_epoch_chain_max_records_exceeded_phase_1358"):
        fresh_adapter.get_epoch_chain(1, 5)
    assert fresh_stub.GetEpochChain.calls == []


def test_epoch_chain_rejects_edge_expansion_for_phase_1358() -> None:
    adapter = _adapter(FakeReadStub())
    with pytest.raises(ValueError, match="epoch_chain_edges_not_enabled_phase_1358"):
        adapter.get_epoch_chain(1, 2, include_edges=True)


def test_quic_ecu_transfer_submission_path_is_present_but_not_activated() -> None:
    path = build_quic_ecu_transfer_submission_path(
        transfer_payload_digest="sha256:" + "a" * 64,
        target_quic_addr="validator.example:443",
        target_validator_id="validator-1",
        protocol_epoch=12,
    )

    assert path.path_token == "quic_ecu_transfer_submission_path_phase_1358"
    assert path.status_token == "live_ecu_transfer_not_activated_phase_1358"
    assert path.production_bridge_active is True
    assert quote_to_canonical_json(path).startswith('{"path_token":"quic_ecu_transfer')
    with pytest.raises(ValueError, match="epoch_proposal_submission_path_invalid_phase_1587"):
        submit_ecu_transfer_via_quic(
            path,  # type: ignore[arg-type]
            config=ConsensusBridgeConfig(target="validator.example:443"),
            stub=FakeProposalStub(SimpleNamespace()),
        )


def test_phase_1587_epoch_proposal_submission_calls_grpc_write_endpoint() -> None:
    settlement_record = b'{"epoch":1,"root":"canonical"}'
    state_root = bytes([7]) * 36
    submitter = bytes([3]) * 48
    submission = build_epoch_settlement_proposal_submission(
        submitter_agent_id=submitter,
        epoch_number=1,
        state_root_cidv1=state_root,
        settlement_record_bytes=settlement_record,
        not_before_unix_ms=123456789,
        network_id="ilc-mainnet-rc01",
    )
    fake_stub = FakeProposalStub(
        SimpleNamespace(
            status_token=SUBMIT_EPOCH_PROPOSAL_ACCEPTED_TOKEN,
            error_code="",
            accepted_epoch_number=1,
            accepted_state_root_cidv1=state_root,
            proposal_id=submission.idempotency_key,
        )
    )
    config = ConsensusBridgeConfig(
        target="read.example:443",
        grpc_timeout_seconds=11,
        proposal_ingress_endpoint="write.example:443",
    )

    result = submit_ecu_transfer_via_quic(submission, config=config, stub=fake_stub)

    request, timeout = fake_stub.SubmitEpochProposal.calls[0]
    assert timeout == 11
    assert request.submitter_agent_id == submitter
    assert request.epoch_number == 1
    assert request.state_root_cidv1 == state_root
    assert request.epoch_data_hash == hashlib.sha256(settlement_record).digest()
    assert request.settlement_record_bytes == settlement_record
    assert request.idempotency_key == submission.idempotency_key
    assert request.not_before_unix_ms == 123456789
    assert request.network_id == "ilc-mainnet-rc01"
    assert result.status_token == SUBMIT_EPOCH_PROPOSAL_ACCEPTED_TOKEN
    assert result.accepted_epoch_number == 1
    assert result.accepted_state_root_cidv1 == state_root
    assert result.proposal_id == submission.idempotency_key
    assert result.production_bridge_active is True


def test_phase_1587_submission_rejects_bad_config_and_payloads() -> None:
    with pytest.raises(ValueError, match="proposal_ingress_endpoint_invalid_phase_1587"):
        ConsensusBridgeConfig(target="read.example:443", proposal_ingress_endpoint="")
    with pytest.raises(ValueError, match="proposal_timeout_invalid_phase_1587"):
        ConsensusBridgeConfig(target="read.example:443", proposal_timeout_seconds=0)
    with pytest.raises(ValueError, match="max_proposal_body_bytes_invalid_phase_1587"):
        ConsensusBridgeConfig(target="read.example:443", max_proposal_body_bytes=0)
    with pytest.raises(ValueError, match="proposal_retry_count_invalid_phase_1587"):
        ConsensusBridgeConfig(target="read.example:443", proposal_retry_count=-1)
    with pytest.raises(
        ValueError,
        match="proposal_client_certificate_pair_invalid_phase_1587_fix1",
    ):
        ConsensusBridgeConfig(
            target="read.example:443",
            proposal_client_private_key=b"client-key",
        )
    with pytest.raises(
        ValueError,
        match="proposal_client_certificate_pair_invalid_phase_1587_fix1",
    ):
        ConsensusBridgeConfig(
            target="read.example:443",
            proposal_client_certificate_chain=b"client-cert",
        )

    with pytest.raises(ValueError, match="submit_epoch_proposal_state_root_invalid_phase_1587"):
        build_epoch_settlement_proposal_submission(
            submitter_agent_id=bytes([1]) * 48,
            epoch_number=1,
            state_root_cidv1=b"short",
            settlement_record_bytes=b"{}",
            not_before_unix_ms=1,
            network_id="ilc-mainnet-rc01",
        )


def test_phase_1587_submission_handles_rust_error_responses() -> None:
    submission = build_epoch_settlement_proposal_submission(
        submitter_agent_id=bytes([1]) * 48,
        epoch_number=2,
        state_root_cidv1=bytes([2]) * 36,
        settlement_record_bytes=b'{"epoch":2}',
        not_before_unix_ms=2,
        network_id="ilc-mainnet-rc01",
    )
    fake_stub = FakeProposalStub(
        SimpleNamespace(
            status_token="",
            error_code="submit_epoch_proposal_network_id_mismatch_phase_1586",
            accepted_epoch_number=0,
            accepted_state_root_cidv1=b"",
            proposal_id="",
        )
    )
    with pytest.raises(
        ValueError,
        match="submit_epoch_proposal_network_id_mismatch_phase_1586",
    ):
        submit_ecu_transfer_via_quic(
            submission,
            config=ConsensusBridgeConfig(target="validator.example:443"),
            stub=fake_stub,
        )


def test_phase_1587_submission_retries_transport_with_same_idempotency_key() -> None:
    class FlakyRpc:
        def __init__(self) -> None:
            self.calls: list[tuple[object, int]] = []

        def __call__(self, request: object, *, timeout: int) -> object:
            self.calls.append((request, timeout))
            if len(self.calls) == 1:
                raise TimeoutError("transient")
            return SimpleNamespace(
                status_token=SUBMIT_EPOCH_PROPOSAL_ACCEPTED_TOKEN,
                error_code="",
                accepted_epoch_number=3,
                accepted_state_root_cidv1=bytes([3]) * 36,
                proposal_id=request.idempotency_key,
            )

    class FlakyStub:
        def __init__(self) -> None:
            self.SubmitEpochProposal = FlakyRpc()

    submission = build_epoch_settlement_proposal_submission(
        submitter_agent_id=bytes([3]) * 48,
        epoch_number=3,
        state_root_cidv1=bytes([3]) * 36,
        settlement_record_bytes=b'{"epoch":3}',
        not_before_unix_ms=3,
        network_id="ilc-mainnet-rc01",
    )
    stub = FlakyStub()

    result = submit_ecu_transfer_via_quic(
        submission,
        config=ConsensusBridgeConfig(
            target="validator.example:443",
            grpc_timeout_seconds=13,
            proposal_retry_count=1,
        ),
        stub=stub,
    )

    first_request, first_timeout = stub.SubmitEpochProposal.calls[0]
    second_request, second_timeout = stub.SubmitEpochProposal.calls[1]
    assert first_request.idempotency_key == second_request.idempotency_key
    assert first_timeout == second_timeout == 13
    assert result.proposal_id == submission.idempotency_key


def test_phase_1587_submission_revalidates_direct_dataclass_before_network() -> None:
    valid = build_epoch_settlement_proposal_submission(
        submitter_agent_id=bytes([4]) * 48,
        epoch_number=4,
        state_root_cidv1=bytes([4]) * 36,
        settlement_record_bytes=b'{"epoch":4}',
        not_before_unix_ms=4,
        network_id="ilc-mainnet-rc01",
    )
    tampered = EpochSettlementProposalSubmission(
        submitter_agent_id=valid.submitter_agent_id,
        epoch_number=valid.epoch_number,
        state_root_cidv1=valid.state_root_cidv1,
        epoch_data_hash=bytes([9]) * 32,
        settlement_record_bytes=valid.settlement_record_bytes,
        idempotency_key=valid.idempotency_key,
        not_before_unix_ms=valid.not_before_unix_ms,
        network_id=valid.network_id,
        production_bridge_active=valid.production_bridge_active,
        activation_token=valid.activation_token,
    )
    fake_stub = FakeProposalStub(SimpleNamespace())

    with pytest.raises(
        ValueError,
        match="submit_epoch_proposal_epoch_data_hash_mismatch_phase_1587_fix1",
    ):
        submit_ecu_transfer_via_quic(
            tampered,
            config=ConsensusBridgeConfig(target="validator.example:443"),
            stub=fake_stub,
        )
    assert fake_stub.SubmitEpochProposal.calls == []


def test_phase_1587_submission_rejects_oversized_body_before_network() -> None:
    submission = build_epoch_settlement_proposal_submission(
        submitter_agent_id=bytes([5]) * 48,
        epoch_number=5,
        state_root_cidv1=bytes([5]) * 36,
        settlement_record_bytes=b"x" * (MAX_PROPOSAL_BODY_BYTES + 1),
        not_before_unix_ms=5,
        network_id="ilc-mainnet-rc01",
    )
    fake_stub = FakeProposalStub(SimpleNamespace())

    with pytest.raises(ValueError, match="submit_epoch_proposal_body_too_large_phase_1587"):
        submit_ecu_transfer_via_quic(
            submission,
            config=ConsensusBridgeConfig(target="validator.example:443"),
            stub=fake_stub,
        )
    assert fake_stub.SubmitEpochProposal.calls == []


def test_phase_1587_submission_rejects_response_proposal_id_mismatch() -> None:
    submission = build_epoch_settlement_proposal_submission(
        submitter_agent_id=bytes([6]) * 48,
        epoch_number=6,
        state_root_cidv1=bytes([6]) * 36,
        settlement_record_bytes=b'{"epoch":6}',
        not_before_unix_ms=6,
        network_id="ilc-mainnet-rc01",
    )
    fake_stub = FakeProposalStub(
        SimpleNamespace(
            status_token=SUBMIT_EPOCH_PROPOSAL_ACCEPTED_TOKEN,
            error_code="",
            accepted_epoch_number=6,
            accepted_state_root_cidv1=bytes([6]) * 36,
            proposal_id="0" * 64,
        )
    )

    with pytest.raises(
        ValueError,
        match="submit_epoch_proposal_idempotency_response_mismatch_phase_1587_fix1",
    ):
        submit_ecu_transfer_via_quic(
            submission,
            config=ConsensusBridgeConfig(target="validator.example:443"),
            stub=fake_stub,
        )


def test_phase_1587_submission_golden_vector_hash_and_idempotency() -> None:
    submission = build_epoch_settlement_proposal_submission(
        submitter_agent_id=bytes([3]) * 48,
        epoch_number=1,
        state_root_cidv1=bytes([7]) * 36,
        settlement_record_bytes=b'{"epoch":1,"root":"canonical"}',
        not_before_unix_ms=123456789,
        network_id="ilc-mainnet-rc01",
    )

    assert (
        submission.epoch_data_hash.hex()
        == "d9bb4e98479cdabbd9acce0b9df6fe1941d78666190038d83082a60ff4789aaf"
    )
    assert (
        submission.idempotency_key
        == "5f3a074b70b96f257ab73f2facefb503fc32fc7b79e9b89b869c0aaa9dfe6e3a"
    )


def test_secure_grpc_constructor_uses_secure_channel_and_tls_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: dict[str, object] = {}

    class FakeChannel:
        def unary_unary(self, path: str, **kwargs: object) -> RecordingRpc:
            calls.setdefault("paths", []).append(path)  # type: ignore[union-attr]
            assert "request_serializer" in kwargs
            assert "response_deserializer" in kwargs
            return RecordingRpc(SimpleNamespace())

    class FakeGrpcModule:
        @staticmethod
        def ssl_channel_credentials(root_certificates: bytes | None = None) -> str:
            calls["roots"] = root_certificates
            return "tls-creds"

        @staticmethod
        def secure_channel(
            target: str,
            credentials: str,
            options: tuple[tuple[str, int], ...] = (),
        ) -> FakeChannel:
            calls["target"] = target
            calls["credentials"] = credentials
            calls["options"] = options
            return FakeChannel()

    monkeypatch.setitem(sys.modules, "grpc", FakeGrpcModule)
    stub = build_secure_grpc_read_stub(
        ConsensusBridgeConfig(
            target="validator.example:443",
            tls_root_certificates=b"root-ca",
        )
    )

    assert stub.GetEpoch is not None
    assert calls["roots"] == b"root-ca"
    assert calls["target"] == "validator.example:443"
    assert calls["credentials"] == "tls-creds"
    assert ("grpc.max_receive_message_length", 1_048_576) in calls["options"]
    assert "/ilc_app.ILCAppReadService/GetBalance" in calls["paths"]  # type: ignore[operator]
    assert not hasattr(FakeGrpcModule, "insecure_channel")


def test_phase_1587_secure_proposal_stub_uses_tls_and_bounded_messages(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: dict[str, object] = {}

    class FakeChannel:
        def unary_unary(self, path: str, **kwargs: object) -> RecordingRpc:
            calls["path"] = path
            assert "request_serializer" in kwargs
            assert "response_deserializer" in kwargs
            return RecordingRpc(SimpleNamespace())

    class FakeGrpcModule:
        @staticmethod
        def ssl_channel_credentials(
            root_certificates: bytes | None = None,
            private_key: bytes | None = None,
            certificate_chain: bytes | None = None,
        ) -> str:
            calls["roots"] = root_certificates
            calls["private_key"] = private_key
            calls["certificate_chain"] = certificate_chain
            return "proposal-tls-creds"

        @staticmethod
        def secure_channel(
            target: str,
            credentials: str,
            options: tuple[tuple[str, int], ...] = (),
        ) -> FakeChannel:
            calls["target"] = target
            calls["credentials"] = credentials
            calls["options"] = options
            return FakeChannel()

    monkeypatch.setitem(sys.modules, "grpc", FakeGrpcModule)
    with pytest.raises(
        ValueError,
        match="proposal_client_certificate_pair_required_phase_1587_fix1",
    ):
        build_secure_grpc_proposal_ingress_stub(
            ConsensusBridgeConfig(
                target="read.example:443",
                proposal_ingress_endpoint="write.example:443",
                proposal_tls_root_certificates=b"proposal-root-ca",
            )
        )

    stub = build_secure_grpc_proposal_ingress_stub(
        ConsensusBridgeConfig(
            target="read.example:443",
            proposal_ingress_endpoint="write.example:443",
            max_proposal_body_bytes=4096,
            proposal_tls_root_certificates=b"proposal-root-ca",
            proposal_client_private_key=b"client-key",
            proposal_client_certificate_chain=b"client-cert",
        )
    )

    assert stub.SubmitEpochProposal is not None
    assert calls["roots"] == b"proposal-root-ca"
    assert calls["private_key"] == b"client-key"
    assert calls["certificate_chain"] == b"client-cert"
    assert calls["target"] == "write.example:443"
    assert calls["credentials"] == "proposal-tls-creds"
    assert (
        "grpc.max_send_message_length",
        4096 + MAX_PROPOSAL_GRPC_OVERHEAD_BYTES,
    ) in calls["options"]
    assert ("grpc.max_receive_message_length", 1_048_576) in calls["options"]
    assert calls["path"] == "/ilc_app.ILCAppProposalIngressService/SubmitEpochProposal"
    assert not hasattr(FakeGrpcModule, "insecure_channel")


def test_ilc_core_does_not_import_testbed_generated_grpc_stubs() -> None:
    offenders: list[str] = []
    for path in Path("ilc_core/consensus").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "tools.testbed" in text or "tools/testbed" in text or "ilc_app_pb2" in text:
            offenders.append(str(path))
    assert offenders == []

    source = Path("ilc_core/consensus/production_bridge.py").read_text(encoding="utf-8")
    assert "insecure_channel" not in source
    assert "records = list(" not in source
    assert "import random" not in source
    assert "assert " not in source
