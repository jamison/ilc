"""In-process claim nullifier and duplicate-claim registry for Phase 1389b."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from threading import Lock
from typing import Any


CLAIM_NULLIFIER_REGISTRY_VERSION = "claim_nullifier_registry_v1"
CLAIM_NULLIFIER_DOMAIN = "ilc-public-claim-nullifier-v1"
CLAIM_NULLIFIER_PREFIX = "claim_nullifier_sha256"
CLAIM_SEED_PREFIX = "claim_seed_sha256"
PRESENTATION_CANONICAL_PREFIX = "claim_presentation_canonical_sha256"
PUBLIC_ECONOMICS_ADMISSION_REF = (
    "public_economics_requires_public_node_admission_verified_phase_1387a"
)
CLAIM_NULLIFIER_REGISTRY_ACTIVE_TOKEN = "claim_nullifier_registry_v1_active_phase_1389b"
DUPLICATE_CLAIM_REGISTRY_ACTIVE_TOKEN = "duplicate_claim_registry_active_phase_1389b"
CLAIMABILITY_VERIFIER_PUBLIC_MODE_READY_TOKEN = (
    "claimability_verifier_public_mode_ready_phase_1389b"
)

PENDING = "pending"
ACCEPTED = "accepted"
REJECTED_NONBLOCKING = "rejected_nonblocking"
EXPIRED = "expired"
ACTIVE_STATUSES = frozenset({PENDING, ACCEPTED})
CLAIM_NULLIFIER_POST_WINDOW_RETENTION_EPOCHS = 1
MAX_CLAIM_NULLIFIER_RECORDS = 100_000
_MAX_CANONICAL_PAYLOAD_DEPTH = 32
_MAX_CANONICAL_PAYLOAD_NODES = 100_000
_MAX_TEXT_LENGTH = 4096
_MAX_CANONICAL_PAYLOAD_TEXT_BYTES = 1_000_000
_MAX_PROTOCOL_INT = 2**63 - 1


class ClaimNullifierRegistryError(ValueError):
    """Stable-token registry error."""

    def __init__(self, token: str, message: str, *, conflict_field: str | None = None) -> None:
        super().__init__(message)
        self.token = token
        self.conflict_field = conflict_field


@dataclass(frozen=True)
class ClaimNullifierRecord:
    claim_nullifier_ref: str
    claim_seed_ref: str
    canonical_agent_identity: str
    presentation_id: str
    presentation_canonical_ref: str
    claimability_proof_ref: str
    conversion_receipt_sha256: str
    conversion_lot_id: str
    claim_window_start_epoch: int
    claim_window_end_epoch: int
    first_seen_issuance_epoch: int
    expires_at_issuance_epoch: int
    status: str
    decision_ref: str | None = None


class ClaimNullifierRegistry:
    """In-process atomic duplicate-claim admission registry."""

    def __init__(self, *, max_records: int = MAX_CLAIM_NULLIFIER_RECORDS) -> None:
        if isinstance(max_records, bool) or not isinstance(max_records, int) or max_records <= 0:
            raise ClaimNullifierRegistryError(
                "claim_nullifier_registry_max_records_invalid_phase_1428_audit_fix",
                "max_records must be a positive integer",
            )
        self._lock = Lock()
        self._max_records = max_records
        self._records: dict[str, ClaimNullifierRecord] = {}
        self._presentation_ids: dict[str, str] = {}
        self._presentation_canonicals: dict[str, str] = {}
        self._proof_refs: dict[tuple[str, str], str] = {}
        self._conversion_receipts: dict[str, str] = {}
        self._conversion_lots: dict[tuple[str, str], str] = {}

    def reserve_presentation(
        self,
        presentation: Mapping[str, Any],
        *,
        current_issuance_epoch: int | None = None,
    ) -> ClaimNullifierRecord:
        """Atomically reserve a presentation before verifier/economic processing."""

        candidate = build_claim_nullifier_record(
            presentation,
            current_issuance_epoch=current_issuance_epoch,
        )
        with self._lock:
            self._expire_stale_records_locked(candidate.first_seen_issuance_epoch)
            if len(self._records) >= self._max_records:
                raise ClaimNullifierRegistryError(
                    "claim_nullifier_registry_record_limit_exceeded_phase_1428_audit_fix",
                    "claim nullifier registry record limit exceeded",
                )
            self._reject_active_conflict(candidate)
            self._records[candidate.claim_nullifier_ref] = candidate
            self._presentation_ids[candidate.presentation_id] = candidate.claim_nullifier_ref
            self._presentation_canonicals[candidate.presentation_canonical_ref] = (
                candidate.claim_nullifier_ref
            )
            self._proof_refs[
                (candidate.canonical_agent_identity, candidate.claimability_proof_ref)
            ] = candidate.claim_nullifier_ref
            self._conversion_receipts[candidate.conversion_receipt_sha256] = (
                candidate.claim_nullifier_ref
            )
            self._conversion_lots[
                (candidate.canonical_agent_identity, candidate.conversion_lot_id)
            ] = candidate.claim_nullifier_ref
            return candidate

    def mark_accepted(self, claim_nullifier_ref: str, *, decision_ref: str) -> ClaimNullifierRecord:
        return self._replace_status(claim_nullifier_ref, status=ACCEPTED, decision_ref=decision_ref)

    def mark_rejected_nonblocking(self, claim_nullifier_ref: str) -> ClaimNullifierRecord:
        return self._replace_status(
            claim_nullifier_ref,
            status=REJECTED_NONBLOCKING,
            decision_ref=None,
        )

    def get(self, claim_nullifier_ref: str) -> ClaimNullifierRecord | None:
        with self._lock:
            return self._records.get(claim_nullifier_ref)

    def records(self) -> tuple[ClaimNullifierRecord, ...]:
        with self._lock:
            return tuple(self._records.values())

    def expire_stale_records(self, current_issuance_epoch: int) -> int:
        current_epoch = _require_int(current_issuance_epoch, "current_issuance_epoch")
        with self._lock:
            return self._expire_stale_records_locked(current_epoch)

    def _expire_stale_records_locked(self, current_issuance_epoch: int) -> int:
        stale_refs = [
            ref
            for ref, record in self._records.items()
            if record.expires_at_issuance_epoch < current_issuance_epoch
        ]
        for ref in stale_refs:
            self._delete_record_locked(ref)
        return len(stale_refs)

    def _delete_record_locked(self, claim_nullifier_ref: str) -> None:
        record = self._records.pop(claim_nullifier_ref, None)
        if record is None:
            return
        self._presentation_ids.pop(record.presentation_id, None)
        self._presentation_canonicals.pop(record.presentation_canonical_ref, None)
        self._proof_refs.pop((record.canonical_agent_identity, record.claimability_proof_ref), None)
        self._conversion_receipts.pop(record.conversion_receipt_sha256, None)
        self._conversion_lots.pop((record.canonical_agent_identity, record.conversion_lot_id), None)

    def _replace_status(
        self,
        claim_nullifier_ref: str,
        *,
        status: str,
        decision_ref: str | None,
    ) -> ClaimNullifierRecord:
        with self._lock:
            record = self._records.get(claim_nullifier_ref)
            if record is None:
                raise ClaimNullifierRegistryError(
                    "claim_nullifier_registry_missing_phase_1389b",
                    "claim nullifier record is missing",
                )
            updated = ClaimNullifierRecord(
                claim_nullifier_ref=record.claim_nullifier_ref,
                claim_seed_ref=record.claim_seed_ref,
                canonical_agent_identity=record.canonical_agent_identity,
                presentation_id=record.presentation_id,
                presentation_canonical_ref=record.presentation_canonical_ref,
                claimability_proof_ref=record.claimability_proof_ref,
                conversion_receipt_sha256=record.conversion_receipt_sha256,
                conversion_lot_id=record.conversion_lot_id,
                claim_window_start_epoch=record.claim_window_start_epoch,
                claim_window_end_epoch=record.claim_window_end_epoch,
                first_seen_issuance_epoch=record.first_seen_issuance_epoch,
                expires_at_issuance_epoch=record.expires_at_issuance_epoch,
                status=status,
                decision_ref=decision_ref,
            )
            self._records[claim_nullifier_ref] = updated
            return updated

    def _reject_active_conflict(self, candidate: ClaimNullifierRecord) -> None:
        conflict = self._active_conflict(
            "claim_nullifier_ref",
            self._records.get(candidate.claim_nullifier_ref),
            candidate.first_seen_issuance_epoch,
        )
        if conflict is not None:
            raise ClaimNullifierRegistryError(
                "claim_nullifier_replay_rejected_phase_1389b",
                "active claim nullifier already exists",
                conflict_field="claim_nullifier_ref",
            )
        checks = (
            (
                "presentation_id",
                self._presentation_ids.get(candidate.presentation_id),
            ),
            (
                "presentation_canonical_ref",
                self._presentation_canonicals.get(candidate.presentation_canonical_ref),
            ),
            (
                "claimability_proof_ref",
                self._proof_refs.get(
                    (candidate.canonical_agent_identity, candidate.claimability_proof_ref)
                ),
            ),
            (
                "conversion_receipt_sha256",
                self._conversion_receipts.get(candidate.conversion_receipt_sha256),
            ),
            (
                "conversion_lot_id",
                self._conversion_lots.get(
                    (candidate.canonical_agent_identity, candidate.conversion_lot_id)
                ),
            ),
        )
        for field, ref in checks:
            if self._active_conflict(field, ref, candidate.first_seen_issuance_epoch) is not None:
                raise ClaimNullifierRegistryError(
                    "duplicate_claim_rejected_at_api_layer",
                    f"active duplicate claim conflict on {field}",
                    conflict_field=field,
                )

    def _active_conflict(
        self,
        _field: str,
        ref_or_record: str | ClaimNullifierRecord | None,
        current_issuance_epoch: int,
    ) -> ClaimNullifierRecord | None:
        if ref_or_record is None:
            return None
        record = (
            ref_or_record
            if isinstance(ref_or_record, ClaimNullifierRecord)
            else self._records.get(ref_or_record)
        )
        if record is None:
            return None
        if (
            record.status in ACTIVE_STATUSES
            and record.expires_at_issuance_epoch >= current_issuance_epoch
        ):
            return record
        return None


def build_claim_nullifier_record(
    presentation: Mapping[str, Any],
    *,
    current_issuance_epoch: int | None = None,
) -> ClaimNullifierRecord:
    if not isinstance(presentation, Mapping):
        raise ClaimNullifierRegistryError(
            "claim_nullifier_presentation_not_object_phase_1389b",
            "presentation must be an object",
        )
    _reject_unsafe_json_tree(presentation)
    agent = _require_text(presentation.get("canonical_agent_identity"), "canonical_agent_identity")
    presentation_id = _require_text(presentation.get("presentation_id"), "presentation_id")
    proof_ref = _require_text(presentation.get("claimability_proof_ref"), "claimability_proof_ref")
    conversion_receipt_sha256 = _require_text(
        presentation.get("conversion_receipt_sha256"),
        "conversion_receipt_sha256",
    )
    lot_id = _require_text(presentation.get("conversion_lot_id"), "conversion_lot_id")
    issue_epoch = _require_int(
        presentation.get("conversion_issuance_epoch"),
        "conversion_issuance_epoch",
    )
    deadline_epoch = _require_int(
        presentation.get("conversion_deadline_epoch"),
        "conversion_deadline_epoch",
    )
    if deadline_epoch < issue_epoch:
        raise ClaimNullifierRegistryError(
            "claim_nullifier_epoch_window_invalid_phase_1389b",
            "claim window end must be >= start",
        )
    seen_epoch = current_issuance_epoch if current_issuance_epoch is not None else issue_epoch
    first_seen_epoch = _require_int(seen_epoch, "current_issuance_epoch")
    claim_window_start = issue_epoch
    claim_window_end = deadline_epoch
    if first_seen_epoch < claim_window_start:
        raise ClaimNullifierRegistryError(
            "claim_window_not_open_phase_1389b",
            "claim window is not open",
        )
    if first_seen_epoch > claim_window_end:
        raise ClaimNullifierRegistryError(
            "claim_window_closed_phase_1389b",
            "claim window is closed",
        )
    nullifier_input = {
        "canonical_agent_identity": agent,
        "claim_epoch": issue_epoch,
        "claim_window_end_epoch": claim_window_end,
        "claim_window_start_epoch": claim_window_start,
        "claimability_proof_ref": proof_ref,
        "conversion_deadline_epoch": deadline_epoch,
        "conversion_issuance_epoch": issue_epoch,
        "conversion_lot_id": lot_id,
        "conversion_receipt_sha256": conversion_receipt_sha256,
        "domain": CLAIM_NULLIFIER_DOMAIN,
        "latest_balance_receipt_ref": _require_text(
            presentation.get("latest_balance_receipt_ref"),
            "latest_balance_receipt_ref",
        ),
        "presentation_id": presentation_id,
        "public_economics_admission_ref": PUBLIC_ECONOMICS_ADMISSION_REF,
        "settled_runtime_root": _require_text(
            presentation.get("settled_runtime_root"),
            "settled_runtime_root",
        ),
        "transport_principal_ref": _require_text(
            presentation.get("transport_principal_ref"),
            "transport_principal_ref",
        ),
        "version": CLAIM_NULLIFIER_REGISTRY_VERSION,
        "wallet_state_root": _require_text(presentation.get("wallet_state_root"), "wallet_state_root"),
    }
    claim_seed_hash = _sha256_canonical(nullifier_input)
    claim_nullifier_hash = _sha256_canonical(
        {
            "claim_seed_sha256": claim_seed_hash,
            "domain": CLAIM_NULLIFIER_DOMAIN,
            "version": CLAIM_NULLIFIER_REGISTRY_VERSION,
        }
    )
    presentation_hash = _sha256_canonical(
        {
            "canonical_presentation": presentation,
            "domain": "ilc-public-claim-presentation-v1",
            "version": CLAIM_NULLIFIER_REGISTRY_VERSION,
        }
    )
    return ClaimNullifierRecord(
        claim_nullifier_ref=f"{CLAIM_NULLIFIER_PREFIX}:{claim_nullifier_hash}",
        claim_seed_ref=f"{CLAIM_SEED_PREFIX}:{claim_seed_hash}",
        canonical_agent_identity=agent,
        presentation_id=presentation_id,
        presentation_canonical_ref=f"{PRESENTATION_CANONICAL_PREFIX}:{presentation_hash}",
        claimability_proof_ref=proof_ref,
        conversion_receipt_sha256=conversion_receipt_sha256,
        conversion_lot_id=lot_id,
        claim_window_start_epoch=claim_window_start,
        claim_window_end_epoch=claim_window_end,
        first_seen_issuance_epoch=first_seen_epoch,
        expires_at_issuance_epoch=(
            max(claim_window_end, deadline_epoch) + CLAIM_NULLIFIER_POST_WINDOW_RETENTION_EPOCHS
        ),
        status=PENDING,
    )


def _sha256_canonical(payload: Any) -> str:
    try:
        _reject_unsafe_json_tree(payload)
        rendered = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ClaimNullifierRegistryError(
            "claim_nullifier_canonical_serialization_failed_phase_1410_fix1",
            f"payload is not JSON-serializable: {exc}",
        ) from exc
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def _reject_unsafe_json_tree(
    value: Any,
    *,
    _depth: int = 0,
    _seen: set[int] | None = None,
    _counter: list[int] | None = None,
    _text_counter: list[int] | None = None,
) -> None:
    if _depth > _MAX_CANONICAL_PAYLOAD_DEPTH:
        raise ClaimNullifierRegistryError(
            "claim_nullifier_payload_too_deep_phase_1428_audit_fix",
            "canonical payload exceeds maximum traversal depth",
        )
    if _seen is None:
        _seen = set()
    if _counter is None:
        _counter = [0]
    if _text_counter is None:
        _text_counter = [0]
    _counter[0] += 1
    if _counter[0] > _MAX_CANONICAL_PAYLOAD_NODES:
        raise ClaimNullifierRegistryError(
            "claim_nullifier_payload_too_large_phase_1428_audit_fix",
            "canonical payload exceeds maximum traversal size",
        )
    if isinstance(value, float):
        raise ClaimNullifierRegistryError(
            "claim_nullifier_payload_float_forbidden_phase_1428_audit_fix",
            "float is forbidden in claim nullifier payloads",
        )
    if isinstance(value, bool) or value is None:
        return
    if isinstance(value, int):
        if value < 0 or value > _MAX_PROTOCOL_INT:
            raise ClaimNullifierRegistryError(
                "claim_nullifier_payload_int_invalid_phase_1428_audit_fix",
                "canonical payload integer exceeds the registry bound",
            )
        return
    if isinstance(value, str):
        if len(value) > _MAX_TEXT_LENGTH:
            raise ClaimNullifierRegistryError(
                "claim_nullifier_payload_text_too_large_phase_1428_audit_fix",
                "canonical payload string exceeds maximum length",
            )
        if any(ord(char) < 0x20 or char == "\x7f" for char in value):
            raise ClaimNullifierRegistryError(
                "claim_nullifier_payload_text_invalid_phase_1428_audit_fix",
                "canonical payload string contains a control character",
            )
        _text_counter[0] += len(value)
        if _text_counter[0] > _MAX_CANONICAL_PAYLOAD_TEXT_BYTES:
            raise ClaimNullifierRegistryError(
                "claim_nullifier_payload_text_too_large_phase_1428_audit_fix",
                "canonical payload aggregate text exceeds maximum size",
            )
        return
    if isinstance(value, Mapping):
        object_id = id(value)
        if object_id in _seen:
            raise ClaimNullifierRegistryError(
                "claim_nullifier_payload_cycle_forbidden_phase_1428_audit_fix",
                "canonical payload must not contain cycles",
            )
        _seen.add(object_id)
        try:
            for key, item in value.items():
                if not isinstance(key, str):
                    raise ClaimNullifierRegistryError(
                        "claim_nullifier_payload_key_invalid_phase_1428_audit_fix",
                        "canonical payload keys must be strings",
                    )
                _reject_unsafe_json_tree(
                    key,
                    _depth=_depth + 1,
                    _seen=_seen,
                    _counter=_counter,
                    _text_counter=_text_counter,
                )
                _reject_unsafe_json_tree(
                    item,
                    _depth=_depth + 1,
                    _seen=_seen,
                    _counter=_counter,
                    _text_counter=_text_counter,
                )
        finally:
            _seen.remove(object_id)
        return
    if isinstance(value, list):
        object_id = id(value)
        if object_id in _seen:
            raise ClaimNullifierRegistryError(
                "claim_nullifier_payload_cycle_forbidden_phase_1428_audit_fix",
                "canonical payload must not contain cycles",
            )
        _seen.add(object_id)
        try:
            for item in value:
                _reject_unsafe_json_tree(
                    item,
                    _depth=_depth + 1,
                    _seen=_seen,
                    _counter=_counter,
                    _text_counter=_text_counter,
                )
        finally:
            _seen.remove(object_id)
        return
    raise ClaimNullifierRegistryError(
        "claim_nullifier_canonical_serialization_failed_phase_1410_fix1",
        "payload is not JSON-serializable",
    )


def _require_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ClaimNullifierRegistryError(
            "claim_nullifier_input_invalid_phase_1389b",
            f"{field} must be a non-empty canonical string",
            conflict_field=field,
        )
    return value


def _require_int(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ClaimNullifierRegistryError(
            "claim_nullifier_input_invalid_phase_1389b",
            f"{field} must be a non-negative integer",
            conflict_field=field,
        )
    return value


__all__ = [
    "ACCEPTED",
    "ACTIVE_STATUSES",
    "CLAIMABILITY_VERIFIER_PUBLIC_MODE_READY_TOKEN",
    "CLAIM_NULLIFIER_DOMAIN",
    "CLAIM_NULLIFIER_REGISTRY_ACTIVE_TOKEN",
    "CLAIM_NULLIFIER_REGISTRY_VERSION",
    "DUPLICATE_CLAIM_REGISTRY_ACTIVE_TOKEN",
    "MAX_CLAIM_NULLIFIER_RECORDS",
    "PENDING",
    "REJECTED_NONBLOCKING",
    "ClaimNullifierRecord",
    "ClaimNullifierRegistry",
    "ClaimNullifierRegistryError",
    "build_claim_nullifier_record",
]
