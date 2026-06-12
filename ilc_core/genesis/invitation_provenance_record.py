# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1562 invitation provenance records.

PUBLIC_RC_EXCLUDE: private_invitation_provenance_record
PUBLIC_RC_EXCLUDE_REASON: Private pre-RC invitation provenance evidence. Does not activate invitation economics, public serving, or public RC.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from ilc_core.private_json_guardrails import canonical_json, reject_float

INVITATION_PROVENANCE_RUNTIME_VERSION = "invitation_provenance_chain_runtime_1562.v0.1"


class InvitationProvenanceError(ValueError):
    """Stable exception type for Phase 1562 invitation provenance validation."""


@dataclass(frozen=True)
class InvitationProvenanceRecord:
    invite_id: str
    inviter_agent_id: str
    invitee_agent_id: str
    serving_receipt_id: str
    invite_depth: int
    timestamp_epoch: int
    record_hash: str
    rule_version: str
    parent_invite_id: str | None

    def to_dict(self) -> dict[str, object]:
        return {
            "invite_depth": self.invite_depth,
            "invite_id": self.invite_id,
            "invitee_agent_id": self.invitee_agent_id,
            "inviter_agent_id": self.inviter_agent_id,
            "parent_invite_id": self.parent_invite_id,
            "record_hash": self.record_hash,
            "rule_version": self.rule_version,
            "serving_receipt_id": self.serving_receipt_id,
            "timestamp_epoch": self.timestamp_epoch,
        }


def build_invitation_record(
    inviter_agent_id: str,
    invitee_agent_id: str,
    serving_receipt_id: str,
    *,
    timestamp_epoch: int,
    parent_invite_id: str | None = None,
) -> InvitationProvenanceRecord:
    """Construct a direct invitation provenance record.

    Phase 1562 only has enough context to construct depth-1 records. Nested
    records require the parent record set so the depth can be derived without
    trusting caller input.
    """
    if parent_invite_id is not None:
        raise InvitationProvenanceError(
            "invitation_provenance_parent_context_required_for_nested_record"
        )
    _require_non_empty_str(inviter_agent_id, "invitation_provenance_missing_inviter_agent_id")
    _require_non_empty_str(invitee_agent_id, "invitation_provenance_missing_invitee_agent_id")
    _require_non_empty_str(serving_receipt_id, "invitation_provenance_missing_serving_receipt_id")
    _require_protocol_epoch(timestamp_epoch)
    payload = _hash_payload(
        inviter_agent_id=inviter_agent_id,
        invitee_agent_id=invitee_agent_id,
        serving_receipt_id=serving_receipt_id,
        invite_depth=1,
        timestamp_epoch=timestamp_epoch,
        parent_invite_id=None,
        rule_version=INVITATION_PROVENANCE_RUNTIME_VERSION,
    )
    record_hash = _sha256_payload(payload)
    return InvitationProvenanceRecord(
        invite_id=record_hash,
        inviter_agent_id=inviter_agent_id,
        invitee_agent_id=invitee_agent_id,
        serving_receipt_id=serving_receipt_id,
        invite_depth=1,
        timestamp_epoch=timestamp_epoch,
        record_hash=record_hash,
        rule_version=INVITATION_PROVENANCE_RUNTIME_VERSION,
        parent_invite_id=None,
    )


def invitation_record_from_dict(payload: Mapping[str, object]) -> InvitationProvenanceRecord:
    reject_float(payload, "invitation_provenance_float_not_allowed")
    parent = payload.get("parent_invite_id")
    if parent is not None and not isinstance(parent, str):
        raise InvitationProvenanceError("invitation_provenance_invalid_parent_invite_id")
    record = InvitationProvenanceRecord(
        invite_id=_required_str(payload, "invite_id"),
        inviter_agent_id=_required_str(payload, "inviter_agent_id"),
        invitee_agent_id=_required_str(payload, "invitee_agent_id"),
        serving_receipt_id=_required_str(payload, "serving_receipt_id"),
        invite_depth=_required_int(payload, "invite_depth"),
        timestamp_epoch=_required_int(payload, "timestamp_epoch"),
        record_hash=_required_str(payload, "record_hash"),
        rule_version=_required_str(payload, "rule_version"),
        parent_invite_id=parent,
    )
    _validate_record_shape(record)
    return record


def verify_record_hash(record: InvitationProvenanceRecord) -> bool:
    _validate_record_shape(record)
    return record.record_hash == _compute_record_hash(record) and record.invite_id == record.record_hash


def verify_chain_depth(records: list[InvitationProvenanceRecord]) -> bool:
    by_id: dict[str, InvitationProvenanceRecord] = {}
    for record in records:
        _validate_record_shape(record)
        if record.invite_id in by_id:
            raise InvitationProvenanceError("invitation_provenance_duplicate_invite_id")
        by_id[record.invite_id] = record

    visiting: set[str] = set()
    resolved: dict[str, int] = {}

    def depth_for(record: InvitationProvenanceRecord) -> int:
        if record.invite_id in resolved:
            return resolved[record.invite_id]
        if record.invite_id in visiting:
            raise InvitationProvenanceError("invitation_provenance_cycle_detected")
        visiting.add(record.invite_id)
        if record.parent_invite_id is None:
            expected = 1
        else:
            parent = by_id.get(record.parent_invite_id)
            if parent is None:
                raise InvitationProvenanceError("invitation_provenance_parent_not_found")
            expected = depth_for(parent) + 1
        visiting.remove(record.invite_id)
        resolved[record.invite_id] = expected
        return expected

    for record in records:
        if record.invite_depth != depth_for(record):
            return False
        if not verify_record_hash(record):
            return False
    return True


def write_invitation_record_json(record: InvitationProvenanceRecord, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    body = canonical_json(
        record.to_dict(),
        float_token="invitation_provenance_float_not_allowed",
    )
    fd, tmp_name = tempfile.mkstemp(
        dir=target.parent,
        prefix=f".{target.name}.",
        suffix=".tmp",
        text=True,
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(body)
            handle.write("\n")
        os.replace(tmp_path, target)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def _hash_payload(
    *,
    inviter_agent_id: str,
    invitee_agent_id: str,
    serving_receipt_id: str,
    invite_depth: int,
    timestamp_epoch: int,
    parent_invite_id: str | None,
    rule_version: str,
) -> dict[str, object]:
    return {
        "invite_depth": invite_depth,
        "invitee_agent_id": invitee_agent_id,
        "inviter_agent_id": inviter_agent_id,
        "parent_invite_id": parent_invite_id,
        "rule_version": rule_version,
        "serving_receipt_id": serving_receipt_id,
        "timestamp_epoch": timestamp_epoch,
    }


def _compute_record_hash(record: InvitationProvenanceRecord) -> str:
    return _sha256_payload(
        _hash_payload(
            inviter_agent_id=record.inviter_agent_id,
            invitee_agent_id=record.invitee_agent_id,
            serving_receipt_id=record.serving_receipt_id,
            invite_depth=record.invite_depth,
            timestamp_epoch=record.timestamp_epoch,
            parent_invite_id=record.parent_invite_id,
            rule_version=record.rule_version,
        )
    )


def _sha256_payload(payload: Mapping[str, object]) -> str:
    body = canonical_json(payload, float_token="invitation_provenance_float_not_allowed")
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _validate_record_shape(record: InvitationProvenanceRecord) -> None:
    reject_float(record.to_dict(), "invitation_provenance_float_not_allowed")
    _require_non_empty_str(record.invite_id, "invitation_provenance_missing_invite_id")
    _require_non_empty_str(record.inviter_agent_id, "invitation_provenance_missing_inviter_agent_id")
    _require_non_empty_str(record.invitee_agent_id, "invitation_provenance_missing_invitee_agent_id")
    _require_non_empty_str(record.serving_receipt_id, "invitation_provenance_missing_serving_receipt_id")
    _require_positive_depth(record.invite_depth)
    _require_protocol_epoch(record.timestamp_epoch)
    _require_non_empty_str(record.record_hash, "invitation_provenance_missing_record_hash")
    if record.invite_id != record.record_hash:
        raise InvitationProvenanceError("invitation_provenance_invite_id_hash_mismatch")
    if record.rule_version != INVITATION_PROVENANCE_RUNTIME_VERSION:
        raise InvitationProvenanceError("invitation_provenance_invalid_rule_version")
    if record.parent_invite_id is not None:
        _require_non_empty_str(
            record.parent_invite_id,
            "invitation_provenance_invalid_parent_invite_id",
        )


def _required_str(payload: Mapping[str, object], key: str) -> str:
    value = payload.get(key)
    _require_non_empty_str(value, f"invitation_provenance_missing_{key}")
    return value


def _required_int(payload: Mapping[str, object], key: str) -> int:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise InvitationProvenanceError(f"invitation_provenance_invalid_{key}")
    return value


def _require_non_empty_str(value: object, token: str) -> None:
    if not isinstance(value, str) or value == "":
        raise InvitationProvenanceError(token)


def _require_protocol_epoch(value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise InvitationProvenanceError("invitation_provenance_invalid_timestamp_epoch")


def _require_positive_depth(value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise InvitationProvenanceError("invitation_provenance_invalid_invite_depth")


__all__ = [
    "INVITATION_PROVENANCE_RUNTIME_VERSION",
    "InvitationProvenanceError",
    "InvitationProvenanceRecord",
    "build_invitation_record",
    "invitation_record_from_dict",
    "verify_chain_depth",
    "verify_record_hash",
    "write_invitation_record_json",
]
