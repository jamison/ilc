from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest

from ilc_core.consensus import (
    ADR_0028_PRODUCTION_BRIDGE_PARTIAL_TOKEN,
    GET_EPOCH_GET_BALANCE_GET_EPOCH_RECORD_GET_EPOCH_CHAIN_TOKEN,
    ILC_CORE_CONSENSUS_GRPC_ADAPTER_VERSION,
    LIVE_ECU_TRANSFER_NOT_ACTIVATED_TOKEN,
    PRODUCTION_BRIDGE_ACTIVE,
    QUIC_ECU_TRANSFER_SUBMISSION_PATH_TOKEN,
    TESTBED_STUBS_REPLACED_PRODUCTION_PATH_TOKEN,
    ConsensusBridgeConfig,
    ILCConsensusGrpcReadAdapter,
    build_quic_ecu_transfer_submission_path,
    build_secure_grpc_read_stub,
    quote_to_canonical_json,
    submit_ecu_transfer_via_quic,
)


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


def _adapter(stub: FakeReadStub, *, timeout: int = 7) -> ILCConsensusGrpcReadAdapter:
    return ILCConsensusGrpcReadAdapter(
        ConsensusBridgeConfig(
            target="validator.example:443",
            grpc_timeout_seconds=timeout,
            max_epoch_chain_records=4,
        ),
        stub=stub,
    )


def test_phase_1358_tokens_and_default_off_exported() -> None:
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
    assert PRODUCTION_BRIDGE_ACTIVE is False


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
    assert quote.production_bridge_active is False
    assert quote_to_canonical_json(quote) == (
        '{"agent_id_length_bytes":48,"amount_ecu":"1.234567",'
        '"amount_micro_ecu":"1234567","epoch":8,'
        '"production_bridge_active":false,"version":4}'
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
    assert path.production_bridge_active is False
    assert quote_to_canonical_json(path).startswith('{"path_token":"quic_ecu_transfer')
    with pytest.raises(ValueError, match="live_ecu_transfer_not_activated_phase_1358"):
        submit_ecu_transfer_via_quic(path)


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


def test_ilc_core_does_not_import_testbed_generated_grpc_stubs() -> None:
    offenders: list[str] = []
    for path in Path("ilc_core").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "tools.testbed" in text or "tools/testbed" in text or "ilc_app_pb2" in text:
            offenders.append(str(path))
    assert offenders == []

    source = Path("ilc_core/consensus/production_bridge.py").read_text(encoding="utf-8")
    assert "insecure_channel" not in source
    assert "records = list(" not in source
    assert "import random" not in source
    assert "assert " not in source
