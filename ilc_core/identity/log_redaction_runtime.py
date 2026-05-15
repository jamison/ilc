"""HIGH-001 AgentID log redaction helpers.

The runtime boundary here is intentionally small: callers redact AgentID values
before handing records to a logging sink. The token is deterministic for
``(agent_id, protocol_epoch)`` so operators can correlate local events without
emitting plaintext identity material.
"""

from __future__ import annotations

import hashlib
import logging
from collections.abc import Iterable, Mapping
from typing import Any

HIGH_001_LOG_REDACTION_RUNTIME_VERSION = "high_001_log_redaction_runtime_phase_1359.v0.1"
AGENT_ID_PLAINTEXT_REDACTED_VALIDATOR_LOGS_TOKEN = (
    "agent_id_plaintext_redacted_validator_logs_phase_1359"
)
SENDER_PRIVACY_CLAIM_BLOCKER_CLEARED_TOKEN = (
    "sender_privacy_claim_blocker_cleared_phase_1359"
)

_REDACTION_DOMAIN = b"ilc-high-001-agentid-log-redaction-v1"
_DEFAULT_PROTOCOL_EPOCH = 0
_MAX_AGENT_ID_CHARS = 512
_MAX_AGENT_ID_BYTES = 512
_MAX_LOG_MESSAGE_CHARS = 65_536
_MAX_AGENT_IDS_PER_RECORD = 128


def redact_agent_id_for_log(
    agent_id: str | bytes | bytearray | memoryview,
    *,
    protocol_epoch: int = _DEFAULT_PROTOCOL_EPOCH,
) -> str:
    """Return a deterministic, non-plaintext log token for an AgentID-like value."""

    epoch = _require_protocol_epoch(protocol_epoch)
    material = _agent_id_material(agent_id)
    digest = hashlib.sha256(
        _REDACTION_DOMAIN
        + b":epoch="
        + str(epoch).encode("ascii")
        + b":"
        + material
    ).hexdigest()[:24]
    return f"[agent_id:redacted:v1:epoch={epoch}:sha256={digest}]"


def redact_agent_ids_in_log_message(
    message: str,
    agent_ids: Iterable[str | bytes | bytearray | memoryview],
    *,
    protocol_epoch: int = _DEFAULT_PROTOCOL_EPOCH,
) -> str:
    """Replace known plaintext AgentID occurrences in a bounded log message."""

    if not isinstance(message, str):
        raise ValueError("log_redaction_message_must_be_str")
    if len(message) > _MAX_LOG_MESSAGE_CHARS:
        raise ValueError("log_redaction_message_exceeds_bound")

    replacements = _replacement_pairs(agent_ids, protocol_epoch=protocol_epoch)
    redacted = message
    for plaintext, token in replacements:
        redacted = redacted.replace(plaintext, token)
    return redacted


class AgentIDLogRedactionFilter(logging.Filter):
    """Logging filter that redacts registered AgentID values before emit."""

    def __init__(
        self,
        agent_ids: Iterable[str | bytes | bytearray | memoryview],
        *,
        protocol_epoch: int = _DEFAULT_PROTOCOL_EPOCH,
        name: str = "",
    ) -> None:
        super().__init__(name)
        self._protocol_epoch = _require_protocol_epoch(protocol_epoch)
        self._replacements = _replacement_pairs(
            agent_ids,
            protocol_epoch=self._protocol_epoch,
        )

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = _redact_string_with_pairs(record.msg, self._replacements)
        record.args = _redact_log_args(record.args, self._replacements)
        return True


def _require_protocol_epoch(protocol_epoch: int) -> int:
    if isinstance(protocol_epoch, bool) or not isinstance(protocol_epoch, int):
        raise ValueError("log_redaction_protocol_epoch_must_be_int")
    if protocol_epoch < 0:
        raise ValueError("log_redaction_protocol_epoch_must_be_non_negative")
    return protocol_epoch


def _agent_id_material(agent_id: str | bytes | bytearray | memoryview) -> bytes:
    if isinstance(agent_id, str):
        if not agent_id:
            raise ValueError("log_redaction_agent_id_empty")
        if len(agent_id) > _MAX_AGENT_ID_CHARS:
            raise ValueError("log_redaction_agent_id_exceeds_bound")
        return agent_id.lower().encode("utf-8")
    if isinstance(agent_id, (bytes, bytearray, memoryview)):
        material = bytes(agent_id)
        if not material:
            raise ValueError("log_redaction_agent_id_empty")
        if len(material) > _MAX_AGENT_ID_BYTES:
            raise ValueError("log_redaction_agent_id_exceeds_bound")
        return material
    raise ValueError("log_redaction_agent_id_type_invalid")


def _plaintext_forms(agent_id: str | bytes | bytearray | memoryview) -> tuple[str, ...]:
    if isinstance(agent_id, str):
        return (agent_id, agent_id.lower())
    material = _agent_id_material(agent_id)
    return (material.hex(),)


def _replacement_pairs(
    agent_ids: Iterable[str | bytes | bytearray | memoryview],
    *,
    protocol_epoch: int,
) -> tuple[tuple[str, str], ...]:
    if isinstance(agent_ids, (str, bytes, bytearray, memoryview)):
        raise ValueError("log_redaction_agent_ids_must_be_iterable_of_ids")

    pairs: list[tuple[str, str]] = []
    seen_plaintexts: set[str] = set()
    count = 0
    for agent_id in agent_ids:
        count += 1
        if count > _MAX_AGENT_IDS_PER_RECORD:
            raise ValueError("log_redaction_agent_ids_exceed_bound")
        token = redact_agent_id_for_log(agent_id, protocol_epoch=protocol_epoch)
        for plaintext in _plaintext_forms(agent_id):
            if plaintext and plaintext not in seen_plaintexts:
                seen_plaintexts.add(plaintext)
                pairs.append((plaintext, token))
    pairs.sort(key=lambda item: len(item[0]), reverse=True)
    return tuple(pairs)


def _redact_string_with_pairs(message: str, pairs: tuple[tuple[str, str], ...]) -> str:
    if len(message) > _MAX_LOG_MESSAGE_CHARS:
        raise ValueError("log_redaction_message_exceeds_bound")
    redacted = message
    for plaintext, token in pairs:
        redacted = redacted.replace(plaintext, token)
    return redacted


def _redact_log_args(args: Any, pairs: tuple[tuple[str, str], ...]) -> Any:
    if not args:
        return args
    if isinstance(args, str):
        return _redact_string_with_pairs(args, pairs)
    if isinstance(args, tuple):
        return tuple(_redact_log_args(item, pairs) for item in args)
    if isinstance(args, Mapping):
        return {key: _redact_log_args(value, pairs) for key, value in args.items()}
    return args
