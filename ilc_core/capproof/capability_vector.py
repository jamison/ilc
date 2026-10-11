# SPDX-License-Identifier: AGPL-3.0-only
"""Capability-vector schema for CDL-115 CapProof v1."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping

_AGENT_ID_RE = re.compile(r"^[0-9a-f]{96}$")
CAPPROOF_MAX_METRIC_VALUE = Decimal("1E+18")


class CapProofValidationError(ValueError):
    """Validation error with a stable token for CapProof callers and tests."""

    def __init__(self, token: str, message: str = "") -> None:
        super().__init__(message or token)
        self.token = token


@dataclass(frozen=True)
class CapabilityVector:
    """Signed-output-ready CapProof v1 capability vector."""

    gemm_gops: Decimal
    infer_tps: Decimal
    bw_gbps: Decimal
    graph_mteps: Decimal
    det_pass: bool
    epoch: int
    agent_id: str

    def __post_init__(self) -> None:
        _require_decimal_metric(self.gemm_gops, "gemm_gops")
        _require_decimal_metric(self.infer_tps, "infer_tps")
        _require_decimal_metric(self.bw_gbps, "bw_gbps")
        _require_decimal_metric(self.graph_mteps, "graph_mteps")
        if type(self.det_pass) is not bool:
            raise CapProofValidationError(
                "capproof_det_pass_must_be_bool",
                "det_pass must be bool, not a truthy or numeric stand-in",
            )
        if not isinstance(self.epoch, int) or type(self.epoch) is bool or self.epoch < 0:
            raise CapProofValidationError(
                "capproof_epoch_must_be_nonnegative_int",
                "epoch must be a non-negative integer",
            )
        if not isinstance(self.agent_id, str) or _AGENT_ID_RE.fullmatch(self.agent_id) is None:
            raise CapProofValidationError(
                "capproof_agent_id_must_be_96_lower_hex",
                "agent_id must be 96 lowercase hex characters",
            )

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic JSON-ready mapping without numeric coercion."""

        return {
            "agent_id": self.agent_id,
            "bw_gbps": _decimal_text(self.bw_gbps),
            "det_pass": self.det_pass,
            "epoch": self.epoch,
            "gemm_gops": _decimal_text(self.gemm_gops),
            "graph_mteps": _decimal_text(self.graph_mteps),
            "infer_tps": _decimal_text(self.infer_tps),
        }

    def to_json(self) -> str:
        """Serialize deterministically for later signing and content addressing."""

        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "CapabilityVector":
        """Load a capability vector from the canonical JSON-ready mapping."""

        if not isinstance(payload, Mapping):
            raise CapProofValidationError("capproof_capability_vector_payload_invalid")
        expected = {
            "agent_id",
            "bw_gbps",
            "det_pass",
            "epoch",
            "gemm_gops",
            "graph_mteps",
            "infer_tps",
        }
        if set(payload) != expected:
            raise CapProofValidationError("capproof_capability_vector_field_set_invalid")
        return cls(
            gemm_gops=_decimal_from_text(payload.get("gemm_gops"), "gemm_gops"),
            infer_tps=_decimal_from_text(payload.get("infer_tps"), "infer_tps"),
            bw_gbps=_decimal_from_text(payload.get("bw_gbps"), "bw_gbps"),
            graph_mteps=_decimal_from_text(payload.get("graph_mteps"), "graph_mteps"),
            det_pass=_required_bool(payload.get("det_pass")),
            epoch=_required_epoch(payload.get("epoch")),
            agent_id=_required_agent_id(payload.get("agent_id")),
        )

    @classmethod
    def from_json(cls, payload: str) -> "CapabilityVector":
        """Deserialize a deterministic JSON capability vector."""

        if type(payload) is not str:
            raise CapProofValidationError("capproof_capability_vector_json_invalid")
        try:
            decoded = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise CapProofValidationError("capproof_capability_vector_json_invalid") from exc
        return cls.from_dict(decoded)


def _require_decimal_metric(value: Decimal, field_name: str) -> None:
    if not isinstance(value, Decimal):
        raise CapProofValidationError(
            f"capproof_{field_name}_must_be_decimal",
            f"{field_name} must be Decimal",
        )
    if not value.is_finite():
        raise CapProofValidationError(
            f"capproof_{field_name}_must_be_finite",
            f"{field_name} must be finite",
        )
    if value < Decimal("0"):
        raise CapProofValidationError(
            f"capproof_{field_name}_must_be_nonnegative",
            f"{field_name} must be non-negative",
        )
    if value > CAPPROOF_MAX_METRIC_VALUE:
        raise CapProofValidationError(
            f"capproof_{field_name}_exceeds_maximum",
            f"{field_name} exceeds maximum CapProof metric value",
        )


def _decimal_text(value: Decimal) -> str:
    return format(value, "f")


def _decimal_from_text(value: Any, field_name: str) -> Decimal:
    if type(value) is not str or not value or value != value.strip():
        raise CapProofValidationError(f"capproof_{field_name}_must_be_decimal_string")
    try:
        parsed = Decimal(value)
    except Exception as exc:
        raise CapProofValidationError(f"capproof_{field_name}_must_be_decimal_string") from exc
    if _decimal_text(parsed) != value:
        raise CapProofValidationError(f"capproof_{field_name}_must_be_canonical_decimal_string")
    return parsed


def _required_bool(value: Any) -> bool:
    if type(value) is not bool:
        raise CapProofValidationError("capproof_det_pass_must_be_bool")
    return value


def _required_epoch(value: Any) -> int:
    if not isinstance(value, int) or type(value) is bool or value < 0:
        raise CapProofValidationError("capproof_epoch_must_be_nonnegative_int")
    return value


def _required_agent_id(value: Any) -> str:
    if not isinstance(value, str) or _AGENT_ID_RE.fullmatch(value) is None:
        raise CapProofValidationError("capproof_agent_id_must_be_96_lower_hex")
    return value
