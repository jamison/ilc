# SPDX-License-Identifier: AGPL-3.0-only
"""Production bridge from ilc_core to ilc_consensus.

The bridge exposes the read-only ILCAppReadService gRPC surface plus the Phase
1587 SubmitEpochProposal ingress client. The historical QUIC transfer path name
is retained for compatibility, but end-user ECU transfer remains unauthorized.
"""

from __future__ import annotations

import importlib
import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Callable, Mapping, Protocol

from google.protobuf import descriptor_pb2, descriptor_pool, message_factory

from ilc_core.consensus.validator_endpoint_assertion import (
    BlsVerifier,
    load_from_atlas,
    verify_bls_signature,
)


ILC_CORE_CONSENSUS_GRPC_ADAPTER_VERSION = (
    "ilc_core_consensus_grpc_read_adapter_phase_1358.v0.1"
)
GET_EPOCH_GET_BALANCE_GET_EPOCH_RECORD_GET_EPOCH_CHAIN_TOKEN = (
    "get_epoch_get_balance_get_epoch_record_get_epoch_chain_phase_1358"
)
QUIC_ECU_TRANSFER_SUBMISSION_PATH_TOKEN = "quic_ecu_transfer_submission_path_phase_1358"
TESTBED_STUBS_REPLACED_PRODUCTION_PATH_TOKEN = (
    "testbed_stubs_replaced_production_path_phase_1358"
)
LIVE_ECU_TRANSFER_NOT_ACTIVATED_TOKEN = "live_ecu_transfer_not_activated_phase_1358"
ADR_0028_PRODUCTION_BRIDGE_PARTIAL_TOKEN = "adr_0028_production_bridge_partial_phase_1358"
PRODUCTION_BRIDGE_ACTIVATED_PHASE_1587_TOKEN = "production_bridge_activated_phase_1587"

PRODUCTION_BRIDGE_ACTIVE = True
VALIDATOR_CERT_GRAPH_BINDING_NOT_ACTIVATED = True
DEFAULT_GRPC_TIMEOUT_SECONDS = 5
MAX_EPOCH_CHAIN_RECORDS = 1024
MAX_EPOCH_CHAIN_RECEIVE_BYTES = 1_048_576
MAX_PROPOSAL_BODY_BYTES = 256 * 1024
MAX_PROPOSAL_GRPC_OVERHEAD_BYTES = 4096
MICRO_ECU_PER_ECU = Decimal("1000000")
UINT64_MAX = Decimal("18446744073709551615")
AGENT_ID_LENGTH_BYTES = 48
CIDV1_ROOT_LENGTH_BYTES = 36
SHA256_LENGTH_BYTES = 32
SUBMIT_EPOCH_PROPOSAL_ACCEPTED_TOKEN = "submit_epoch_proposal_accepted_phase_1586"
EPOCH_PROPOSAL_PREIMAGE_DOMAIN = b"ILC_SUBMIT_EPOCH_PROPOSAL_V1"


class UnaryUnaryRpc(Protocol):
    def __call__(self, request: Any, *, timeout: int) -> Any: ...


class ILCAppReadServiceStubProtocol(Protocol):
    GetBalance: UnaryUnaryRpc
    GetEpoch: UnaryUnaryRpc
    GetEpochRecord: UnaryUnaryRpc
    GetEpochChain: UnaryUnaryRpc


class ILCAppProposalIngressServiceStubProtocol(Protocol):
    SubmitEpochProposal: UnaryUnaryRpc


@dataclass(frozen=True)
class ConsensusBridgeConfig:
    target: str
    grpc_timeout_seconds: int = DEFAULT_GRPC_TIMEOUT_SECONDS
    max_epoch_chain_records: int = MAX_EPOCH_CHAIN_RECORDS
    max_epoch_chain_receive_bytes: int = MAX_EPOCH_CHAIN_RECEIVE_BYTES
    tls_root_certificates: bytes | None = None
    proposal_ingress_endpoint: str | None = None
    proposal_timeout_seconds: int = DEFAULT_GRPC_TIMEOUT_SECONDS
    max_proposal_body_bytes: int = MAX_PROPOSAL_BODY_BYTES
    proposal_retry_count: int = 0
    proposal_tls_root_certificates: bytes | None = None
    proposal_client_private_key: bytes | None = None
    proposal_client_certificate_chain: bytes | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.target, str) or not self.target.strip():
            raise ValueError("consensus_bridge_target_invalid_phase_1358")
        if isinstance(self.grpc_timeout_seconds, bool) or not isinstance(
            self.grpc_timeout_seconds, int
        ):
            raise ValueError("consensus_bridge_timeout_invalid_phase_1358")
        if self.grpc_timeout_seconds <= 0:
            raise ValueError("consensus_bridge_timeout_invalid_phase_1358")
        if isinstance(self.max_epoch_chain_records, bool) or not isinstance(
            self.max_epoch_chain_records, int
        ):
            raise ValueError("consensus_bridge_max_records_invalid_phase_1358")
        if self.max_epoch_chain_records <= 0:
            raise ValueError("consensus_bridge_max_records_invalid_phase_1358")
        if isinstance(self.max_epoch_chain_receive_bytes, bool) or not isinstance(
            self.max_epoch_chain_receive_bytes, int
        ):
            raise ValueError("consensus_bridge_max_receive_bytes_invalid_phase_1386a")
        if self.max_epoch_chain_receive_bytes <= 0:
            raise ValueError("consensus_bridge_max_receive_bytes_invalid_phase_1386a")
        if self.tls_root_certificates is not None and not isinstance(
            self.tls_root_certificates, bytes
        ):
            raise ValueError("consensus_bridge_tls_roots_invalid_phase_1358")
        if self.proposal_ingress_endpoint is not None and (
            not isinstance(self.proposal_ingress_endpoint, str)
            or not self.proposal_ingress_endpoint.strip()
        ):
            raise ValueError("proposal_ingress_endpoint_invalid_phase_1587")
        if isinstance(self.proposal_timeout_seconds, bool) or not isinstance(
            self.proposal_timeout_seconds, int
        ):
            raise ValueError("proposal_timeout_invalid_phase_1587")
        if self.proposal_timeout_seconds <= 0:
            raise ValueError("proposal_timeout_invalid_phase_1587")
        if isinstance(self.max_proposal_body_bytes, bool) or not isinstance(
            self.max_proposal_body_bytes, int
        ):
            raise ValueError("max_proposal_body_bytes_invalid_phase_1587")
        if self.max_proposal_body_bytes <= 0:
            raise ValueError("max_proposal_body_bytes_invalid_phase_1587")
        if isinstance(self.proposal_retry_count, bool) or not isinstance(
            self.proposal_retry_count, int
        ):
            raise ValueError("proposal_retry_count_invalid_phase_1587")
        if self.proposal_retry_count < 0:
            raise ValueError("proposal_retry_count_invalid_phase_1587")
        if self.proposal_tls_root_certificates is not None and not isinstance(
            self.proposal_tls_root_certificates, bytes
        ):
            raise ValueError("proposal_tls_roots_invalid_phase_1587")
        if self.proposal_client_private_key is not None and not isinstance(
            self.proposal_client_private_key, bytes
        ):
            raise ValueError("proposal_client_private_key_invalid_phase_1587_fix1")
        if self.proposal_client_certificate_chain is not None and not isinstance(
            self.proposal_client_certificate_chain, bytes
        ):
            raise ValueError("proposal_client_certificate_chain_invalid_phase_1587_fix1")
        if (self.proposal_client_private_key is None) != (
            self.proposal_client_certificate_chain is None
        ):
            raise ValueError("proposal_client_certificate_pair_invalid_phase_1587_fix1")


@dataclass(frozen=True)
class BalanceQuote:
    agent_id_length_bytes: int
    amount_micro_ecu: Decimal
    amount_ecu: Decimal
    version: int
    epoch: int
    production_bridge_active: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id_length_bytes": self.agent_id_length_bytes,
            "amount_ecu": _decimal_to_string(self.amount_ecu),
            "amount_micro_ecu": _decimal_to_string(self.amount_micro_ecu),
            "epoch": self.epoch,
            "production_bridge_active": self.production_bridge_active,
            "version": self.version,
        }


@dataclass(frozen=True)
class EpochRecordQuote:
    epoch: int
    found: bool
    state_root: bytes
    agg_sig: bytes

    def to_dict(self) -> dict[str, Any]:
        return {
            "agg_sig_hex": self.agg_sig.hex(),
            "epoch": self.epoch,
            "found": self.found,
            "state_root_hex": self.state_root.hex(),
        }


@dataclass(frozen=True)
class EpochChainQuote:
    from_epoch: int
    to_epoch: int
    chain_complete: bool
    records: tuple[EpochRecordQuote, ...]
    production_bridge_active: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "chain_complete": self.chain_complete,
            "from_epoch": self.from_epoch,
            "production_bridge_active": self.production_bridge_active,
            "records": [record.to_dict() for record in self.records],
            "to_epoch": self.to_epoch,
        }


@dataclass(frozen=True)
class QuicEcuTransferSubmissionPath:
    transfer_payload_digest: str
    target_quic_addr: str
    target_validator_id: str
    protocol_epoch: int
    production_bridge_active: bool
    path_token: str
    status_token: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "path_token": self.path_token,
            "production_bridge_active": self.production_bridge_active,
            "protocol_epoch": self.protocol_epoch,
            "status_token": self.status_token,
            "target_quic_addr": self.target_quic_addr,
            "target_validator_id": self.target_validator_id,
            "transfer_payload_digest": self.transfer_payload_digest,
        }


@dataclass(frozen=True)
class EpochSettlementProposalSubmission:
    submitter_agent_id: bytes
    epoch_number: int
    state_root_cidv1: bytes
    epoch_data_hash: bytes
    settlement_record_bytes: bytes
    idempotency_key: str
    not_before_unix_ms: int
    network_id: str
    production_bridge_active: bool
    activation_token: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "activation_token": self.activation_token,
            "epoch_data_hash_hex": self.epoch_data_hash.hex(),
            "epoch_number": self.epoch_number,
            "idempotency_key": self.idempotency_key,
            "network_id": self.network_id,
            "not_before_unix_ms": self.not_before_unix_ms,
            "production_bridge_active": self.production_bridge_active,
            "settlement_record_bytes_sha256": hashlib.sha256(
                self.settlement_record_bytes
            ).hexdigest(),
            "state_root_cidv1_hex": self.state_root_cidv1.hex(),
            "submitter_agent_id_hex": self.submitter_agent_id.hex(),
        }


@dataclass(frozen=True)
class EpochProposalSubmissionResult:
    status_token: str
    accepted_epoch_number: int
    accepted_state_root_cidv1: bytes
    proposal_id: str
    production_bridge_active: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted_epoch_number": self.accepted_epoch_number,
            "accepted_state_root_cidv1_hex": self.accepted_state_root_cidv1.hex(),
            "production_bridge_active": self.production_bridge_active,
            "proposal_id": self.proposal_id,
            "status_token": self.status_token,
        }


@dataclass(frozen=True)
class _MessageTypes:
    GetBalanceRequest: type[Any]
    GetBalanceResponse: type[Any]
    GetEpochRequest: type[Any]
    GetEpochResponse: type[Any]
    GetEpochRecordRequest: type[Any]
    GetEpochRecordResponse: type[Any]
    GetEpochChainRequest: type[Any]
    GetEpochChainResponse: type[Any]
    SubmitEpochProposalRequest: type[Any]
    SubmitEpochProposalResponse: type[Any]


def _decimal_to_string(value: Decimal) -> str:
    if not value.is_finite():
        raise ValueError("invalid_amount_non_finite")
    if value == Decimal("0"):
        return "0"
    rendered = format(value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered or "0"


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def quote_to_canonical_json(quote: Any) -> str:
    if not hasattr(quote, "to_dict"):
        raise ValueError("consensus_bridge_quote_not_serializable_phase_1358")
    return _canonical_json(quote.to_dict())


def _is_binary_floating_value(value: Any) -> bool:
    value_type = type(value)
    return value_type.__module__ == "builtins" and value_type.__name__ == "float"


def _parse_decimal(value: Any, token: str) -> Decimal:
    if isinstance(value, bool) or _is_binary_floating_value(value):
        raise ValueError(token)
    if isinstance(value, Decimal):
        number = value
    elif isinstance(value, int):
        number = Decimal(value)
    elif isinstance(value, str):
        try:
            number = Decimal(value)
        except InvalidOperation as exc:
            raise ValueError(token) from exc
    else:
        raise ValueError(token)
    if not number.is_finite():
        raise ValueError("invalid_amount_non_finite")
    return number


def _require_uint64_decimal(value: Any, token: str) -> Decimal:
    number = _parse_decimal(value, token)
    if number < Decimal("0") or number > UINT64_MAX:
        raise ValueError(token)
    if number != number.to_integral_value():
        raise ValueError(token)
    return number


def _require_uint64_int(value: Any, token: str) -> int:
    number = _require_uint64_decimal(value, token)
    return int(number)


def _require_bool(value: Any, token: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(token)
    return value


def _require_bytes(value: Any, token: str) -> bytes:
    if isinstance(value, bytes):
        return value
    if isinstance(value, bytearray):
        return bytes(value)
    if isinstance(value, memoryview):
        return value.tobytes()
    raise ValueError(token)


def _require_non_empty_str(value: Any, token: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(token)
    return value


def _normalize_agent_id(agent_id: bytes | bytearray | memoryview) -> bytes:
    normalized = _require_bytes(agent_id, "agent_id_must_be_48_bytes_phase_1358")
    if len(normalized) != AGENT_ID_LENGTH_BYTES:
        raise ValueError("agent_id_must_be_48_bytes_phase_1358")
    return normalized


def _require_exact_bytes(value: Any, expected_len: int, token: str) -> bytes:
    normalized = _require_bytes(value, token)
    if len(normalized) != expected_len:
        raise ValueError(token)
    return normalized


def _require_lower_sha256_hex(value: Any, token: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(token)
    if any(char not in "0123456789abcdef" for char in value):
        raise ValueError(token)
    return value


def _require_lower_sha384_hex(value: Any, token: str) -> str:
    if not isinstance(value, str) or len(value) != 96:
        raise ValueError(token)
    if any(char not in "0123456789abcdef" for char in value):
        raise ValueError(token)
    return value


def _sha256_bytes(value: bytes) -> bytes:
    return hashlib.sha256(value).digest()


def _build_epoch_proposal_preimage(
    *,
    network_id: str,
    epoch_number: int,
    submitter_agent_id: bytes,
    state_root_cidv1: bytes,
    epoch_data_hash: bytes,
    settlement_record_bytes: bytes,
    not_before_unix_ms: int,
) -> bytes:
    return b"".join(
        (
            EPOCH_PROPOSAL_PREIMAGE_DOMAIN,
            network_id.encode("utf-8"),
            epoch_number.to_bytes(8, "big"),
            submitter_agent_id,
            state_root_cidv1,
            epoch_data_hash,
            _sha256_bytes(settlement_record_bytes),
            not_before_unix_ms.to_bytes(8, "big"),
        )
    )


def _epoch_proposal_idempotency_key(
    *,
    network_id: str,
    epoch_number: int,
    submitter_agent_id: bytes,
    state_root_cidv1: bytes,
    epoch_data_hash: bytes,
    settlement_record_bytes: bytes,
    not_before_unix_ms: int,
) -> str:
    return hashlib.sha256(
        _build_epoch_proposal_preimage(
            network_id=network_id,
            epoch_number=epoch_number,
            submitter_agent_id=submitter_agent_id,
            state_root_cidv1=state_root_cidv1,
            epoch_data_hash=epoch_data_hash,
            settlement_record_bytes=settlement_record_bytes,
            not_before_unix_ms=not_before_unix_ms,
        )
    ).hexdigest()


def _expected_epoch_proposal_idempotency_key(
    submission: EpochSettlementProposalSubmission,
) -> str:
    return _epoch_proposal_idempotency_key(
        network_id=submission.network_id,
        epoch_number=submission.epoch_number,
        submitter_agent_id=submission.submitter_agent_id,
        state_root_cidv1=submission.state_root_cidv1,
        epoch_data_hash=submission.epoch_data_hash,
        settlement_record_bytes=submission.settlement_record_bytes,
        not_before_unix_ms=submission.not_before_unix_ms,
    )


def _validate_epoch_settlement_proposal_submission(
    submission: EpochSettlementProposalSubmission,
) -> None:
    _normalize_agent_id(submission.submitter_agent_id)
    _require_uint64_int(
        submission.epoch_number,
        "submit_epoch_proposal_epoch_number_invalid_phase_1587",
    )
    _require_exact_bytes(
        submission.state_root_cidv1,
        CIDV1_ROOT_LENGTH_BYTES,
        "submit_epoch_proposal_state_root_invalid_phase_1587",
    )
    _require_exact_bytes(
        submission.epoch_data_hash,
        SHA256_LENGTH_BYTES,
        "submit_epoch_proposal_epoch_data_hash_invalid_phase_1587_fix1",
    )
    _require_bytes(
        submission.settlement_record_bytes,
        "submit_epoch_proposal_settlement_record_invalid_phase_1587",
    )
    if not submission.settlement_record_bytes:
        raise ValueError("submit_epoch_proposal_settlement_record_empty_phase_1587")
    _require_uint64_int(
        submission.not_before_unix_ms,
        "submit_epoch_proposal_not_before_invalid_phase_1587",
    )
    _require_non_empty_str(
        submission.network_id,
        "submit_epoch_proposal_network_id_invalid_phase_1587",
    )
    _require_lower_sha256_hex(
        submission.idempotency_key,
        "submit_epoch_proposal_idempotency_key_invalid_phase_1587",
    )
    if submission.epoch_data_hash != _sha256_bytes(submission.settlement_record_bytes):
        raise ValueError("submit_epoch_proposal_epoch_data_hash_mismatch_phase_1587_fix1")
    if submission.idempotency_key != _expected_epoch_proposal_idempotency_key(submission):
        raise ValueError("submit_epoch_proposal_idempotency_preimage_mismatch_phase_1587")
    if submission.production_bridge_active is not PRODUCTION_BRIDGE_ACTIVE:
        raise ValueError("submit_epoch_proposal_bridge_active_flag_mismatch_phase_1587_fix1")
    if submission.activation_token != PRODUCTION_BRIDGE_ACTIVATED_PHASE_1587_TOKEN:
        raise ValueError("submit_epoch_proposal_activation_token_invalid_phase_1587_fix1")


def _add_field(
    message: descriptor_pb2.DescriptorProto,
    name: str,
    number: int,
    field_type: int,
    *,
    label: int = descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL,
    type_name: str | None = None,
) -> None:
    field = message.field.add()
    field.name = name
    field.number = number
    field.label = label
    field.type = field_type
    if type_name is not None:
        field.type_name = type_name


def _add_message(
    file_proto: descriptor_pb2.FileDescriptorProto,
    name: str,
    fields: tuple[tuple[str, int, int], ...],
) -> descriptor_pb2.DescriptorProto:
    message = file_proto.message_type.add()
    message.name = name
    for field_name, number, field_type in fields:
        _add_field(message, field_name, number, field_type)
    return message


def _build_message_types() -> _MessageTypes:
    file_proto = descriptor_pb2.FileDescriptorProto()
    file_proto.name = "ilc_app.proto"
    file_proto.package = "ilc_app"
    file_proto.syntax = "proto3"

    _add_message(
        file_proto,
        "GetBalanceRequest",
        (("agent_id", 1, descriptor_pb2.FieldDescriptorProto.TYPE_BYTES),),
    )
    _add_message(
        file_proto,
        "GetBalanceResponse",
        (
            ("amount_micro_ecu", 1, descriptor_pb2.FieldDescriptorProto.TYPE_UINT64),
            ("version", 2, descriptor_pb2.FieldDescriptorProto.TYPE_UINT64),
            ("epoch", 3, descriptor_pb2.FieldDescriptorProto.TYPE_UINT64),
        ),
    )
    _add_message(file_proto, "GetEpochRequest", ())
    _add_message(
        file_proto,
        "GetEpochResponse",
        (("current_epoch", 1, descriptor_pb2.FieldDescriptorProto.TYPE_UINT64),),
    )
    _add_message(
        file_proto,
        "GetEpochRecordRequest",
        (("epoch", 1, descriptor_pb2.FieldDescriptorProto.TYPE_UINT64),),
    )
    _add_message(
        file_proto,
        "GetEpochRecordResponse",
        (
            ("epoch", 1, descriptor_pb2.FieldDescriptorProto.TYPE_UINT64),
            ("state_root", 2, descriptor_pb2.FieldDescriptorProto.TYPE_BYTES),
            ("agg_sig", 3, descriptor_pb2.FieldDescriptorProto.TYPE_BYTES),
            ("found", 4, descriptor_pb2.FieldDescriptorProto.TYPE_BOOL),
        ),
    )
    chain_request = _add_message(file_proto, "GetEpochChainRequest", ())
    _add_field(
        chain_request,
        "from_epoch",
        1,
        descriptor_pb2.FieldDescriptorProto.TYPE_UINT64,
    )
    _add_field(
        chain_request,
        "to_epoch",
        2,
        descriptor_pb2.FieldDescriptorProto.TYPE_UINT64,
    )
    _add_field(
        chain_request,
        "include_edges",
        3,
        descriptor_pb2.FieldDescriptorProto.TYPE_BOOL,
    )
    chain_response = _add_message(file_proto, "GetEpochChainResponse", ())
    _add_field(
        chain_response,
        "records",
        1,
        descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE,
        label=descriptor_pb2.FieldDescriptorProto.LABEL_REPEATED,
        type_name=".ilc_app.GetEpochRecordResponse",
    )
    _add_field(
        chain_response,
        "chain_complete",
        4,
        descriptor_pb2.FieldDescriptorProto.TYPE_BOOL,
    )
    _add_message(
        file_proto,
        "SubmitEpochProposalRequest",
        (
            ("submitter_agent_id", 1, descriptor_pb2.FieldDescriptorProto.TYPE_BYTES),
            ("epoch_number", 2, descriptor_pb2.FieldDescriptorProto.TYPE_UINT64),
            ("state_root_cidv1", 3, descriptor_pb2.FieldDescriptorProto.TYPE_BYTES),
            ("epoch_data_hash", 4, descriptor_pb2.FieldDescriptorProto.TYPE_BYTES),
            (
                "settlement_record_bytes",
                5,
                descriptor_pb2.FieldDescriptorProto.TYPE_BYTES,
            ),
            ("idempotency_key", 6, descriptor_pb2.FieldDescriptorProto.TYPE_STRING),
            ("not_before_unix_ms", 7, descriptor_pb2.FieldDescriptorProto.TYPE_UINT64),
            ("network_id", 8, descriptor_pb2.FieldDescriptorProto.TYPE_STRING),
        ),
    )
    _add_message(
        file_proto,
        "SubmitEpochProposalResponse",
        (
            ("status_token", 1, descriptor_pb2.FieldDescriptorProto.TYPE_STRING),
            ("error_code", 2, descriptor_pb2.FieldDescriptorProto.TYPE_STRING),
            (
                "accepted_epoch_number",
                3,
                descriptor_pb2.FieldDescriptorProto.TYPE_UINT64,
            ),
            (
                "accepted_state_root_cidv1",
                4,
                descriptor_pb2.FieldDescriptorProto.TYPE_BYTES,
            ),
            ("proposal_id", 5, descriptor_pb2.FieldDescriptorProto.TYPE_STRING),
        ),
    )

    pool = descriptor_pool.DescriptorPool()
    pool.Add(file_proto)

    def message_class(name: str) -> type[Any]:
        descriptor = pool.FindMessageTypeByName(f"ilc_app.{name}")
        return message_factory.GetMessageClass(descriptor)

    return _MessageTypes(
        GetBalanceRequest=message_class("GetBalanceRequest"),
        GetBalanceResponse=message_class("GetBalanceResponse"),
        GetEpochRequest=message_class("GetEpochRequest"),
        GetEpochResponse=message_class("GetEpochResponse"),
        GetEpochRecordRequest=message_class("GetEpochRecordRequest"),
        GetEpochRecordResponse=message_class("GetEpochRecordResponse"),
        GetEpochChainRequest=message_class("GetEpochChainRequest"),
        GetEpochChainResponse=message_class("GetEpochChainResponse"),
        SubmitEpochProposalRequest=message_class("SubmitEpochProposalRequest"),
        SubmitEpochProposalResponse=message_class("SubmitEpochProposalResponse"),
    )


class _DynamicILCAppReadServiceStub:
    def __init__(self, channel: Any, messages: _MessageTypes) -> None:
        self.GetBalance = _unary_unary(
            channel,
            "/ilc_app.ILCAppReadService/GetBalance",
            messages.GetBalanceRequest.SerializeToString,
            messages.GetBalanceResponse.FromString,
        )
        self.GetEpoch = _unary_unary(
            channel,
            "/ilc_app.ILCAppReadService/GetEpoch",
            messages.GetEpochRequest.SerializeToString,
            messages.GetEpochResponse.FromString,
        )
        self.GetEpochRecord = _unary_unary(
            channel,
            "/ilc_app.ILCAppReadService/GetEpochRecord",
            messages.GetEpochRecordRequest.SerializeToString,
            messages.GetEpochRecordResponse.FromString,
        )
        self.GetEpochChain = _unary_unary(
            channel,
            "/ilc_app.ILCAppReadService/GetEpochChain",
            messages.GetEpochChainRequest.SerializeToString,
            messages.GetEpochChainResponse.FromString,
        )


class _DynamicILCAppProposalIngressServiceStub:
    def __init__(self, channel: Any, messages: _MessageTypes) -> None:
        self.SubmitEpochProposal = _unary_unary(
            channel,
            "/ilc_app.ILCAppProposalIngressService/SubmitEpochProposal",
            messages.SubmitEpochProposalRequest.SerializeToString,
            messages.SubmitEpochProposalResponse.FromString,
        )


def _unary_unary(
    channel: Any,
    path: str,
    request_serializer: Callable[[Any], bytes],
    response_deserializer: Callable[[bytes], Any],
) -> UnaryUnaryRpc:
    return channel.unary_unary(
        path,
        request_serializer=request_serializer,
        response_deserializer=response_deserializer,
    )


def build_secure_grpc_read_stub(
    config: ConsensusBridgeConfig,
    *,
    messages: _MessageTypes | None = None,
) -> ILCAppReadServiceStubProtocol:
    grpc_module = importlib.import_module("grpc")
    credentials = grpc_module.ssl_channel_credentials(
        root_certificates=config.tls_root_certificates
    )
    channel = grpc_module.secure_channel(
        config.target,
        credentials,
        options=(
            (
                "grpc.max_receive_message_length",
                config.max_epoch_chain_receive_bytes,
            ),
        ),
    )
    return _DynamicILCAppReadServiceStub(channel, messages or _build_message_types())


def build_secure_grpc_proposal_ingress_stub(
    config: ConsensusBridgeConfig,
    *,
    messages: _MessageTypes | None = None,
) -> ILCAppProposalIngressServiceStubProtocol:
    if (
        config.proposal_client_private_key is None
        or config.proposal_client_certificate_chain is None
    ):
        raise ValueError("proposal_client_certificate_pair_required_phase_1587_fix1")
    grpc_module = importlib.import_module("grpc")
    credentials = grpc_module.ssl_channel_credentials(
        root_certificates=(
            config.proposal_tls_root_certificates or config.tls_root_certificates
        ),
        private_key=config.proposal_client_private_key,
        certificate_chain=config.proposal_client_certificate_chain,
    )
    max_send_message_bytes = (
        config.max_proposal_body_bytes + MAX_PROPOSAL_GRPC_OVERHEAD_BYTES
    )
    channel = grpc_module.secure_channel(
        config.proposal_ingress_endpoint or config.target,
        credentials,
        options=(
            ("grpc.max_send_message_length", max_send_message_bytes),
            (
                "grpc.max_receive_message_length",
                config.max_epoch_chain_receive_bytes,
            ),
        ),
    )
    return _DynamicILCAppProposalIngressServiceStub(
        channel,
        messages or _build_message_types(),
    )


class ILCConsensusGrpcReadAdapter:
    def __init__(
        self,
        config: ConsensusBridgeConfig,
        *,
        stub: ILCAppReadServiceStubProtocol | None = None,
        messages: _MessageTypes | None = None,
    ) -> None:
        self.config = config
        self.messages = messages or _build_message_types()
        self.stub = stub or build_secure_grpc_read_stub(config, messages=self.messages)

    def verify_validator_cert_against_graph(
        self,
        *,
        validator_agent_id: str,
        presented_cert_der: bytes | bytearray | memoryview,
        atlas_reader: Any,
        expected_bls_public_key_hex: str,
        network_id: str,
        bls_verifier: BlsVerifier | None = None,
        graph_binding_guard: bool | None = None,
    ) -> bool:
        return verify_validator_cert_against_graph(
            validator_agent_id=validator_agent_id,
            presented_cert_der=presented_cert_der,
            atlas_reader=atlas_reader,
            expected_bls_public_key_hex=expected_bls_public_key_hex,
            network_id=network_id,
            bls_verifier=bls_verifier,
            graph_binding_guard=graph_binding_guard,
        )

    def _call(self, method_name: str, request: Any) -> Any:
        method = getattr(self.stub, method_name, None)
        if method is None:
            raise ValueError("consensus_grpc_stub_method_missing_phase_1358")
        return method(request, timeout=self.config.grpc_timeout_seconds)

    def get_epoch(self) -> int:
        response = self._call("GetEpoch", self.messages.GetEpochRequest())
        return _require_uint64_int(
            getattr(response, "current_epoch", None),
            "get_epoch_response_invalid_phase_1358",
        )

    def get_balance(self, agent_id: bytes | bytearray | memoryview) -> BalanceQuote:
        normalized_agent_id = _normalize_agent_id(agent_id)
        request = self.messages.GetBalanceRequest(agent_id=normalized_agent_id)
        response = self._call("GetBalance", request)
        amount_micro_ecu = _require_uint64_decimal(
            getattr(response, "amount_micro_ecu", None),
            "get_balance_amount_invalid_phase_1358",
        )
        version = _require_uint64_int(
            getattr(response, "version", None),
            "get_balance_version_invalid_phase_1358",
        )
        epoch = _require_uint64_int(
            getattr(response, "epoch", None),
            "get_balance_epoch_invalid_phase_1358",
        )
        return BalanceQuote(
            agent_id_length_bytes=len(normalized_agent_id),
            amount_micro_ecu=amount_micro_ecu,
            amount_ecu=amount_micro_ecu / MICRO_ECU_PER_ECU,
            version=version,
            epoch=epoch,
            production_bridge_active=PRODUCTION_BRIDGE_ACTIVE,
        )

    def get_epoch_record(self, epoch: int) -> EpochRecordQuote:
        normalized_epoch = _require_uint64_int(
            epoch,
            "get_epoch_record_epoch_invalid_phase_1358",
        )
        request = self.messages.GetEpochRecordRequest(epoch=normalized_epoch)
        response = self._call("GetEpochRecord", request)
        return _normalize_epoch_record_response(
            response,
            "get_epoch_record_response_invalid_phase_1358",
        )

    def get_epoch_chain(
        self,
        from_epoch: int,
        to_epoch: int,
        *,
        include_edges: bool = False,
    ) -> EpochChainQuote:
        if not isinstance(include_edges, bool):
            raise ValueError("epoch_chain_include_edges_invalid_phase_1358")
        if include_edges:
            raise ValueError("epoch_chain_edges_not_enabled_phase_1358")
        start = _require_uint64_int(
            from_epoch,
            "get_epoch_chain_from_epoch_invalid_phase_1358",
        )
        end = _require_uint64_int(to_epoch, "get_epoch_chain_to_epoch_invalid_phase_1358")
        # Rust app_interface.rs treats epoch 0 as a range sentinel:
        # from_epoch=0 starts at history epoch 1, and to_epoch=0 means current
        # epoch. Phase 1386a reconciles that contract over the TLS gRPC path.
        if start != 0 and end != 0 and end < start:
            raise ValueError("get_epoch_chain_range_invalid_phase_1358")
        if start != 0 and end != 0:
            requested_count = end - start + 1
            if requested_count > self.config.max_epoch_chain_records:
                raise ValueError("get_epoch_chain_max_records_exceeded_phase_1358")
        request = self.messages.GetEpochChainRequest(
            from_epoch=start,
            to_epoch=end,
            include_edges=False,
        )
        response = self._call("GetEpochChain", request)
        records = []
        for record in getattr(response, "records", ()):
            if len(records) >= self.config.max_epoch_chain_records:
                raise ValueError("get_epoch_chain_max_records_exceeded_phase_1358")
            records.append(record)
        normalized_records = tuple(
            _normalize_epoch_record_response(
                record,
                "get_epoch_chain_record_invalid_phase_1358",
            )
            for record in records
        )
        return EpochChainQuote(
            from_epoch=start,
            to_epoch=end,
            chain_complete=_require_bool(
                getattr(response, "chain_complete", None),
                "get_epoch_chain_complete_invalid_phase_1358",
            ),
            records=normalized_records,
            production_bridge_active=PRODUCTION_BRIDGE_ACTIVE,
        )


def _normalize_epoch_record_response(response: Any, token: str) -> EpochRecordQuote:
    return EpochRecordQuote(
        epoch=_require_uint64_int(getattr(response, "epoch", None), token),
        found=_require_bool(getattr(response, "found", None), token),
        state_root=_require_bytes(getattr(response, "state_root", None), token),
        agg_sig=_require_bytes(getattr(response, "agg_sig", None), token),
    )


def verify_validator_cert_against_graph(
    *,
    validator_agent_id: str,
    presented_cert_der: bytes | bytearray | memoryview,
    atlas_reader: Any,
    expected_bls_public_key_hex: str,
    network_id: str,
    bls_verifier: BlsVerifier | None = None,
    graph_binding_guard: bool | None = None,
) -> bool:
    """Verify TLS certificate identity against the Atlas assertion graph.

    The live Phase 1577b guard remains closed. While
    ``VALIDATOR_CERT_GRAPH_BINDING_NOT_ACTIVATED`` is true, this function is a
    no-op and preserves the current TLS-only bridge behavior. Tests pass an
    explicit false guard to exercise the fail-closed CDL-105 branches.
    """

    guard = (
        VALIDATOR_CERT_GRAPH_BINDING_NOT_ACTIVATED
        if graph_binding_guard is None
        else graph_binding_guard
    )
    if not isinstance(guard, bool):
        raise ValueError("validator_cert_graph_binding_guard_invalid_phase_1577b")
    if guard:
        return True

    cert_bytes = _require_bytes(
        presented_cert_der,
        "validator_cert_der_invalid_phase_1577b",
    )
    if not cert_bytes:
        raise ValueError("validator_cert_der_invalid_phase_1577b")
    assertion = load_from_atlas(atlas_reader, validator_agent_id)
    if assertion.revised_by is not None:
        raise ValueError("validator_cert_assertion_superseded")
    fingerprint = hashlib.sha256(cert_bytes).hexdigest()
    if assertion.tls_cert_sha256_fingerprint != fingerprint:
        raise ValueError("validator_cert_fingerprint_mismatch")
    if not verify_bls_signature(
        assertion,
        network_id=network_id,
        verifier=bls_verifier,
    ):
        raise ValueError("validator_cert_assertion_bls_invalid")
    expected_key = _require_lower_sha384_hex(
        expected_bls_public_key_hex,
        "validator_cert_expected_bls_key_invalid_phase_1577b",
    )
    if assertion.bls_public_key_hex != expected_key:
        raise ValueError("validator_cert_bls_key_identity_mismatch")
    return True


def build_quic_ecu_transfer_submission_path(
    *,
    transfer_payload_digest: str,
    target_quic_addr: str,
    target_validator_id: str,
    protocol_epoch: int,
) -> QuicEcuTransferSubmissionPath:
    return QuicEcuTransferSubmissionPath(
        transfer_payload_digest=_require_non_empty_str(
            transfer_payload_digest,
            "transfer_payload_digest_invalid_phase_1358",
        ),
        target_quic_addr=_require_non_empty_str(
            target_quic_addr,
            "target_quic_addr_invalid_phase_1358",
        ),
        target_validator_id=_require_non_empty_str(
            target_validator_id,
            "target_validator_id_invalid_phase_1358",
        ),
        protocol_epoch=_require_uint64_int(
            protocol_epoch,
            "transfer_protocol_epoch_invalid_phase_1358",
        ),
        production_bridge_active=PRODUCTION_BRIDGE_ACTIVE,
        path_token=QUIC_ECU_TRANSFER_SUBMISSION_PATH_TOKEN,
        status_token=LIVE_ECU_TRANSFER_NOT_ACTIVATED_TOKEN,
    )


def build_epoch_settlement_proposal_submission(
    *,
    submitter_agent_id: bytes | bytearray | memoryview,
    epoch_number: int,
    state_root_cidv1: bytes | bytearray | memoryview,
    settlement_record_bytes: bytes | bytearray | memoryview,
    not_before_unix_ms: int,
    network_id: str,
    idempotency_key: str | None = None,
) -> EpochSettlementProposalSubmission:
    normalized_submitter = _normalize_agent_id(submitter_agent_id)
    normalized_epoch = _require_uint64_int(
        epoch_number,
        "submit_epoch_proposal_epoch_number_invalid_phase_1587",
    )
    normalized_root = _require_exact_bytes(
        state_root_cidv1,
        CIDV1_ROOT_LENGTH_BYTES,
        "submit_epoch_proposal_state_root_invalid_phase_1587",
    )
    normalized_record = _require_bytes(
        settlement_record_bytes,
        "submit_epoch_proposal_settlement_record_invalid_phase_1587",
    )
    if not normalized_record:
        raise ValueError("submit_epoch_proposal_settlement_record_empty_phase_1587")
    normalized_not_before = _require_uint64_int(
        not_before_unix_ms,
        "submit_epoch_proposal_not_before_invalid_phase_1587",
    )
    normalized_network_id = _require_non_empty_str(
        network_id,
        "submit_epoch_proposal_network_id_invalid_phase_1587",
    )
    epoch_data_hash = _sha256_bytes(normalized_record)
    expected_key = _epoch_proposal_idempotency_key(
        network_id=normalized_network_id,
        epoch_number=normalized_epoch,
        submitter_agent_id=normalized_submitter,
        state_root_cidv1=normalized_root,
        epoch_data_hash=epoch_data_hash,
        settlement_record_bytes=normalized_record,
        not_before_unix_ms=normalized_not_before,
    )
    normalized_key = (
        expected_key
        if idempotency_key is None
        else _require_lower_sha256_hex(
            idempotency_key,
            "submit_epoch_proposal_idempotency_key_invalid_phase_1587",
        )
    )
    if normalized_key != expected_key:
        raise ValueError("submit_epoch_proposal_idempotency_preimage_mismatch_phase_1587")
    return EpochSettlementProposalSubmission(
        submitter_agent_id=normalized_submitter,
        epoch_number=normalized_epoch,
        state_root_cidv1=normalized_root,
        epoch_data_hash=epoch_data_hash,
        settlement_record_bytes=normalized_record,
        idempotency_key=normalized_key,
        not_before_unix_ms=normalized_not_before,
        network_id=normalized_network_id,
        production_bridge_active=PRODUCTION_BRIDGE_ACTIVE,
        activation_token=PRODUCTION_BRIDGE_ACTIVATED_PHASE_1587_TOKEN,
    )


def submit_ecu_transfer_via_quic(
    submission_path: EpochSettlementProposalSubmission,
    *,
    config: ConsensusBridgeConfig,
    stub: ILCAppProposalIngressServiceStubProtocol | None = None,
    messages: _MessageTypes | None = None,
) -> EpochProposalSubmissionResult:
    if not isinstance(submission_path, EpochSettlementProposalSubmission):
        raise ValueError("epoch_proposal_submission_path_invalid_phase_1587")
    _validate_epoch_settlement_proposal_submission(submission_path)
    if not PRODUCTION_BRIDGE_ACTIVE:
        raise ValueError(LIVE_ECU_TRANSFER_NOT_ACTIVATED_TOKEN)
    if len(submission_path.settlement_record_bytes) > config.max_proposal_body_bytes:
        raise ValueError("submit_epoch_proposal_body_too_large_phase_1587")
    message_types = messages or _build_message_types()
    proposal_stub = stub or build_secure_grpc_proposal_ingress_stub(
        config,
        messages=message_types,
    )
    request = message_types.SubmitEpochProposalRequest(
        submitter_agent_id=submission_path.submitter_agent_id,
        epoch_number=submission_path.epoch_number,
        state_root_cidv1=submission_path.state_root_cidv1,
        epoch_data_hash=submission_path.epoch_data_hash,
        settlement_record_bytes=submission_path.settlement_record_bytes,
        idempotency_key=submission_path.idempotency_key,
        not_before_unix_ms=submission_path.not_before_unix_ms,
        network_id=submission_path.network_id,
    )

    response: Any | None = None
    last_exc: Exception | None = None
    for _attempt in range(config.proposal_retry_count + 1):
        try:
            response = proposal_stub.SubmitEpochProposal(
                request,
                timeout=config.grpc_timeout_seconds,
            )
            break
        except Exception as exc:
            last_exc = exc
    if response is None:
        raise ValueError("submit_epoch_proposal_transport_failed_phase_1587") from last_exc

    error_code = getattr(response, "error_code", "")
    if error_code:
        raise ValueError(error_code)
    status_token = _require_non_empty_str(
        getattr(response, "status_token", None),
        "submit_epoch_proposal_status_token_invalid_phase_1587",
    )
    if status_token != SUBMIT_EPOCH_PROPOSAL_ACCEPTED_TOKEN:
        raise ValueError("submit_epoch_proposal_unexpected_status_phase_1587")
    accepted_epoch = _require_uint64_int(
        getattr(response, "accepted_epoch_number", None),
        "submit_epoch_proposal_accepted_epoch_invalid_phase_1587",
    )
    accepted_root = _require_exact_bytes(
        getattr(response, "accepted_state_root_cidv1", None),
        CIDV1_ROOT_LENGTH_BYTES,
        "submit_epoch_proposal_accepted_root_invalid_phase_1587",
    )
    proposal_id = _require_non_empty_str(
        getattr(response, "proposal_id", None),
        "submit_epoch_proposal_id_invalid_phase_1587",
    )
    if proposal_id != submission_path.idempotency_key:
        raise ValueError("submit_epoch_proposal_idempotency_response_mismatch_phase_1587_fix1")
    if accepted_epoch != submission_path.epoch_number:
        raise ValueError("submit_epoch_proposal_accepted_epoch_mismatch_phase_1587")
    if accepted_root != submission_path.state_root_cidv1:
        raise ValueError("submit_epoch_proposal_accepted_root_mismatch_phase_1587")
    return EpochProposalSubmissionResult(
        status_token=status_token,
        accepted_epoch_number=accepted_epoch,
        accepted_state_root_cidv1=accepted_root,
        proposal_id=proposal_id,
        production_bridge_active=PRODUCTION_BRIDGE_ACTIVE,
    )


__all__ = [
    "ADR_0028_PRODUCTION_BRIDGE_PARTIAL_TOKEN",
    "AGENT_ID_LENGTH_BYTES",
    "BalanceQuote",
    "ConsensusBridgeConfig",
    "DEFAULT_GRPC_TIMEOUT_SECONDS",
    "EPOCH_PROPOSAL_PREIMAGE_DOMAIN",
    "EpochChainQuote",
    "EpochProposalSubmissionResult",
    "EpochRecordQuote",
    "EpochSettlementProposalSubmission",
    "GET_EPOCH_GET_BALANCE_GET_EPOCH_RECORD_GET_EPOCH_CHAIN_TOKEN",
    "ILCConsensusGrpcReadAdapter",
    "ILC_CORE_CONSENSUS_GRPC_ADAPTER_VERSION",
    "LIVE_ECU_TRANSFER_NOT_ACTIVATED_TOKEN",
    "MAX_PROPOSAL_GRPC_OVERHEAD_BYTES",
    "MAX_PROPOSAL_BODY_BYTES",
    "MAX_EPOCH_CHAIN_RECORDS",
    "MAX_EPOCH_CHAIN_RECEIVE_BYTES",
    "PRODUCTION_BRIDGE_ACTIVE",
    "PRODUCTION_BRIDGE_ACTIVATED_PHASE_1587_TOKEN",
    "QUIC_ECU_TRANSFER_SUBMISSION_PATH_TOKEN",
    "QuicEcuTransferSubmissionPath",
    "SUBMIT_EPOCH_PROPOSAL_ACCEPTED_TOKEN",
    "TESTBED_STUBS_REPLACED_PRODUCTION_PATH_TOKEN",
    "VALIDATOR_CERT_GRAPH_BINDING_NOT_ACTIVATED",
    "build_epoch_settlement_proposal_submission",
    "build_quic_ecu_transfer_submission_path",
    "build_secure_grpc_proposal_ingress_stub",
    "build_secure_grpc_read_stub",
    "quote_to_canonical_json",
    "submit_ecu_transfer_via_quic",
    "verify_validator_cert_against_graph",
]
