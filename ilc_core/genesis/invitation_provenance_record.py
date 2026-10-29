# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1562 invitation provenance records.

"""

from __future__ import annotations

import hashlib
import os
import secrets
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, Mapping

from ilc_core.private_json_guardrails import canonical_json, reject_float

INVITATION_PROVENANCE_RUNTIME_VERSION = "invitation_provenance_chain_runtime_1562.v0.1"
INVITE_BATCH_RUNTIME_VERSION = "invite_batch_runtime_1573z.v0.1"
INVITE_NULLIFIER_DOMAIN = b"ilc-invite-nullifier-v1:"
INVITE_NONCE_LEAF_DOMAIN = b"ilc-invite-nonce-leaf-v1:"
INVITE_NONCE_NODE_DOMAIN = b"ilc-invite-nonce-node-v1:"
INVITE_NONCE_BYTES = 32
MAX_INVITE_BATCH_SIZE = 500
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
    nonce_membership_proof: tuple[Mapping[str, object], ...]
    redeemer_pubkey_cid: str
    redeemer_agent_id: str
    redemption_epoch: int
    inviter_cid: str
    invite_id: str | None = None
    redeemer_key_binding: Mapping[str, object] | None = None

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "batch_id": self.batch_id,
            "inviter_cid": self.inviter_cid,
            "nonce_membership_proof": [
                dict(step) for step in self.nonce_membership_proof
            ],
            "redeemer_key_binding": (
                dict(self.redeemer_key_binding)
                if self.redeemer_key_binding is not None
                else None
            ),
            "redeemer_agent_id": self.redeemer_agent_id,
            "redeemer_pubkey_cid": self.redeemer_pubkey_cid,
            "redemption_epoch": self.redemption_epoch,
            "redemption_nullifier": self.redemption_nullifier,
        }
        if self.invite_id is not None:
            payload["invite_id"] = self.invite_id
        return payload

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
    nonce_membership_proof: tuple[Mapping[str, object], ...],
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
        invite_id=batch.batch_id,
        redeemer_key_binding=None,
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


def build_nonce_membership_proof(
    *,
    nonces: tuple[bytes, ...],
    nonce_index: int,
) -> tuple[dict[str, str], ...]:
    """Build the canonical Merkle proof for one invite nonce."""

    if len(nonces) == 0:
        raise InvitationProvenanceError("invite_batch_empty_nonce_set")
    if isinstance(nonce_index, bool) or not isinstance(nonce_index, int):
        raise InvitationProvenanceError("invite_nonce_membership_index_invalid")
    if nonce_index < 0 or nonce_index >= len(nonces):
        raise InvitationProvenanceError("invite_nonce_membership_index_invalid")
    for nonce in nonces:
        _require_nonce_bytes(nonce)

    root = invite_nonce_merkle_root(nonces)
    proof: list[dict[str, str]] = []
    index = nonce_index
    level = [_invite_nonce_leaf_hash(nonce) for nonce in nonces]
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        sibling_index = index - 1 if index % 2 else index + 1
        proof.append(
            {
                "position": "left" if index % 2 else "right",
                "sibling": level[sibling_index].hex(),
            }
        )
        next_level: list[bytes] = []
        for pair_index in range(0, len(level), 2):
            next_level.append(
                hashlib.sha256(
                    INVITE_NONCE_NODE_DOMAIN + level[pair_index] + level[pair_index + 1]
                ).digest()
            )
        level = next_level
        index //= 2
    verify_nonce_membership_proof(
        nonce_bytes=nonces[nonce_index],
        nonce_merkle_root=root,
        count=len(nonces),
        proof=tuple(proof),
    )
    return tuple(proof)


def verify_nonce_membership_proof(
    *,
    nonce_bytes: bytes,
    nonce_merkle_root: str,
    count: int,
    proof: tuple[dict[str, object], ...],
) -> None:
    """Verify nonce membership in an invite batch Merkle tree.

    This is the canonical raise-on-fail form of the OpenClaw invite nonce
    proof algorithm. It is a utility only; this module does not activate invite
    enforcement or nullifier propagation.
    """
    _require_nonce_bytes(nonce_bytes)
    _require_sha256_hex(nonce_merkle_root, "invite_nonce_membership_root_invalid")
    _require_positive_count(count)
    if not isinstance(proof, tuple):
        raise InvitationProvenanceError("invite_nonce_membership_proof_invalid")
    expected_length = _invite_nonce_merkle_proof_length(count)
    if len(proof) != expected_length:
        token = (
            "invite_nonce_membership_proof_required"
            if expected_length > 0 and len(proof) == 0
            else "invite_nonce_membership_proof_length_invalid"
        )
        raise InvitationProvenanceError(token)

    digest = _invite_nonce_leaf_hash(nonce_bytes)
    if count == 1:
        if digest.hex() != nonce_merkle_root:
            raise InvitationProvenanceError("invite_nonce_membership_mismatch")
        return

    for item in proof:
        if not isinstance(item, Mapping):
            raise InvitationProvenanceError("invite_nonce_membership_proof_invalid")
        sibling = item.get("sibling")
        position = item.get("position")
        _require_sha256_hex(sibling, "invite_nonce_membership_proof_invalid")
        sibling_bytes = bytes.fromhex(str(sibling))
        if position == "left":
            digest = hashlib.sha256(INVITE_NONCE_NODE_DOMAIN + sibling_bytes + digest).digest()
        elif position == "right":
            digest = hashlib.sha256(INVITE_NONCE_NODE_DOMAIN + digest + sibling_bytes).digest()
        else:
            raise InvitationProvenanceError("invite_nonce_membership_proof_invalid")
    if digest.hex() != nonce_merkle_root:
        raise InvitationProvenanceError("invite_nonce_membership_mismatch")


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
    proof = _nonce_membership_proof(payload.get("nonce_membership_proof"))
    record = InviteRedemptionRecord(
        batch_id=_required_str(payload, "batch_id"),
        redemption_nullifier=_required_str(payload, "redemption_nullifier"),
        nonce_membership_proof=proof,
        redeemer_pubkey_cid=_required_str(payload, "redeemer_pubkey_cid"),
        redeemer_agent_id=_required_str(payload, "redeemer_agent_id"),
        redemption_epoch=_required_int(payload, "redemption_epoch"),
        inviter_cid=_required_str(payload, "inviter_cid"),
        invite_id=_optional_str(payload.get("invite_id")),
        redeemer_key_binding=_optional_mapping(payload.get("redeemer_key_binding")),
    )
    _validate_invite_redemption_record(record)
    return record


def validate_invite_redemption_record(
    record: InviteRedemptionRecord | Mapping[str, object],
) -> InviteRedemptionRecord:
    """Validate an invite redemption record and return the canonical dataclass.

    Phase 1576n exposes the prior internal validator as the public enforcement
    boundary used by enrollment gates. Later onboarding hardening allows a
    nullable invite_id for PoP-bound redemptions while preserving legacy records.
    """

    if isinstance(record, InviteRedemptionRecord):
        _validate_invite_redemption_record(record)
        return record
    if isinstance(record, Mapping):
        return invite_redemption_record_from_dict(record)
    raise InvitationProvenanceError("invite_redemption_record_invalid")


InvitePopVerifier = Callable[..., bool]


def verify_invite_redemption_redeemer_key_binding(
    record: InviteRedemptionRecord | Mapping[str, object],
    *,
    invite_pop_verifier: InvitePopVerifier | None = None,
) -> InviteRedemptionRecord:
    """Verify the BLS PoP binding for an invite redemption record."""

    normalized = validate_invite_redemption_record(record)
    if normalized.invite_id is None:
        raise InvitationProvenanceError("invite_redemption_invite_id_required_for_pop")
    binding = normalized.redeemer_key_binding
    if binding is None:
        raise InvitationProvenanceError("invite_redemption_redeemer_key_binding_required")

    from ilc_core.identity.first_run_provisioning import (
        invite_pop_payload_ref,
        verify_invite_pop,
    )

    payload_ref = str(binding.get("payload_ref"))
    expected_payload_ref = invite_pop_payload_ref(
        agent_id_hex=normalized.redeemer_agent_id,
        invite_nullifier=normalized.redemption_nullifier,
        invite_id=normalized.invite_id,
        epoch=normalized.redemption_epoch,
    )
    if payload_ref != expected_payload_ref:
        raise InvitationProvenanceError("invite_redemption_redeemer_key_binding_payload_mismatch")

    verifier = invite_pop_verifier or verify_invite_pop
    if not verifier(
        agent_id_hex=normalized.redeemer_agent_id,
        invite_nullifier=normalized.redemption_nullifier,
        invite_id=normalized.invite_id,
        epoch=normalized.redemption_epoch,
        invite_pop=str(binding.get("signature")),
    ):
        raise InvitationProvenanceError("invite_redemption_redeemer_key_binding_invalid")
    return normalized


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


def _invite_nonce_merkle_proof_length(count: int) -> int:
    _require_positive_count(count)
    length = 0
    width = count
    while width > 1:
        length += 1
        width = (width + 1) // 2
    return length


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
    _validate_nonce_membership_proof(record.nonce_membership_proof)
    _require_non_empty_str(record.redeemer_pubkey_cid, "invite_redemption_missing_redeemer_pubkey_cid")
    _require_non_empty_str(record.redeemer_agent_id, "invite_redemption_missing_redeemer_agent_id")
    _require_protocol_epoch(record.redemption_epoch)
    _require_non_empty_str(record.inviter_cid, "invite_redemption_missing_inviter_cid")
    if record.invite_id is not None:
        _require_non_empty_str(record.invite_id, "invite_redemption_invalid_invite_id")
    if record.redeemer_key_binding is not None:
        _validate_redeemer_key_binding(record.redeemer_key_binding)


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


def _optional_mapping(value: object) -> Mapping[str, object] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise InvitationProvenanceError("invite_redemption_invalid_redeemer_key_binding")
    return dict(value)


def _nonce_membership_proof(
    value: object,
) -> tuple[Mapping[str, object], ...]:
    if not isinstance(value, (list, tuple)):
        raise InvitationProvenanceError("invite_redemption_invalid_nonce_membership_proof")
    return tuple(_nonce_membership_proof_step(item) for item in value)


def _validate_nonce_membership_proof(
    value: tuple[Mapping[str, object], ...],
) -> None:
    if not isinstance(value, tuple):
        raise InvitationProvenanceError("invite_redemption_invalid_nonce_membership_proof")
    for step in value:
        _nonce_membership_proof_step(step)


def _nonce_membership_proof_step(value: object) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise InvitationProvenanceError("invite_redemption_invalid_nonce_membership_proof")
    sibling = value.get("sibling")
    position = value.get("position")
    _require_sha256_hex(sibling, "invite_redemption_invalid_nonce_membership_proof")
    if position not in {"left", "right"}:
        raise InvitationProvenanceError("invite_redemption_invalid_nonce_membership_proof")
    return {
        "position": str(position),
        "sibling": str(sibling),
    }


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or value == "":
        raise InvitationProvenanceError("invite_redemption_invalid_invite_id")
    return value


def _validate_redeemer_key_binding(value: Mapping[str, object]) -> None:
    reject_float(value, "invite_redemption_float_not_allowed")
    if value.get("domain") != "ilc-invite-pop-v1":
        raise InvitationProvenanceError("invite_redemption_invalid_redeemer_key_binding")
    _require_sha384_hex(
        value.get("payload_ref"),
        "invite_redemption_invalid_redeemer_key_binding",
    )
    _require_bls_signature_hex(
        value.get("signature"),
        "invite_redemption_invalid_redeemer_key_binding",
    )


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
    if value > MAX_INVITE_BATCH_SIZE:
        raise InvitationProvenanceError("invite_batch_count_exceeds_max")


def _require_sha256_hex(value: object, token: str) -> None:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(char not in "0123456789abcdef" for char in value)
    ):
        raise InvitationProvenanceError(token)


def _require_sha384_hex(value: object, token: str) -> None:
    if (
        not isinstance(value, str)
        or len(value) != 96
        or any(char not in "0123456789abcdef" for char in value)
    ):
        raise InvitationProvenanceError(token)


def _require_bls_signature_hex(value: object, token: str) -> None:
    if (
        not isinstance(value, str)
        or len(value) != 192
        or any(char not in "0123456789abcdef" for char in value)
    ):
        raise InvitationProvenanceError(token)


def _require_nonce_bytes(value: object) -> None:
    if not isinstance(value, bytes) or len(value) != INVITE_NONCE_BYTES:
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
    "INVITE_NONCE_BYTES",
    "INVITE_NULLIFIER_DOMAIN",
    "INVITATION_PROVENANCE_RUNTIME_VERSION",
    "MAX_INVITE_BATCH_SIZE",
    "InviteBatchRecord",
    "InviteRedemptionRecord",
    "InvitationProvenanceError",
    "InvitationProvenanceRecord",
    "SigningLevel",
    "build_nonce_membership_proof",
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
    "validate_invite_redemption_record",
    "verify_invite_redemption_redeemer_key_binding",
    "verify_nonce_membership_proof",
    "verify_chain_depth",
    "verify_record_hash",
    "write_invitation_record_json",
]
