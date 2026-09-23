# SPDX-License-Identifier: AGPL-3.0-only
"""Durable ECU accrual evidence for monthly close dry-runs."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping, Protocol

from ilc_core.epoch.epoch_distribution_writer import MAX_ELIGIBLE_AGENTS
from ilc_core.epoch.ecu_attribution_receipt_store import (
    compute_attribution_receipt_state_root_sha256,
)
from ilc_core.epoch.protocol_account_boundary import is_reserved_protocol_account
from ilc_core.ledger.exact_numeric import decimal_to_canonical_string, parse_non_negative_decimal


ECU_ACCRUAL_EVIDENCE_SCHEMA_VERSION = (
    "ecu_accrual_evidence_GAP_ECU_ACCRUAL_EVIDENCE_SOURCE_BRIDGE_00.v0.2"
)
MAX_ECU_ACCRUAL_EVIDENCE_BYTES = 1_048_576
MAX_ECU_ACCRUAL_AGENT_ID_BYTES = 256
_AGENT_ID_RE = re.compile(r"^[0-9a-f]{96}$")
_EVIDENCE_HASH_FIELDS = frozenset(
    {
        "accrual_close_validation_epoch",
        "agent_ecu_weights",
        "issuance_interval_id",
        "lmdb_state_root_sha256",
        "schema_version",
    }
)
EMPTY_ATTRIBUTION_RECEIPT_STATE_ROOT_SHA256 = compute_attribution_receipt_state_root_sha256(
    "__empty_attribution_receipt_store__"
)
_HEX_64_RE = re.compile(r"^[0-9a-f]{64}$")


class EcuAccrualRuntime(Protocol):
    def get_accrued_ecu(self, agent_id: str) -> str:
        ...


@dataclass(frozen=True, kw_only=True)
class EcuAccrualEvidence:
    """Validated durable snapshot of ECU accrual weights.

    These weights are accounting evidence for later settlement input. They are
    not spendable balances and are not wallet rows.
    """

    issuance_interval_id: int
    agent_ecu_weights: dict[str, str]
    accrual_close_validation_epoch: int
    lmdb_state_root_sha256: str = EMPTY_ATTRIBUTION_RECEIPT_STATE_ROOT_SHA256
    schema_version: str = ECU_ACCRUAL_EVIDENCE_SCHEMA_VERSION
    evidence_sha256: str = ""

    def __post_init__(self) -> None:
        interval_id = _require_non_negative_int(
            self.issuance_interval_id,
            "ecu_accrual_evidence_issuance_interval_id_invalid",
        )
        close_epoch = _require_non_negative_int(
            self.accrual_close_validation_epoch,
            "ecu_accrual_evidence_close_validation_epoch_invalid",
        )
        schema = _require_exact_schema(self.schema_version)
        weights = _require_agent_weight_mapping(self.agent_ecu_weights)
        lmdb_state_root = _require_sha256_hex(
            self.lmdb_state_root_sha256,
            "ecu_accrual_evidence_lmdb_state_root_sha256_invalid",
        )
        expected_hash = _hash_evidence_payload(
            {
                "accrual_close_validation_epoch": close_epoch,
                "agent_ecu_weights": weights,
                "issuance_interval_id": interval_id,
                "lmdb_state_root_sha256": lmdb_state_root,
                "schema_version": schema,
            }
        )
        if self.evidence_sha256 and self.evidence_sha256 != expected_hash:
            raise ValueError("ecu_accrual_evidence_sha256_mismatch")

        object.__setattr__(self, "issuance_interval_id", interval_id)
        object.__setattr__(self, "accrual_close_validation_epoch", close_epoch)
        object.__setattr__(self, "schema_version", schema)
        object.__setattr__(self, "agent_ecu_weights", weights)
        object.__setattr__(self, "lmdb_state_root_sha256", lmdb_state_root)
        object.__setattr__(self, "evidence_sha256", expected_hash)

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "accrual_close_validation_epoch": self.accrual_close_validation_epoch,
            "agent_ecu_weights": dict(self.agent_ecu_weights),
            "evidence_sha256": self.evidence_sha256,
            "issuance_interval_id": self.issuance_interval_id,
            "lmdb_state_root_sha256": self.lmdb_state_root_sha256,
            "schema_version": self.schema_version,
        }


def build_ecu_accrual_evidence(
    runtime: EcuAccrualRuntime,
    *,
    issuance_interval_id: int,
    accrual_close_validation_epoch: int,
    agent_ids: list[str] | tuple[str, ...] | None = None,
) -> EcuAccrualEvidence:
    if not hasattr(runtime, "get_accrued_ecu"):
        raise ValueError("ecu_accrual_runtime_required")
    normalized_ids = _require_agent_id_sequence(
        _enumerate_agent_ids(runtime) if agent_ids is None else agent_ids
    )
    weights = {
        agent_id: _canonical_ecu_weight(runtime.get_accrued_ecu(agent_id))
        for agent_id in normalized_ids
    }
    return EcuAccrualEvidence(
        issuance_interval_id=issuance_interval_id,
        agent_ecu_weights=weights,
        accrual_close_validation_epoch=accrual_close_validation_epoch,
        lmdb_state_root_sha256=_runtime_lmdb_state_root_sha256(runtime),
    )


def write_ecu_accrual_evidence(evidence: EcuAccrualEvidence, path: str | Path) -> None:
    normalized = _require_evidence(evidence)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(
        normalized.to_canonical_record(),
        indent=2,
        sort_keys=True,
        allow_nan=False,
    )
    encoded_content = f"{content}\n".encode("utf-8")
    if len(encoded_content) > MAX_ECU_ACCRUAL_EVIDENCE_BYTES:
        raise ValueError("ecu_accrual_evidence_exceeds_max_bytes")
    fd, tmp = tempfile.mkstemp(dir=target.parent, prefix=f".{target.name}.", suffix=".tmp")
    tmp_path = Path(tmp)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded_content)
        os.replace(tmp_path, target)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def read_ecu_accrual_evidence(path: str | Path) -> EcuAccrualEvidence:
    source = Path(path)
    size = source.stat().st_size
    if size > MAX_ECU_ACCRUAL_EVIDENCE_BYTES:
        raise ValueError("ecu_accrual_evidence_exceeds_max_bytes")
    try:
        payload = json.loads(
            source.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_json_keys,
        )
    except json.JSONDecodeError as exc:
        raise ValueError("ecu_accrual_evidence_json_invalid") from exc
    if not isinstance(payload, Mapping):
        raise ValueError("ecu_accrual_evidence_record_required")
    return _coerce_evidence_mapping(payload)


def is_replay_safe(
    evidence: EcuAccrualEvidence,
    *,
    issuance_interval_id: int,
    accrual_close_validation_epoch: int,
) -> bool:
    normalized = _require_evidence(evidence)
    return (
        normalized.issuance_interval_id == issuance_interval_id
        and normalized.accrual_close_validation_epoch == accrual_close_validation_epoch
    )


def _coerce_evidence_mapping(payload: Mapping[str, Any]) -> EcuAccrualEvidence:
    keys = set(payload)
    expected = set(_EVIDENCE_HASH_FIELDS) | {"evidence_sha256"}
    if keys != expected:
        raise ValueError("ecu_accrual_evidence_fields_invalid")
    return EcuAccrualEvidence(
        issuance_interval_id=payload["issuance_interval_id"],
        agent_ecu_weights=payload["agent_ecu_weights"],
        accrual_close_validation_epoch=payload["accrual_close_validation_epoch"],
        lmdb_state_root_sha256=payload["lmdb_state_root_sha256"],
        schema_version=payload["schema_version"],
        evidence_sha256=payload["evidence_sha256"],
    )


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    record: dict[str, Any] = {}
    for key, value in pairs:
        if key in record:
            raise ValueError("ecu_accrual_evidence_duplicate_json_key")
        record[key] = value
    return record


def _require_evidence(value: object) -> EcuAccrualEvidence:
    if not isinstance(value, EcuAccrualEvidence):
        raise ValueError("ecu_accrual_evidence_required")
    return value


def _require_exact_schema(value: object) -> str:
    if value != ECU_ACCRUAL_EVIDENCE_SCHEMA_VERSION:
        raise ValueError("ecu_accrual_evidence_schema_version_invalid")
    return value


def _runtime_lmdb_state_root_sha256(runtime: EcuAccrualRuntime) -> str:
    provider = getattr(runtime, "lmdb_state_root_sha256", None)
    if provider is None:
        return EMPTY_ATTRIBUTION_RECEIPT_STATE_ROOT_SHA256
    value = provider() if callable(provider) else provider
    return _require_sha256_hex(value, "ecu_accrual_runtime_lmdb_state_root_sha256_invalid")


def _enumerate_agent_ids(runtime: EcuAccrualRuntime) -> list[str] | tuple[str, ...]:
    provider = getattr(runtime, "list_agents_with_attribution_receipts", None)
    if provider is None or not callable(provider):
        raise ValueError("ecu_accrual_agent_ids_required_without_enumerator")
    agent_ids = provider()
    if not isinstance(agent_ids, (list, tuple)):
        raise ValueError("ecu_accrual_agent_enumerator_must_return_sequence")
    return agent_ids


def _require_non_negative_int(value: object, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(token)
    return value


def _require_sha256_hex(value: object, token: str) -> str:
    if not isinstance(value, str) or _HEX_64_RE.fullmatch(value) is None:
        raise ValueError(token)
    return value


def _require_agent_id_sequence(value: object) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise ValueError("ecu_accrual_agent_ids_must_be_sequence")
    if len(value) > MAX_ELIGIBLE_AGENTS:
        raise ValueError("ecu_accrual_agent_ids_exceeds_max_count")
    seen: set[str] = set()
    normalized: list[str] = []
    for raw_agent_id in value:
        agent_id = _require_agent_id(raw_agent_id)
        if agent_id in seen:
            raise ValueError("ecu_accrual_agent_id_duplicate")
        seen.add(agent_id)
        normalized.append(agent_id)
    return tuple(normalized)


def _require_agent_weight_mapping(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        raise ValueError("ecu_accrual_agent_weights_must_be_dict")
    if len(value) > MAX_ELIGIBLE_AGENTS:
        raise ValueError("ecu_accrual_agent_weights_exceeds_max_count")
    normalized: dict[str, str] = {}
    for raw_agent_id, raw_weight in value.items():
        normalized[_require_agent_id(raw_agent_id)] = _canonical_ecu_weight(raw_weight)
    return dict(sorted(normalized.items()))


def _require_agent_id(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("ecu_accrual_agent_id_required")
    if is_reserved_protocol_account(value):
        raise ValueError("ecu_accrual_evidence_agent_id_reserved_protocol_account")
    if len(value.encode("utf-8")) > MAX_ECU_ACCRUAL_AGENT_ID_BYTES:
        raise ValueError("ecu_accrual_agent_id_exceeds_max_bytes")
    if _AGENT_ID_RE.fullmatch(value) is None:
        raise ValueError("ecu_accrual_agent_id_must_be_96_hex")
    return value


def _canonical_ecu_weight(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("ecu_accrual_weight_must_be_canonical_decimal_string")
    amount = parse_non_negative_decimal(
        value,
        token="ecu_accrual_weight_must_be_non_negative_decimal",
    )
    canonical = decimal_to_canonical_string(amount)
    if value != canonical:
        raise ValueError("ecu_accrual_weight_must_be_canonical_decimal_string")
    return canonical


def _hash_evidence_payload(payload: Mapping[str, Any]) -> str:
    if set(payload) != _EVIDENCE_HASH_FIELDS:
        raise ValueError("ecu_accrual_evidence_hash_payload_fields_invalid")
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode(
            "utf-8"
        )
    ).hexdigest()


__all__ = [
    "ECU_ACCRUAL_EVIDENCE_SCHEMA_VERSION",
    "EMPTY_ATTRIBUTION_RECEIPT_STATE_ROOT_SHA256",
    "EcuAccrualEvidence",
    "MAX_ECU_ACCRUAL_AGENT_ID_BYTES",
    "MAX_ECU_ACCRUAL_EVIDENCE_BYTES",
    "build_ecu_accrual_evidence",
    "is_replay_safe",
    "read_ecu_accrual_evidence",
    "write_ecu_accrual_evidence",
]
