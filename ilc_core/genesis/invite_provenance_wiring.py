# SPDX-License-Identifier: AGPL-3.0-only
"""Invite provenance edge wiring for CDL-102/CDL-108 attribution.

This module records the graph edge that makes an inviter reachable to the
CDL-108 backward-attribution traversal engine. It does not compute a fixed
inviter reward, mint ECU, settle ILC, or activate production attribution.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from types import SimpleNamespace
from typing import Any, Mapping

from ilc_core.private_json_guardrails import canonical_json, reject_float


INVITE_PROVENANCE_WIRING_VERSION = "invite_provenance_wiring_1576q.v0.1"
INVITE_PROVENANCE_EDGE_TYPE = "PROVENANCE"
INVITE_PROVENANCE_SUBTYPE = "invite_init_origin"
INVITE_CREDIT_MODEL = "organic_cdl_108_backward_attribution"
INVITE_PROVENANCE_PHASE = "1576q"
INVITE_PROVENANCE_GO_PHRASE = "GO Phase 1576q INVITE-PROVENANCE-EDGE"
INVITE_PROVENANCE_OUTPUT_TOKEN = "invite_ecu_credit_runtime_committed_phase_1576q"
INVITE_PROVENANCE_NO_ACTIVATION = "no_invite_ecu_settlement_activation_phase_1576q"

MAX_INVITE_PROVENANCE_STRING_CHARS = 8192
SHA256_HEX_CHARS = 64


class InviteProvenanceWiringError(ValueError):
    """Stable exception type for invite provenance edge validation."""


@dataclass(frozen=True)
class InviteProvenanceEdgeRecord:
    """Canonical invite-init PROVENANCE edge record.

    ``source_node_id`` is the invited agent's INIT/work node. ``target_node_id``
    is the inviter identity or eligible inviter artifact node. CDL-108 traversal
    moves from downstream source to upstream target.
    """

    source_node_id: str
    target_node_id: str
    redemption_nullifier: str
    batch_id: str
    inviter_cid: str
    redeemer_agent_id: str
    redemption_epoch: int
    edge_confidence: Decimal = Decimal("1")
    schema_version: str = INVITE_PROVENANCE_WIRING_VERSION
    edge_type: str = INVITE_PROVENANCE_EDGE_TYPE
    provenance_subtype: str = INVITE_PROVENANCE_SUBTYPE
    invite_credit_model: str = INVITE_CREDIT_MODEL
    non_recursive_invite_credit: bool = True
    no_fixed_invite_fraction: bool = True
    no_cdl084_explicit_chain_settlement: bool = True

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "batch_id": self.batch_id,
            "cdl_authority": ["CDL-102", "CDL-108"],
            "edge_confidence": _decimal_to_canonical_string(self.edge_confidence),
            "edge_id": self.edge_id(),
            "edge_type": self.edge_type,
            "invite_credit_model": self.invite_credit_model,
            "no_cdl084_explicit_chain_settlement": self.no_cdl084_explicit_chain_settlement,
            "no_fixed_invite_fraction": self.no_fixed_invite_fraction,
            "non_recursive_invite_credit": self.non_recursive_invite_credit,
            "provenance_subtype": self.provenance_subtype,
            "redeemer_agent_id": self.redeemer_agent_id,
            "redemption_epoch": self.redemption_epoch,
            "redemption_nullifier": self.redemption_nullifier,
            "schema_version": self.schema_version,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "inviter_cid": self.inviter_cid,
        }
        reject_float(payload, "invite_provenance_edge_float_not_allowed")
        return payload

    def to_atlas_edge(self) -> dict[str, Any]:
        """Return a safe-writer-compatible Atlas edge row."""

        payload = self.to_dict()
        return {
            "annotation_phase": "phase_1576q",
            "candidate_status": "invite_provenance_edge_wired_phase_1576q",
            "edge_confidence": payload["edge_confidence"],
            "edge_id": payload["edge_id"],
            "edge_type": self.edge_type,
            "invite_credit_model": self.invite_credit_model,
            "metadata": payload,
            "source": self.source_node_id,
            "source_candidate_id": self.source_node_id,
            "src": self.source_node_id,
            "target": self.target_node_id,
            "target_candidate_id": self.target_node_id,
            "tgt": self.target_node_id,
        }

    def to_backward_attribution_edge(self) -> dict[str, Any]:
        """Return the edge shape consumed by BackwardAttributionTraversal."""

        return {
            "edge_confidence": _decimal_to_canonical_string(self.edge_confidence),
            "edge_type": self.edge_type,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
        }

    def canonical_json(self) -> str:
        return canonical_json(
            self.to_dict(),
            float_token="invite_provenance_edge_float_not_allowed",
        )

    def record_hash(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()

    def edge_id(self) -> str:
        digest = hashlib.sha256(
            f"{self.source_node_id}|{self.edge_type}|{self.target_node_id}".encode(
                "utf-8"
            )
        ).hexdigest()[:16]
        return f"edge:{digest}"


def build_invite_provenance_edge_record(
    *,
    source_node_id: str,
    target_node_id: str,
    redemption_nullifier: str,
    batch_id: str,
    inviter_cid: str,
    redeemer_agent_id: str,
    redemption_epoch: int,
    edge_confidence: Decimal | int | str = Decimal("1"),
) -> InviteProvenanceEdgeRecord:
    """Build and validate an invite-init PROVENANCE edge record."""

    record = InviteProvenanceEdgeRecord(
        source_node_id=_require_non_empty_string(
            source_node_id,
            "invite_provenance_source_node_id_required",
        ),
        target_node_id=_require_non_empty_string(
            target_node_id,
            "invite_provenance_target_node_id_required",
        ),
        redemption_nullifier=_require_sha256_hex(
            redemption_nullifier,
            "invite_provenance_redemption_nullifier_invalid",
        ),
        batch_id=_require_non_empty_string(
            batch_id,
            "invite_provenance_batch_id_required",
        ),
        inviter_cid=_require_non_empty_string(
            inviter_cid,
            "invite_provenance_inviter_cid_required",
        ),
        redeemer_agent_id=_require_non_empty_string(
            redeemer_agent_id,
            "invite_provenance_redeemer_agent_id_required",
        ),
        redemption_epoch=_require_non_negative_int(
            redemption_epoch,
            "invite_provenance_redemption_epoch_invalid",
        ),
        edge_confidence=_require_factor(
            edge_confidence,
            "invite_provenance_edge_confidence_invalid",
        ),
    )
    _validate_record(record)
    return record


def build_invite_provenance_edge_from_redemption(
    redemption_record: Mapping[str, Any] | object,
    *,
    source_node_id: str,
    target_node_id: str | None = None,
    edge_confidence: Decimal | int | str = Decimal("1"),
) -> InviteProvenanceEdgeRecord:
    """Build a provenance edge from an InviteRedemptionRecord-like object."""

    payload = _mapping_from_record(redemption_record)
    inviter_cid = _require_non_empty_string(
        payload.get("inviter_cid"),
        "invite_provenance_inviter_cid_required",
    )
    return build_invite_provenance_edge_record(
        source_node_id=source_node_id,
        target_node_id=target_node_id or inviter_cid,
        redemption_nullifier=_require_sha256_hex(
            payload.get("redemption_nullifier"),
            "invite_provenance_redemption_nullifier_invalid",
        ),
        batch_id=_require_non_empty_string(
            payload.get("batch_id"),
            "invite_provenance_batch_id_required",
        ),
        inviter_cid=inviter_cid,
        redeemer_agent_id=_require_non_empty_string(
            payload.get("redeemer_agent_id"),
            "invite_provenance_redeemer_agent_id_required",
        ),
        redemption_epoch=_require_non_negative_int(
            payload.get("redemption_epoch"),
            "invite_provenance_redemption_epoch_invalid",
        ),
        edge_confidence=edge_confidence,
    )


def write_invite_provenance_edge(
    record: InviteProvenanceEdgeRecord,
    atlas_writer: object,
) -> dict[str, Any]:
    """Write an invite provenance edge through an Atlas-compatible writer.

    Supported writer surfaces are deliberately narrow: ``apply_plan`` (safe
    writer style), ``put_edges`` (store style), ``store.put_edges``, ``write_edge``,
    or ``add_edge``. The function returns deterministic telemetry and never
    computes or settles credit.
    """

    _validate_record(record)
    if atlas_writer is None:
        raise InviteProvenanceWiringError("invite_provenance_atlas_writer_required")
    edge = record.to_atlas_edge()
    method = "unknown"
    receipt: object = None

    apply_plan = getattr(atlas_writer, "apply_plan", None)
    if callable(apply_plan):
        method = "apply_plan"
        plan = SimpleNamespace(
            nodes_to_add=[],
            edges_to_add=[edge],
            metadata={"phase": "1576q"},
            phase="1576q",
            dry_run=False,
        )
        receipt = apply_plan(plan)
    else:
        put_edges = getattr(atlas_writer, "put_edges", None)
        if callable(put_edges):
            method = "put_edges"
            receipt = put_edges([edge])
        else:
            store = getattr(atlas_writer, "store", None)
            store_put_edges = getattr(store, "put_edges", None)
            if callable(store_put_edges):
                method = "store.put_edges"
                receipt = store_put_edges([edge])
            else:
                write_edge = getattr(atlas_writer, "write_edge", None)
                if callable(write_edge):
                    method = "write_edge"
                    receipt = write_edge(edge)
                else:
                    add_edge = getattr(atlas_writer, "add_edge", None)
                    if callable(add_edge):
                        method = "add_edge"
                        receipt = add_edge(edge)
                    else:
                        raise InviteProvenanceWiringError(
                            "invite_provenance_atlas_writer_missing_edge_interface"
                        )

    return {
        "edge_id": record.edge_id(),
        "edge_record_hash": record.record_hash(),
        "edge_type": record.edge_type,
        "invite_credit_model": record.invite_credit_model,
        "no_credit_computed": True,
        "no_settlement_activated": True,
        "schema_version": INVITE_PROVENANCE_WIRING_VERSION,
        "write_method": method,
        "writer_receipt": receipt,
    }


def maybe_write_invite_provenance_edge(
    *,
    atlas_writer: object | None,
    source_node_id: str | None,
    target_node_id: str | None,
    redemption_nullifier: str | None,
    batch_id: str | None,
    inviter_cid: str | None,
    redeemer_agent_id: str | None,
    redemption_epoch: int | None,
) -> tuple[str, InviteProvenanceEdgeRecord | None, dict[str, Any] | None]:
    """Best-effort optional hook for invite bootstrap callers."""

    if atlas_writer is None:
        return "not_configured", None, None
    if source_node_id is None:
        return "deferred_redeemer_init_node_required", None, None
    if target_node_id is None and inviter_cid is None:
        return "deferred_inviter_target_node_required", None, None
    if (
        redemption_nullifier is None
        or batch_id is None
        or inviter_cid is None
        or redeemer_agent_id is None
        or redemption_epoch is None
    ):
        return "deferred_invite_redemption_metadata_required", None, None
    record = build_invite_provenance_edge_record(
        source_node_id=source_node_id,
        target_node_id=target_node_id or inviter_cid,
        redemption_nullifier=redemption_nullifier,
        batch_id=batch_id,
        inviter_cid=inviter_cid,
        redeemer_agent_id=redeemer_agent_id,
        redemption_epoch=redemption_epoch,
    )
    receipt = write_invite_provenance_edge(record, atlas_writer)
    return "written", record, receipt


def _mapping_from_record(record: Mapping[str, Any] | object) -> Mapping[str, Any]:
    if isinstance(record, Mapping):
        reject_float(record, "invite_provenance_edge_float_not_allowed")
        return record
    to_dict = getattr(record, "to_dict", None)
    if callable(to_dict):
        payload = to_dict()
        if not isinstance(payload, Mapping):
            raise InviteProvenanceWiringError("invite_provenance_record_mapping_required")
        reject_float(payload, "invite_provenance_edge_float_not_allowed")
        return payload
    raise InviteProvenanceWiringError("invite_provenance_record_mapping_required")


def _validate_record(record: InviteProvenanceEdgeRecord) -> None:
    if record.edge_type != INVITE_PROVENANCE_EDGE_TYPE:
        raise InviteProvenanceWiringError("invite_provenance_edge_type_must_be_provenance")
    if record.provenance_subtype != INVITE_PROVENANCE_SUBTYPE:
        raise InviteProvenanceWiringError("invite_provenance_subtype_invalid")
    if record.invite_credit_model != INVITE_CREDIT_MODEL:
        raise InviteProvenanceWiringError("invite_provenance_credit_model_invalid")
    if record.source_node_id == record.target_node_id:
        raise InviteProvenanceWiringError("invite_provenance_self_edge_rejected")
    if not record.non_recursive_invite_credit:
        raise InviteProvenanceWiringError("invite_provenance_must_be_non_recursive")
    if not record.no_fixed_invite_fraction:
        raise InviteProvenanceWiringError("invite_provenance_fixed_fraction_forbidden")
    if not record.no_cdl084_explicit_chain_settlement:
        raise InviteProvenanceWiringError("invite_provenance_cdl084_settlement_forbidden")


def _require_non_empty_string(value: object, token: str) -> str:
    if type(value) is not str:
        raise InviteProvenanceWiringError(token)
    normalized = value.strip()
    if (
        not normalized
        or normalized != value
        or len(normalized) > MAX_INVITE_PROVENANCE_STRING_CHARS
    ):
        raise InviteProvenanceWiringError(token)
    return normalized


def _require_non_negative_int(value: object, token: str) -> int:
    if type(value) is not int or value < 0:
        raise InviteProvenanceWiringError(token)
    return value


def _require_sha256_hex(value: object, token: str) -> str:
    if (
        type(value) is not str
        or len(value) != SHA256_HEX_CHARS
        or any(char not in "0123456789abcdef" for char in value)
    ):
        raise InviteProvenanceWiringError(token)
    return value


def _require_factor(value: object, token: str) -> Decimal:
    if isinstance(value, bool):
        raise InviteProvenanceWiringError(token)
    if isinstance(value, Decimal):
        number = value
    elif isinstance(value, int):
        number = Decimal(value)
    elif isinstance(value, str):
        try:
            number = Decimal(value)
        except InvalidOperation as exc:
            raise InviteProvenanceWiringError(token) from exc
    else:
        raise InviteProvenanceWiringError(token)
    if not number.is_finite() or number < Decimal("0") or number > Decimal("1"):
        raise InviteProvenanceWiringError(token)
    return number


def _decimal_to_canonical_string(value: Decimal) -> str:
    if not value.is_finite():
        raise InviteProvenanceWiringError("invite_provenance_decimal_not_finite")
    normalized = value.normalize()
    if normalized == normalized.to_integral():
        return str(normalized.quantize(Decimal("1")))
    return format(normalized, "f")


__all__ = [
    "INVITE_CREDIT_MODEL",
    "INVITE_PROVENANCE_EDGE_TYPE",
    "INVITE_PROVENANCE_GO_PHRASE",
    "INVITE_PROVENANCE_NO_ACTIVATION",
    "INVITE_PROVENANCE_OUTPUT_TOKEN",
    "INVITE_PROVENANCE_SUBTYPE",
    "INVITE_PROVENANCE_WIRING_VERSION",
    "InviteProvenanceEdgeRecord",
    "InviteProvenanceWiringError",
    "build_invite_provenance_edge_from_redemption",
    "build_invite_provenance_edge_record",
    "maybe_write_invite_provenance_edge",
    "write_invite_provenance_edge",
]
