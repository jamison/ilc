# SPDX-License-Identifier: AGPL-3.0-only
"""Model Router local receipt schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ilc_core.sidecars.execution_receipt import (
    SIDECAR_EXECUTION_RECEIPT_SCHEMA_VERSION,
    SidecarExecutionReceipt,
    SidecarExecutionReceiptError,
)

from .adapter import MAX_ROUTER_TEXT_CHARS

MODEL_ROUTER_COMPANION_SCHEMA_VERSION = "ilc_model_router_companion_meta_phase_1610.v0.1"
MODEL_ROUTER_PACKAGE_NAME = "ilc-model-router"
MODEL_ROUTER_TOOL_ID = "ilc-model-router-v1"
CONSENT_STATUSES = frozenset({"local_only", "promoted", "promotion_pending"})
CAPABILITY_CLASSES = frozenset({"embedding", "inference", "multimodal", None})
_HEX = frozenset("0123456789abcdef")


class RouterReceiptError(ValueError):
    """Stable Model Router receipt validation error."""


@dataclass(frozen=True)
class RouterCompanionRecord:
    """Router-specific metadata stored outside the core sidecar receipt."""

    receipt_token: str
    model_id: str
    provider: str
    token_counts_input: int
    token_counts_output: int
    capability_class: str | None = None
    consent_status: str = "local_only"
    schema_version: str = MODEL_ROUTER_COMPANION_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _require_exact(
            self.schema_version,
            MODEL_ROUTER_COMPANION_SCHEMA_VERSION,
            "model_router_companion_schema_version_invalid",
        )
        _require_hex(self.receipt_token, "model_router_companion_receipt_token_invalid", length=64)
        _require_text(self.model_id, "model_router_model_id_invalid")
        _require_text(self.provider, "model_router_provider_invalid")
        _require_non_negative_int(
            self.token_counts_input,
            "model_router_token_counts_input_invalid",
        )
        _require_non_negative_int(
            self.token_counts_output,
            "model_router_token_counts_output_invalid",
        )
        if self.capability_class not in CAPABILITY_CLASSES:
            raise RouterReceiptError("model_router_capability_class_invalid")
        if self.consent_status not in CONSENT_STATUSES:
            raise RouterReceiptError("model_router_consent_status_invalid")

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_class": self.capability_class,
            "consent_status": self.consent_status,
            "model_id": self.model_id,
            "provider": self.provider,
            "receipt_token": self.receipt_token,
            "schema_version": self.schema_version,
            "token_counts_input": self.token_counts_input,
            "token_counts_output": self.token_counts_output,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "RouterCompanionRecord":
        if not isinstance(payload, Mapping):
            raise RouterReceiptError("model_router_companion_payload_invalid")
        expected = {
            "capability_class",
            "consent_status",
            "model_id",
            "provider",
            "receipt_token",
            "schema_version",
            "token_counts_input",
            "token_counts_output",
        }
        if set(payload) != expected:
            raise RouterReceiptError("model_router_companion_field_set_invalid")
        return cls(
            receipt_token=_required_str(payload, "receipt_token"),
            model_id=_required_str(payload, "model_id"),
            provider=_required_str(payload, "provider"),
            token_counts_input=_required_int(payload, "token_counts_input"),
            token_counts_output=_required_int(payload, "token_counts_output"),
            capability_class=payload.get("capability_class"),
            consent_status=_required_str(payload, "consent_status"),
            schema_version=_required_str(payload, "schema_version"),
        )


@dataclass(frozen=True)
class RouterReceipt:
    """Full router receipt: core HARNESS-SIDECAR-05 fields plus companion."""

    action_type: str
    agent_id_hex: str
    epoch: int
    error_token: str
    inputs_hash: str
    outputs_hash: str
    receipt_token: str
    schema_version: str
    status: str
    tool_id: str
    companion: RouterCompanionRecord

    def __post_init__(self) -> None:
        if self.action_type != "model_inference":
            raise RouterReceiptError("router_receipt_action_type_must_be_model_inference")
        _require_exact(
            self.schema_version,
            SIDECAR_EXECUTION_RECEIPT_SCHEMA_VERSION,
            "router_receipt_core_schema_version_invalid",
        )
        try:
            core = self.to_core_receipt()
        except SidecarExecutionReceiptError as exc:
            raise RouterReceiptError(str(exc)) from exc
        if core.receipt_token != self.receipt_token:
            raise RouterReceiptError("router_receipt_token_mismatch")
        if self.companion.receipt_token != self.receipt_token:
            raise RouterReceiptError("router_receipt_companion_token_mismatch")

    def to_core_receipt(self) -> SidecarExecutionReceipt:
        return SidecarExecutionReceipt(
            tool_id=self.tool_id,
            action_type=self.action_type,
            epoch=self.epoch,
            agent_id_hex=self.agent_id_hex,
            inputs_hash=self.inputs_hash,
            outputs_hash=self.outputs_hash,
            status=self.status,
            error_token=self.error_token,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_type": self.action_type,
            "agent_id_hex": self.agent_id_hex,
            "companion": self.companion.to_dict(),
            "epoch": self.epoch,
            "error_token": self.error_token,
            "inputs_hash": self.inputs_hash,
            "outputs_hash": self.outputs_hash,
            "receipt_token": self.receipt_token,
            "schema_version": self.schema_version,
            "status": self.status,
            "tool_id": self.tool_id,
        }

    @classmethod
    def from_core_and_companion(
        cls,
        core: SidecarExecutionReceipt,
        companion: RouterCompanionRecord,
    ) -> "RouterReceipt":
        return cls(
            action_type=core.action_type,
            agent_id_hex=core.agent_id_hex,
            epoch=core.epoch,
            error_token=core.error_token,
            inputs_hash=core.inputs_hash,
            outputs_hash=core.outputs_hash,
            receipt_token=core.receipt_token,
            schema_version=SIDECAR_EXECUTION_RECEIPT_SCHEMA_VERSION,
            status=core.status,
            tool_id=core.tool_id,
            companion=companion,
        )


def build_router_receipt(
    *,
    agent_id_hex: str,
    epoch: int,
    inputs_hash: str,
    outputs_hash: str,
    status: str,
    companion: RouterCompanionRecord,
    error_token: str = "",
    tool_id: str = MODEL_ROUTER_TOOL_ID,
) -> RouterReceipt:
    """Build a RouterReceipt from core fields and an already-tokenized companion."""

    core = SidecarExecutionReceipt(
        tool_id=tool_id,
        action_type="model_inference",
        epoch=epoch,
        agent_id_hex=agent_id_hex,
        inputs_hash=inputs_hash,
        outputs_hash=outputs_hash,
        status=status,
        error_token=error_token,
    )
    return RouterReceipt.from_core_and_companion(core, companion)


def _require_exact(value: Any, expected: str, token: str) -> str:
    if value != expected:
        raise RouterReceiptError(token)
    return expected


def _require_text(value: Any, token: str) -> str:
    if type(value) is not str or not value or len(value) > MAX_ROUTER_TEXT_CHARS:
        raise RouterReceiptError(token)
    return value


def _require_non_negative_int(value: Any, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise RouterReceiptError(token)
    return value


def _require_hex(value: Any, token: str, *, length: int) -> str:
    if type(value) is not str or len(value) != length:
        raise RouterReceiptError(token)
    if value.lower() != value or any(char not in _HEX for char in value):
        raise RouterReceiptError(token)
    return value


def _required_str(payload: Mapping[str, Any], field_name: str) -> str:
    value = payload.get(field_name)
    if type(value) is not str:
        raise RouterReceiptError(f"model_router_{field_name}_invalid")
    return value


def _required_int(payload: Mapping[str, Any], field_name: str) -> int:
    value = payload.get(field_name)
    if isinstance(value, bool) or not isinstance(value, int):
        raise RouterReceiptError(f"model_router_{field_name}_invalid")
    return value


__all__ = [
    "CAPABILITY_CLASSES",
    "CONSENT_STATUSES",
    "MAX_ROUTER_TEXT_CHARS",
    "MODEL_ROUTER_COMPANION_SCHEMA_VERSION",
    "MODEL_ROUTER_PACKAGE_NAME",
    "MODEL_ROUTER_TOOL_ID",
    "RouterCompanionRecord",
    "RouterReceipt",
    "RouterReceiptError",
    "build_router_receipt",
]
