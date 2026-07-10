# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1562 invitation provenance records.

PUBLIC_RC_EXCLUDE: private_invitation_provenance_record
PUBLIC_RC_EXCLUDE_REASON: Private pre-RC invitation provenance evidence. Does not activate invitation economics, public serving, or public RC.
"""

from __future__ import annotations

import hashlib
import os
import secrets
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Mapping

from ilc_core.private_json_guardrails import canonical_json, reject_float

INVITATION_PROVENANCE_RUNTIME_VERSION = "invitation_provenance_chain_runtime_1562.v0.1"
INVITE_BATCH_RUNTIME_VERSION = "invite_batch_runtime_1573z.v0.1"
INVITE_NULLIFIER_DOMAIN = b"ilc-invite-nullifier-v1:"
INVITE_NONCE_LEAF_DOMAIN = b"ilc-invite-nonce-leaf-v1:"
INVITE_NONCE_NODE_DOMAIN = b"ilc-invite-nonce-node-v1:"
AGENT_ID_DERIVATION_DOMAIN = b"ilc-agent-id-v1:"


class SigningLevel(Enum):
    AUTONOMOUS = "autonomous"
    SESSION = "session"
    MANUAL = "manual"


DEFAULT_SIGNING_LEVEL = SigningLevel.AUTONOMOUS


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


@dataclass(frozen=True)
class InviteBatchRecord:
    inviter_cid: str
    batch_id: str
    count: int
    nonce_merkle_root: str
    created_epoch: int
    inviter_sig: str

    def to_dict(self) -> dict[str, object]:
        return {
            "batch_id": self.batch_id,
            "count": self.count,
            "created_epoch": self.created_epoch,
            "inviter_cid": self.inviter_cid,
            "inviter_sig": self.inviter_sig,
            "nonce_merkle_root": self.nonce_merkle_root,
        }

    def canonical_cid(self) -> str:
        _validate_invite_batch_record(self)
        return _sha256_payload(
            {
                "record": self.to_dict(),
                "rule_version": INVITE_BATCH_RUNTIME_VERSION,
            }
        )


@dataclass(frozen=True)
class InviteRedemptionRecord:
    batch_id: str
    redemption_nullifier: str
    nonce_membership_proof: tuple[str, ...]
    redeemer_pubkey_cid: str
    redeemer_agent_id: str
    redemption_epoch: int
    inviter_cid: str

    def to_dict(self) -> dict[str, object]:
        return {
            "batch_id": self.batch_id,
            "inviter_cid": self.inviter_cid,
            "nonce_membership_proof": self.nonce_membership_proof,
            "redeemer_agent_id": self.redeemer_agent_id,
            "redeemer_pubkey_cid": self.redeemer_pubkey_cid,
            "redemption_epoch": self.redemption_epoch,
            "redemption_nullifier": self.redemption_nullifier,
        }

    def canonical_cid(self) -> str:
        _validate_invite_redemption_record(self)
        return _sha256_payload(
            {
                "record": self.to_dict(),
                "rule_version": INVITE_BATCH_RUNTIME_VERSION,
            }
        )


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


def build_invite_batch_record(
    *,
    inviter_cid: str,
    batch_id: str,
    count: int,
    created_epoch: int,
    inviter_sig: str,
    nonces: tuple[bytes, ...] | None = None,
) -> tuple[InviteBatchRecord, tuple[str, ...]]:
    _require_non_empty_str(inviter_cid, "invite_batch_missing_inviter_cid")
    _require_non_empty_str(batch_id, "invite_batch_missing_batch_id")
    _require_positive_count(count)
    _require_protocol_epoch(created_epoch)
    _require_non_empty_str(inviter_sig, "invite_batch_missing_inviter_sig")
    nonce_values = nonces if nonces is not None else tuple(secrets.token_bytes(32) for _ in range(count))
    if len(nonce_values) != count:
        raise InvitationProvenanceError("invite_batch_nonce_count_mismatch")
    for nonce in nonce_values:
        _require_nonce_bytes(nonce)
    record = InviteBatchRecord(
        inviter_cid=inviter_cid,
        batch_id=batch_id,
        count=count,
        nonce_merkle_root=invite_nonce_merkle_root(nonce_values),
        created_epoch=created_epoch,
        inviter_sig=inviter_sig,
    )
    _validate_invite_batch_record(record)
    return record, tuple(nonce.hex() for nonce in nonce_values)


def build_invite_redemption_record(
    *,
    batch: InviteBatchRecord,
    nonce: bytes | str,
    nonce_membership_proof: tuple[str, ...],
    redeemer_pubkey_cid: str,
    identity_seed: bytes | str,
    redemption_epoch: int,
) -> InviteRedemptionRecord:
    _validate_invite_batch_record(batch)
    _require_protocol_epoch(redemption_epoch)
    _require_non_empty_str(redeemer_pubkey_cid, "invite_redemption_missing_redeemer_pubkey_cid")
    record = InviteRedemptionRecord(
        batch_id=batch.batch_id,
        redemption_nullifier=derive_invite_redemption_nullifier(batch.batch_id, nonce),
        nonce_membership_proof=nonce_membership_proof,
        redeemer_pubkey_cid=redeemer_pubkey_cid,
        redeemer_agent_id=derive_agent_id_from_identity_seed(identity_seed),
        redemption_epoch=redemption_epoch,
        inviter_cid=batch.inviter_cid,
    )
    _validate_invite_redemption_record(record)
    return record


def derive_invite_redemption_nullifier(batch_id: str, nonce: bytes | str) -> str:
    _require_non_empty_str(batch_id, "invite_redemption_missing_batch_id")
    nonce_bytes = _coerce_nonce_bytes(nonce)
    return hashlib.sha256(INVITE_NULLIFIER_DOMAIN + batch_id.encode("utf-8") + b":" + nonce_bytes).hexdigest()


def derive_agent_id_from_identity_seed(identity_seed: bytes | str) -> str:
    seed = _coerce_identity_seed_bytes(identity_seed)
    return hashlib.sha384(AGENT_ID_DERIVATION_DOMAIN + seed).hexdigest()


def invite_nonce_merkle_root(nonces: tuple[bytes, ...]) -> str:
    if len(nonces) == 0:
        raise InvitationProvenanceError("invite_batch_empty_nonce_set")
    level = [_invite_nonce_leaf_hash(nonce) for nonce in nonces]
    while len(level) > 1:
        next_level: list[bytes] = []
        for index in range(0, len(level), 2):
            left = level[index]
            right = level[index + 1] if index + 1 < len(level) else left
            next_level.append(hashlib.sha256(INVITE_NONCE_NODE_DOMAIN + left + right).digest())
        level = next_level
    return level[0].hex()


def invite_batch_record_from_dict(payload: Mapping[str, object]) -> InviteBatchRecord:
    reject_float(payload, "invite_batch_float_not_allowed")
    record = InviteBatchRecord(
        inviter_cid=_required_str(payload, "inviter_cid"),
        batch_id=_required_str(payload, "batch_id"),
        count=_required_int(payload, "count"),
        nonce_merkle_root=_required_str(payload, "nonce_merkle_root"),
        created_epoch=_required_int(payload, "created_epoch"),
        inviter_sig=_required_str(payload, "inviter_sig"),
    )
    _validate_invite_batch_record(record)
    return record


def invite_redemption_record_from_dict(payload: Mapping[str, object]) -> InviteRedemptionRecord:
    reject_float(payload, "invite_redemption_float_not_allowed")
    proof = payload.get("nonce_membership_proof")
    if not isinstance(proof, (list, tuple)) or any(not isinstance(item, str) for item in proof):
        raise InvitationProvenanceError("invite_redemption_invalid_nonce_membership_proof")
    record = InviteRedemptionRecord(
        batch_id=_required_str(payload, "batch_id"),
        redemption_nullifier=_required_str(payload, "redemption_nullifier"),
        nonce_membership_proof=tuple(proof),
        redeemer_pubkey_cid=_required_str(payload, "redeemer_pubkey_cid"),
        redeemer_agent_id=_required_str(payload, "redeemer_agent_id"),
        redemption_epoch=_required_int(payload, "redemption_epoch"),
        inviter_cid=_required_str(payload, "inviter_cid"),
    )
    _validate_invite_redemption_record(record)
    return record


def invite_record_canonical_json(record: InviteBatchRecord | InviteRedemptionRecord) -> str:
    return canonical_json(
        record.to_dict(),
        float_token="invite_record_float_not_allowed",
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


def _invite_nonce_leaf_hash(nonce: bytes) -> bytes:
    _require_nonce_bytes(nonce)
    return hashlib.sha256(INVITE_NONCE_LEAF_DOMAIN + nonce).digest()


def _validate_invite_batch_record(record: InviteBatchRecord) -> None:
    reject_float(record.to_dict(), "invite_batch_float_not_allowed")
    _require_non_empty_str(record.inviter_cid, "invite_batch_missing_inviter_cid")
    _require_non_empty_str(record.batch_id, "invite_batch_missing_batch_id")
    _require_positive_count(record.count)
    _require_sha256_hex(record.nonce_merkle_root, "invite_batch_invalid_nonce_merkle_root")
    _require_protocol_epoch(record.created_epoch)
    _require_non_empty_str(record.inviter_sig, "invite_batch_missing_inviter_sig")


def _validate_invite_redemption_record(record: InviteRedemptionRecord) -> None:
    reject_float(record.to_dict(), "invite_redemption_float_not_allowed")
    _require_non_empty_str(record.batch_id, "invite_redemption_missing_batch_id")
    _require_sha256_hex(record.redemption_nullifier, "invite_redemption_invalid_nullifier")
    for proof_hash in record.nonce_membership_proof:
        _require_sha256_hex(proof_hash, "invite_redemption_invalid_nonce_membership_proof")
    _require_non_empty_str(record.redeemer_pubkey_cid, "invite_redemption_missing_redeemer_pubkey_cid")
    _require_non_empty_str(record.redeemer_agent_id, "invite_redemption_missing_redeemer_agent_id")
    _require_protocol_epoch(record.redemption_epoch)
    _require_non_empty_str(record.inviter_cid, "invite_redemption_missing_inviter_cid")


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


def _require_positive_count(value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise InvitationProvenanceError("invite_batch_invalid_count")


def _require_sha256_hex(value: object, token: str) -> None:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(char not in "0123456789abcdef" for char in value)
    ):
        raise InvitationProvenanceError(token)


def _require_nonce_bytes(value: object) -> None:
    if not isinstance(value, bytes) or len(value) == 0:
        raise InvitationProvenanceError("invite_nonce_invalid")


def _coerce_nonce_bytes(value: bytes | str) -> bytes:
    if isinstance(value, bytes):
        _require_nonce_bytes(value)
        return value
    if isinstance(value, str):
        try:
            nonce = bytes.fromhex(value)
        except ValueError as exc:
            raise InvitationProvenanceError("invite_nonce_invalid") from exc
        _require_nonce_bytes(nonce)
        return nonce
    raise InvitationProvenanceError("invite_nonce_invalid")


def _coerce_identity_seed_bytes(value: bytes | str) -> bytes:
    if isinstance(value, bytes):
        if len(value) == 0:
            raise InvitationProvenanceError("identity_seed_invalid")
        return value
    if isinstance(value, str):
        try:
            seed = bytes.fromhex(value)
        except ValueError as exc:
            raise InvitationProvenanceError("identity_seed_invalid") from exc
        if len(seed) == 0:
            raise InvitationProvenanceError("identity_seed_invalid")
        return seed
    raise InvitationProvenanceError("identity_seed_invalid")


__all__ = [
    "AGENT_ID_DERIVATION_DOMAIN",
    "DEFAULT_SIGNING_LEVEL",
    "INVITE_BATCH_RUNTIME_VERSION",
    "INVITE_NULLIFIER_DOMAIN",
    "INVITATION_PROVENANCE_RUNTIME_VERSION",
    "InviteBatchRecord",
    "InviteRedemptionRecord",
    "InvitationProvenanceError",
    "InvitationProvenanceRecord",
    "SigningLevel",
    "build_invite_batch_record",
    "build_invite_redemption_record",
    "build_invitation_record",
    "derive_agent_id_from_identity_seed",
    "derive_invite_redemption_nullifier",
    "invite_batch_record_from_dict",
    "invite_nonce_merkle_root",
    "invite_record_canonical_json",
    "invite_redemption_record_from_dict",
    "invitation_record_from_dict",
    "verify_chain_depth",
    "verify_record_hash",
    "write_invitation_record_json",
]
