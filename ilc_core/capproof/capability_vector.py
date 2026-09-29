# SPDX-License-Identifier: AGPL-3.0-only
"""Capability-vector schema for CDL-115 CapProof v1."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

_AGENT_ID_RE = re.compile(r"^[0-9a-f]{96}$")


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


def _decimal_text(value: Decimal) -> str:
    return format(value, "f")
