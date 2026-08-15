# SPDX-License-Identifier: AGPL-3.0-only
"""Local LMDB-backed task coordination sidecar.

This module is operator-local coordination state. It does not publish task
state, open a P2P surface, mutate CDLs, or activate automated payment.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping, cast

import lmdb

from ilc_core.ledger.exact_numeric import decimal_to_canonical_string
from ilc_core.sidecars.execution_receipt import (
    SidecarExecutionReceipt,
    SidecarExecutionReceiptStore,
    hash_receipt_component,
)
from ilc_core.value_action.ilc_transfer_ledger import ILCTransferLedger


TASK_COORDINATION_SCHEMA_VERSION = "task_coordination_GAP_HARNESS_SIDECAR_08.v0.1"
TASK_COORDINATION_TRANSFER_ENABLED: bool = False

DEFAULT_TASK_COORDINATION_MAP_SIZE_BYTES = 64 * 1024 * 1024
DEFAULT_MAX_CONCURRENT_ACCEPTANCES_PER_AGENT = 10
MAX_ACCEPTANCES_PER_AGENT = 10_000
MAX_TASK_DESCRIPTION_BYTES = 1000
MAX_RESULT_CRITERIA_BYTES = 500
MAX_RESULT_SUMMARY_BYTES = 1000
MAX_RESULT_HASH_BYTES = 128
MAX_TASK_DESCRIPTION_CHARS = MAX_TASK_DESCRIPTION_BYTES
MAX_RESULT_CRITERIA_CHARS = MAX_RESULT_CRITERIA_BYTES
MAX_RESULT_SUMMARY_CHARS = MAX_RESULT_SUMMARY_BYTES
MAX_RESULT_HASH_CHARS = MAX_RESULT_HASH_BYTES
MAX_CAPS_MAX_CONCURRENT = 1000
MAX_RESULT_RECORDS_PER_OFFER = 0xFFFFFFFF

OFFERS_DB_NAME = b"offers"
ACCEPTANCES_DB_NAME = b"acceptances"
RESULTS_DB_NAME = b"results"

TASK_OFFER_STATUSES = frozenset({"open", "accepted", "completed", "expired", "cancelled"})
_TASK_OFFER_KEYS = frozenset(
    {
        "caps_max_concurrent",
        "commissioning_agent_id",
        "expiry_epoch",
        "offer_id",
        "pre_committed_ilc_amount",
        "result_criteria",
        "schema_version",
        "status",
        "task_description",
    }
)
_HEX = frozenset("0123456789abcdef")


class TaskCoordinationError(ValueError):
    """Stable task coordination validation/store error."""


@dataclass(frozen=True, init=False)
class TaskOffer:
    """Local task offer record with deterministic offer_id construction."""

    offer_id: str
    commissioning_agent_id: str
    task_description: str
    result_criteria: str
    expiry_epoch: int
    pre_committed_ilc_amount: Decimal | None
    caps_max_concurrent: int
    status: str

    def __init__(
        self,
        *,
        commissioning_agent_id: str,
        task_description: str,
        result_criteria: str,
        expiry_epoch: int,
        pre_committed_ilc_amount: Decimal | None = None,
        caps_max_concurrent: int = 1,
        status: str = "open",
    ) -> None:
        normalized = _offer_payload_without_id(
            commissioning_agent_id=commissioning_agent_id,
            task_description=task_description,
            result_criteria=result_criteria,
            expiry_epoch=expiry_epoch,
            pre_committed_ilc_amount=pre_committed_ilc_amount,
            caps_max_concurrent=caps_max_concurrent,
            status=status,
        )
        offer_id = _sha256_canonical(_offer_id_preimage(normalized))
        object.__setattr__(self, "offer_id", offer_id)
        object.__setattr__(self, "commissioning_agent_id", normalized["commissioning_agent_id"])
        object.__setattr__(self, "task_description", normalized["task_description"])
        object.__setattr__(self, "result_criteria", normalized["result_criteria"])
        object.__setattr__(self, "expiry_epoch", normalized["expiry_epoch"])
        object.__setattr__(
            self,
            "pre_committed_ilc_amount",
            _decode_optional_decimal(normalized["pre_committed_ilc_amount"]),
        )
        object.__setattr__(self, "caps_max_concurrent", normalized["caps_max_concurrent"])
        object.__setattr__(self, "status", normalized["status"])

    def to_dict(self) -> dict[str, Any]:
        payload = _offer_payload_without_id(
            commissioning_agent_id=self.commissioning_agent_id,
            task_description=self.task_description,
            result_criteria=self.result_criteria,
            expiry_epoch=self.expiry_epoch,
            pre_committed_ilc_amount=self.pre_committed_ilc_amount,
            caps_max_concurrent=self.caps_max_concurrent,
            status=self.status,
        )
        payload["offer_id"] = self.offer_id
        payload["schema_version"] = TASK_COORDINATION_SCHEMA_VERSION
        return payload

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "TaskOffer":
        if not isinstance(payload, Mapping):
            raise TaskCoordinationError("task_offer_payload_invalid")
        if set(payload) != _TASK_OFFER_KEYS:
            raise TaskCoordinationError("task_offer_field_set_invalid")
        if payload.get("schema_version") != TASK_COORDINATION_SCHEMA_VERSION:
            raise TaskCoordinationError("task_offer_schema_version_invalid")
        amount = _decode_optional_decimal(payload.get("pre_committed_ilc_amount"))
        offer = cls(
            commissioning_agent_id=_required_str(payload, "commissioning_agent_id"),
            task_description=_required_str(payload, "task_description"),
            result_criteria=_required_str(payload, "result_criteria"),
            expiry_epoch=_required_int(payload, "expiry_epoch"),
            pre_committed_ilc_amount=amount,
            caps_max_concurrent=_required_int(payload, "caps_max_concurrent"),
            status=_required_str(payload, "status"),
        )
        if payload.get("offer_id") != offer.offer_id:
            raise TaskCoordinationError("task_offer_id_mismatch")
        return offer

    def with_status(self, status: str) -> "TaskOffer":
        return TaskOffer(
            commissioning_agent_id=self.commissioning_agent_id,
            task_description=self.task_description,
            result_criteria=self.result_criteria,
            expiry_epoch=self.expiry_epoch,
            pre_committed_ilc_amount=self.pre_committed_ilc_amount,
            caps_max_concurrent=self.caps_max_concurrent,
            status=status,
        )


class TaskCoordinationLmdbStore:
    """Local LMDB store for task offers, acceptances, results, and receipts."""

    def __init__(
        self,
        storage_dir: str | Path,
        *,
        map_size_bytes: int = DEFAULT_TASK_COORDINATION_MAP_SIZE_BYTES,
        max_concurrent_acceptances_per_agent: int = DEFAULT_MAX_CONCURRENT_ACCEPTANCES_PER_AGENT,
        receipt_store: SidecarExecutionReceiptStore | None = None,
    ) -> None:
        if isinstance(map_size_bytes, bool) or not isinstance(map_size_bytes, int):
            raise TaskCoordinationError("task_coordination_map_size_invalid")
        if map_size_bytes <= 0:
            raise TaskCoordinationError("task_coordination_map_size_invalid")
        self.max_concurrent_acceptances_per_agent = _require_agent_concurrency_cap(
            max_concurrent_acceptances_per_agent
        )
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.env = lmdb.open(
            str(self.storage_dir.resolve()),
            create=True,
            lock=True,
            map_size=map_size_bytes,
            max_dbs=3,
            subdir=True,
        )
        self._offers_db = self.env.open_db(OFFERS_DB_NAME)
        self._acceptances_db = self.env.open_db(ACCEPTANCES_DB_NAME)
        self._results_db = self.env.open_db(RESULTS_DB_NAME)
        self._receipt_store = receipt_store or SidecarExecutionReceiptStore(
            self.storage_dir / "execution_receipts"
        )

    def create_offer(self, offer: TaskOffer) -> None:
        if not isinstance(offer, TaskOffer):
            raise TaskCoordinationError("task_offer_invalid")
        encoded_offer = _encode_json(offer.to_dict())
        with self.env.begin(write=True) as txn:
            offer_key = _offer_key(offer.offer_id)
            if txn.get(offer_key, db=self._offers_db) is not None:
                raise TaskCoordinationError("task_offer_duplicate")
            txn.put(offer_key, encoded_offer, db=self._offers_db)
        self._append_receipt(
            event_name="create_offer",
            agent_id_hex=offer.commissioning_agent_id,
            epoch=offer.expiry_epoch,
            inputs={"offer_id": offer.offer_id},
            outputs=offer.to_dict(),
        )

    def accept_offer(
        self,
        offer_id: str,
        accepting_agent_id: str,
        current_epoch: int,
        *,
        transfer_ledger: ILCTransferLedger | None = None,
        transfer_envelope: object | None = None,
        nonce_store: object | None = None,
        transfer_kwargs: Mapping[str, Any] | None = None,
    ) -> None:
        normalized_offer_id = _require_sha256_hex(offer_id, "task_offer_id_invalid")
        normalized_agent_id = _require_agent_id(accepting_agent_id)
        normalized_epoch = _require_epoch(current_epoch, "task_current_epoch_invalid")
        expired_in_txn = False
        with self.env.begin(write=True) as txn:
            offer = _read_offer_from_txn(txn, self._offers_db, normalized_offer_id)
            if offer is None:
                raise TaskCoordinationError("task_offer_missing")
            if offer.status not in {"open", "accepted"}:
                raise TaskCoordinationError("task_offer_not_open")
            if normalized_epoch >= offer.expiry_epoch:
                updated = offer.with_status("expired")
                txn.put(_offer_key(normalized_offer_id), _encode_json(updated.to_dict()), db=self._offers_db)
                expired_in_txn = True
                record = {}
            else:
                acceptance_key = _acceptance_key(normalized_offer_id, normalized_agent_id)
                if txn.get(acceptance_key, db=self._acceptances_db) is not None:
                    raise TaskCoordinationError("task_offer_already_accepted_by_agent")
                acceptances = _acceptance_records_for_offer(txn, self._acceptances_db, normalized_offer_id)
                if len(acceptances) >= offer.caps_max_concurrent:
                    raise TaskCoordinationError("task_offer_capacity_exceeded")
                if (
                    _active_acceptance_count_for_agent(txn, self._acceptances_db, normalized_agent_id)
                    >= self.max_concurrent_acceptances_per_agent
                ):
                    raise TaskCoordinationError("task_agent_concurrent_cap_exceeded")
                if offer.pre_committed_ilc_amount is not None:
                    _execute_pre_commitment_transfer_if_enabled(
                        transfer_ledger=transfer_ledger,
                        transfer_envelope=transfer_envelope,
                        nonce_store=nonce_store,
                        transfer_kwargs=transfer_kwargs,
                    )
                record = _acceptance_record(
                    offer_id=normalized_offer_id,
                    accepting_agent_id=normalized_agent_id,
                    accepted_epoch=normalized_epoch,
                )
                txn.put(acceptance_key, _encode_json(record), db=self._acceptances_db)
                updated_offer = offer.with_status("accepted")
                txn.put(
                    _offer_key(normalized_offer_id),
                    _encode_json(updated_offer.to_dict()),
                    db=self._offers_db,
                )
        if expired_in_txn:
            raise TaskCoordinationError("task_offer_expired")
        self._append_receipt(
            event_name="accept_offer",
            agent_id_hex=normalized_agent_id,
            epoch=normalized_epoch,
            inputs={"accepting_agent_id": normalized_agent_id, "offer_id": normalized_offer_id},
            outputs=record,
        )

    def submit_result(
        self,
        offer_id: str,
        accepting_agent_id: str,
        result_hash: str,
        result_summary: str,
        current_epoch: int,
    ) -> None:
        normalized_offer_id = _require_sha256_hex(offer_id, "task_offer_id_invalid")
        normalized_agent_id = _require_agent_id(accepting_agent_id)
        normalized_result_hash = _require_text(
            result_hash,
            "task_result_hash_invalid",
            max_bytes=MAX_RESULT_HASH_BYTES,
        )
        normalized_summary = _require_text(
            result_summary,
            "task_result_summary_invalid",
            max_bytes=MAX_RESULT_SUMMARY_BYTES,
        )
        normalized_epoch = _require_epoch(current_epoch, "task_current_epoch_invalid")
        with self.env.begin(write=True) as txn:
            offer = _read_offer_from_txn(txn, self._offers_db, normalized_offer_id)
            if offer is None:
                raise TaskCoordinationError("task_offer_missing")
            if txn.get(_acceptance_key(normalized_offer_id, normalized_agent_id), db=self._acceptances_db) is None:
                raise TaskCoordinationError("task_offer_not_accepted_by_agent")
            if offer.status != "accepted":
                raise TaskCoordinationError("task_offer_not_accepted")
            ordinal = _next_result_ordinal(txn, self._results_db, normalized_offer_id)
            result_record = {
                "accepting_agent_id": normalized_agent_id,
                "offer_id": normalized_offer_id,
                "ordinal": ordinal,
                "result_hash": normalized_result_hash,
                "result_summary": normalized_summary,
                "schema_version": TASK_COORDINATION_SCHEMA_VERSION,
                "submitted_epoch": normalized_epoch,
            }
            txn.put(
                _result_key(normalized_offer_id, ordinal),
                _encode_json(result_record),
                db=self._results_db,
            )
            txn.put(
                _offer_key(normalized_offer_id),
                _encode_json(offer.with_status("completed").to_dict()),
                db=self._offers_db,
            )
        self._append_receipt(
            event_name="submit_result",
            agent_id_hex=normalized_agent_id,
            epoch=normalized_epoch,
            inputs={"accepting_agent_id": normalized_agent_id, "offer_id": normalized_offer_id},
            outputs=result_record,
        )

    def expire_stale_offers(self, current_epoch: int) -> list[str]:
        normalized_epoch = _require_epoch(current_epoch, "task_current_epoch_invalid")
        expired_ids: list[str] = []
        expired_offers: list[TaskOffer] = []
        with self.env.begin(write=True) as txn:
            with txn.cursor(db=self._offers_db) as cursor:
                for _key, raw in cursor:
                    offer = TaskOffer.from_dict(_decode_json_dict(raw))
                    if offer.status in {"open", "accepted"} and normalized_epoch >= offer.expiry_epoch:
                        expired = offer.with_status("expired")
                        txn.put(_offer_key(offer.offer_id), _encode_json(expired.to_dict()), db=self._offers_db)
                        expired_ids.append(offer.offer_id)
                        expired_offers.append(expired)
        for offer in expired_offers:
            self._append_receipt(
                event_name="expire_offer",
                agent_id_hex=offer.commissioning_agent_id,
                epoch=normalized_epoch,
                inputs={"current_epoch": normalized_epoch, "offer_id": offer.offer_id},
                outputs=offer.to_dict(),
            )
        return expired_ids

    def get_offer(self, offer_id: str) -> TaskOffer | None:
        normalized_offer_id = _require_sha256_hex(offer_id, "task_offer_id_invalid")
        with self.env.begin() as txn:
            return _read_offer_from_txn(txn, self._offers_db, normalized_offer_id)

    def list_acceptances(self, offer_id: str) -> list[dict[str, Any]]:
        normalized_offer_id = _require_sha256_hex(offer_id, "task_offer_id_invalid")
        with self.env.begin(db=self._acceptances_db) as txn:
            return _acceptance_records_for_offer(txn, self._acceptances_db, normalized_offer_id)

    def list_results(self, offer_id: str) -> list[dict[str, Any]]:
        normalized_offer_id = _require_sha256_hex(offer_id, "task_offer_id_invalid")
        prefix = _offer_key(normalized_offer_id)
        results: list[dict[str, Any]] = []
        with self.env.begin(db=self._results_db) as txn:
            with txn.cursor() as cursor:
                if not cursor.set_range(prefix):
                    return []
                for key, value in cursor:
                    if not key.startswith(prefix):
                        break
                    results.append(_decode_json_dict(value))
        return results

    def _append_receipt(
        self,
        *,
        event_name: str,
        agent_id_hex: str,
        epoch: int,
        inputs: Mapping[str, Any],
        outputs: Mapping[str, Any],
    ) -> None:
        receipt = SidecarExecutionReceipt(
            tool_id=f"task_coordination:{event_name}",
            action_type="unknown",
            epoch=epoch,
            agent_id_hex=agent_id_hex,
            inputs_hash=hash_receipt_component(inputs),
            outputs_hash=hash_receipt_component(outputs),
            status="success",
        )
        self._receipt_store.append_receipt(receipt)


def _execute_pre_commitment_transfer_if_enabled(
    *,
    transfer_ledger: ILCTransferLedger | None,
    transfer_envelope: object | None,
    nonce_store: object | None,
    transfer_kwargs: Mapping[str, Any] | None,
) -> object:
    if TASK_COORDINATION_TRANSFER_ENABLED is not True:
        raise ValueError("task_coordination_transfer_not_activated")
    if transfer_ledger is None or transfer_envelope is None or nonce_store is None:
        raise TaskCoordinationError("task_coordination_transfer_runtime_not_configured")
    kwargs = dict(transfer_kwargs or {})
    return transfer_ledger.execute_transfer(transfer_envelope, nonce_store, **kwargs)  # type: ignore[arg-type]


def _offer_payload_without_id(
    *,
    commissioning_agent_id: str,
    task_description: str,
    result_criteria: str,
    expiry_epoch: int,
    pre_committed_ilc_amount: Decimal | None,
    caps_max_concurrent: int,
    status: str,
) -> dict[str, Any]:
    return {
        "caps_max_concurrent": _require_offer_capacity(caps_max_concurrent),
        "commissioning_agent_id": _require_agent_id(commissioning_agent_id),
        "expiry_epoch": _require_epoch(expiry_epoch, "task_expiry_epoch_invalid"),
        "pre_committed_ilc_amount": _encode_optional_amount(pre_committed_ilc_amount),
        "result_criteria": _require_text(
            result_criteria,
            "task_result_criteria_invalid",
            max_bytes=MAX_RESULT_CRITERIA_BYTES,
        ),
        "status": _require_status(status),
        "task_description": _require_text(
            task_description,
            "task_description_invalid",
            max_bytes=MAX_TASK_DESCRIPTION_BYTES,
        ),
    }


def _offer_id_preimage(normalized_offer_payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in normalized_offer_payload.items()
        if key != "status"
    }


def _encode_optional_amount(value: Decimal | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, Decimal):
        raise TaskCoordinationError("invalid_amount_type")
    if not value.is_finite():
        raise ValueError("invalid_amount_non_finite")
    if value <= Decimal("0"):
        raise TaskCoordinationError("invalid_amount_non_positive")
    return decimal_to_canonical_string(value)


def _decode_optional_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    if type(value) is not str:
        raise TaskCoordinationError("invalid_amount_type")
    try:
        decimal_value = Decimal(value)
    except InvalidOperation as exc:
        raise TaskCoordinationError("invalid_amount_type") from exc
    if not decimal_value.is_finite():
        raise ValueError("invalid_amount_non_finite")
    if decimal_value <= Decimal("0"):
        raise TaskCoordinationError("invalid_amount_non_positive")
    return decimal_value


def _read_offer_from_txn(txn: Any, offers_db: Any, offer_id: str) -> TaskOffer | None:
    raw = txn.get(_offer_key(offer_id), db=offers_db)
    if raw is None:
        return None
    return TaskOffer.from_dict(_decode_json_dict(raw))


def _acceptance_record(
    *,
    offer_id: str,
    accepting_agent_id: str,
    accepted_epoch: int,
) -> dict[str, Any]:
    return {
        "accepted_epoch": _require_epoch(accepted_epoch, "task_accepted_epoch_invalid"),
        "accepting_agent_id": _require_agent_id(accepting_agent_id),
        "offer_id": _require_sha256_hex(offer_id, "task_offer_id_invalid"),
        "schema_version": TASK_COORDINATION_SCHEMA_VERSION,
    }


def _acceptance_records_for_offer(txn: Any, acceptances_db: Any, offer_id: str) -> list[dict[str, Any]]:
    prefix = _offer_key(offer_id)
    records: list[dict[str, Any]] = []
    with txn.cursor(db=acceptances_db) as cursor:
        if not cursor.set_range(prefix):
            return []
        for key, value in cursor:
            if not key.startswith(prefix):
                break
            records.append(_decode_json_dict(value))
    return records


def _active_acceptance_count_for_agent(txn: Any, acceptances_db: Any, agent_id: str) -> int:
    count = 0
    with txn.cursor(db=acceptances_db) as cursor:
        for _key, value in cursor:
            record = _decode_json_dict(value)
            if record.get("accepting_agent_id") == agent_id:
                count += 1
    return count


def _next_result_ordinal(txn: Any, results_db: Any, offer_id: str) -> int:
    prefix = _offer_key(offer_id)
    count = 0
    with txn.cursor(db=results_db) as cursor:
        if cursor.set_range(prefix):
            for key, _value in cursor:
                if not key.startswith(prefix):
                    break
                if len(key) != len(prefix) + 4:
                    raise TaskCoordinationError("task_result_key_corrupted")
                count += 1
    if count > MAX_RESULT_RECORDS_PER_OFFER:
        raise TaskCoordinationError("task_results_exhausted")
    return count


def _offer_key(offer_id: str) -> bytes:
    return _require_sha256_hex(offer_id, "task_offer_id_invalid").encode("utf-8")


def _acceptance_key(offer_id: str, accepting_agent_id: str) -> bytes:
    return _offer_key(offer_id) + _require_agent_id(accepting_agent_id).encode("utf-8")


def _result_key(offer_id: str, ordinal: int) -> bytes:
    if isinstance(ordinal, bool) or not isinstance(ordinal, int) or ordinal < 0:
        raise TaskCoordinationError("task_result_ordinal_invalid")
    if ordinal > MAX_RESULT_RECORDS_PER_OFFER:
        raise TaskCoordinationError("task_result_ordinal_invalid")
    return _offer_key(offer_id) + ordinal.to_bytes(4, "big", signed=False)


def _encode_json(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode(
        "utf-8"
    )


def _decode_json_dict(raw: bytes) -> dict[str, Any]:
    try:
        decoded = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TaskCoordinationError("task_coordination_json_corrupted") from exc
    if not isinstance(decoded, dict):
        raise TaskCoordinationError("task_coordination_json_invalid")
    return cast(dict[str, Any], decoded)


def _sha256_canonical(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(_encode_json(payload)).hexdigest()


def _required_str(payload: Mapping[str, Any], field_name: str) -> str:
    value = payload.get(field_name)
    if type(value) is not str:
        raise TaskCoordinationError(f"task_offer_{field_name}_invalid")
    return value


def _required_int(payload: Mapping[str, Any], field_name: str) -> int:
    value = payload.get(field_name)
    if isinstance(value, bool) or not isinstance(value, int):
        raise TaskCoordinationError(f"task_offer_{field_name}_invalid")
    return value


def _require_agent_id(value: Any) -> str:
    if type(value) is not str or len(value) != 96:
        raise TaskCoordinationError("task_agent_id_invalid")
    if value.lower() != value or any(char not in _HEX for char in value):
        raise TaskCoordinationError("task_agent_id_invalid")
    return value


def _require_sha256_hex(value: Any, token: str) -> str:
    if type(value) is not str or len(value) != 64:
        raise TaskCoordinationError(token)
    if value.lower() != value or any(char not in _HEX for char in value):
        raise TaskCoordinationError(token)
    return value


def _require_epoch(value: Any, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise TaskCoordinationError(token)
    return value


def _require_text(value: Any, token: str, *, max_bytes: int) -> str:
    if type(value) is not str or not value:
        raise TaskCoordinationError(token)
    if len(value.encode("utf-8")) > max_bytes:
        raise TaskCoordinationError(token)
    return value


def _require_status(value: Any) -> str:
    if type(value) is not str or value not in TASK_OFFER_STATUSES:
        raise TaskCoordinationError("task_offer_status_invalid")
    return value


def _require_offer_capacity(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TaskCoordinationError("task_offer_capacity_invalid")
    if value < 1 or value > MAX_CAPS_MAX_CONCURRENT:
        raise TaskCoordinationError("task_offer_capacity_invalid")
    return value


def _require_agent_concurrency_cap(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TaskCoordinationError("task_agent_concurrent_cap_invalid")
    if value < 1 or value > MAX_ACCEPTANCES_PER_AGENT:
        raise TaskCoordinationError("task_agent_concurrent_cap_invalid")
    return value


__all__ = [
    "ACCEPTANCES_DB_NAME",
    "DEFAULT_MAX_CONCURRENT_ACCEPTANCES_PER_AGENT",
    "DEFAULT_TASK_COORDINATION_MAP_SIZE_BYTES",
    "OFFERS_DB_NAME",
    "RESULTS_DB_NAME",
    "TASK_COORDINATION_SCHEMA_VERSION",
    "TASK_COORDINATION_TRANSFER_ENABLED",
    "TaskCoordinationError",
    "TaskCoordinationLmdbStore",
    "TaskOffer",
]
