# SPDX-License-Identifier: AGPL-3.0-only
"""Monthly issuance maturity gate for nonzero ILC settlement."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ilc_core.epoch.epoch_emission_runtime import ISSUANCE_EPOCH_DURATION, VALIDATION_EPOCH_SECONDS


EPOCH_MATURITY_GATE_VERSION = "epoch_maturity_gate_GAP_EPOCH_MATURITY_GATE_00.v0.1"
MONTHLY_ISSUANCE_MATURITY_PROOF_SCHEMA_VERSION = (
    "monthly_issuance_maturity_proof_GAP_EPOCH_MATURITY_GATE_00.v0.1"
)
MONTHLY_ISSUANCE_MATURITY_PROOF_REQUIRED_TOKEN = (
    "monthly_issuance_maturity_proof_required_GAP_EPOCH_MATURITY_GATE_00"
)
VALIDATION_EPOCH_TRANSITION_NOT_MONTHLY_MATURITY_TOKEN = (
    "validation_epoch_transition_not_monthly_maturity_GAP_EPOCH_MATURITY_GATE_00"
)
MONTHLY_ISSUANCE_MATURITY_PROOF_ACCEPTED_TOKEN = (
    "monthly_issuance_maturity_proof_accepted_GAP_EPOCH_MATURITY_GATE_00"
)
EPOCH_ZERO_NONZERO_SETTLEMENT_NOT_MATURE_TOKEN = (
    "epoch_zero_nonzero_settlement_not_mature_GAP_EPOCH_MATURITY_GATE_00"
)

CDL_027_REF = "CDL-027"
CIDV1_DAG_CBOR_SHA2_256_ROOT_PREFIX_HEX = "01711220"
_MIN_MONTHLY_ISSUANCE_SECONDS = 28 * 24 * 60 * 60
if _MIN_MONTHLY_ISSUANCE_SECONDS % VALIDATION_EPOCH_SECONDS != 0:
    raise RuntimeError("monthly_maturity_validation_epoch_span_non_integral")
MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN = (
    _MIN_MONTHLY_ISSUANCE_SECONDS // VALIDATION_EPOCH_SECONDS
)
MAX_MATURITY_REF_BYTES = 512
_PROOF_CONSTRUCTOR_KEYS = frozenset(
    {
        "matured_issuance_epoch",
        "distribution_issuance_epoch",
        "source_settlement_root_hex",
        "opening_validation_epoch",
        "closing_validation_epoch",
        "validator_quorum_certificate_ref",
        "evidence_ref",
        "schema_version",
        "maturity_status",
        "cdl_ref",
        "issuance_epoch_duration",
        "maturity_evidence_kind",
    }
)


@dataclass(frozen=True, kw_only=True)
class MonthlyIssuanceMaturityProof:
    """Structural proof that a monthly issuance epoch closed.

    The gate intentionally validates sequence/evidence fields and never asks
    local wall-clock time whether an epoch is mature.
    """

    matured_issuance_epoch: int
    distribution_issuance_epoch: int
    source_settlement_root_hex: str
    opening_validation_epoch: int
    closing_validation_epoch: int
    validator_quorum_certificate_ref: str
    evidence_ref: str
    schema_version: str = MONTHLY_ISSUANCE_MATURITY_PROOF_SCHEMA_VERSION
    maturity_status: str = "matured"
    cdl_ref: str = CDL_027_REF
    issuance_epoch_duration: str = ISSUANCE_EPOCH_DURATION
    maturity_evidence_kind: str = "validator_monthly_issuance_close"

    def __post_init__(self) -> None:
        _require_exact_str(
            self.schema_version,
            MONTHLY_ISSUANCE_MATURITY_PROOF_SCHEMA_VERSION,
            "monthly_maturity_proof_schema_version_invalid",
        )
        _require_exact_str(
            self.maturity_status,
            "matured",
            "monthly_maturity_proof_status_invalid",
        )
        _require_exact_str(self.cdl_ref, CDL_027_REF, "monthly_maturity_proof_cdl_ref_invalid")
        _require_exact_str(
            self.issuance_epoch_duration,
            ISSUANCE_EPOCH_DURATION,
            "monthly_maturity_proof_duration_invalid",
        )
        _require_exact_str(
            self.maturity_evidence_kind,
            "validator_monthly_issuance_close",
            "monthly_maturity_proof_evidence_kind_invalid",
        )
        _require_non_negative_int(
            self.matured_issuance_epoch,
            "monthly_maturity_proof_matured_epoch_invalid",
        )
        _require_non_negative_int(
            self.distribution_issuance_epoch,
            "monthly_maturity_proof_distribution_epoch_invalid",
        )
        _require_root_hex(self.source_settlement_root_hex)
        opening = _require_non_negative_int(
            self.opening_validation_epoch,
            "monthly_maturity_proof_opening_validation_epoch_invalid",
        )
        closing = _require_non_negative_int(
            self.closing_validation_epoch,
            "monthly_maturity_proof_closing_validation_epoch_invalid",
        )
        if closing <= opening:
            raise ValueError("monthly_maturity_proof_validation_epoch_order_invalid")
        if closing - opening < MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN:
            raise ValueError(VALIDATION_EPOCH_TRANSITION_NOT_MONTHLY_MATURITY_TOKEN)
        _require_non_empty_ref(
            self.validator_quorum_certificate_ref,
            "monthly_maturity_proof_quorum_ref_required",
        )
        _require_non_empty_ref(self.evidence_ref, "monthly_maturity_proof_evidence_ref_required")

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "cdl_ref": self.cdl_ref,
            "closing_validation_epoch": self.closing_validation_epoch,
            "distribution_issuance_epoch": self.distribution_issuance_epoch,
            "evidence_ref": self.evidence_ref,
            "gate_version": EPOCH_MATURITY_GATE_VERSION,
            "issuance_epoch_duration": self.issuance_epoch_duration,
            "matured_issuance_epoch": self.matured_issuance_epoch,
            "maturity_evidence_kind": self.maturity_evidence_kind,
            "maturity_status": self.maturity_status,
            "opening_validation_epoch": self.opening_validation_epoch,
            "schema_version": self.schema_version,
            "source_settlement_root_hex": self.source_settlement_root_hex,
            "validator_quorum_certificate_ref": self.validator_quorum_certificate_ref,
        }


def require_monthly_issuance_maturity_proof(
    proof: MonthlyIssuanceMaturityProof | Mapping[str, Any] | None,
    *,
    distribution_issuance_epoch: int,
    source_settlement_root_hex: str,
) -> MonthlyIssuanceMaturityProof:
    """Return a validated proof or raise a stable fail-closed token."""
    if proof is None:
        raise ValueError(MONTHLY_ISSUANCE_MATURITY_PROOF_REQUIRED_TOKEN)
    normalized = _coerce_maturity_proof(proof)
    expected_distribution_epoch = _require_non_negative_int(
        distribution_issuance_epoch,
        "distribution_issuance_epoch_invalid",
    )
    if expected_distribution_epoch == 0:
        raise ValueError("monthly_maturity_proof_not_defined_for_epoch_zero")
    expected_root = _require_root_hex(source_settlement_root_hex)
    if normalized.distribution_issuance_epoch != expected_distribution_epoch:
        raise ValueError("monthly_maturity_proof_distribution_epoch_mismatch")
    expected_matured_epoch = expected_distribution_epoch - 1
    if normalized.matured_issuance_epoch != expected_matured_epoch:
        raise ValueError("monthly_maturity_proof_matured_epoch_mismatch")
    if normalized.source_settlement_root_hex != expected_root:
        raise ValueError("monthly_maturity_proof_source_settlement_root_mismatch")
    return normalized


def _coerce_maturity_proof(
    proof: MonthlyIssuanceMaturityProof | Mapping[str, Any],
) -> MonthlyIssuanceMaturityProof:
    """Coerce proof mappings while preserving field-level validation tokens."""
    if isinstance(proof, MonthlyIssuanceMaturityProof):
        return proof
    if not isinstance(proof, Mapping):
        raise ValueError("monthly_maturity_proof_required")
    record = dict(proof)
    gate_version = record.pop("gate_version", EPOCH_MATURITY_GATE_VERSION)
    _require_exact_str(
        gate_version,
        EPOCH_MATURITY_GATE_VERSION,
        "monthly_maturity_proof_gate_version_invalid",
    )
    extra_keys = set(record) - _PROOF_CONSTRUCTOR_KEYS
    missing_keys = {
        "matured_issuance_epoch",
        "distribution_issuance_epoch",
        "source_settlement_root_hex",
        "opening_validation_epoch",
        "closing_validation_epoch",
        "validator_quorum_certificate_ref",
        "evidence_ref",
    } - set(record)
    if extra_keys or missing_keys:
        raise ValueError("monthly_maturity_proof_fields_invalid")
    try:
        return MonthlyIssuanceMaturityProof(**record)
    except TypeError as exc:
        raise ValueError("monthly_maturity_proof_fields_invalid") from exc


def _require_exact_str(value: object, expected: str, token: str) -> str:
    if not isinstance(value, str) or value != expected:
        raise ValueError(token)
    return value


def _require_non_negative_int(value: object, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(token)
    return value


def _require_root_hex(value: object) -> str:
    if not isinstance(value, str) or any(char not in "0123456789abcdef" for char in value):
        raise ValueError("monthly_maturity_proof_source_settlement_root_invalid")
    if len(value) == 64:
        return value
    if len(value) == 72 and value.startswith(CIDV1_DAG_CBOR_SHA2_256_ROOT_PREFIX_HEX):
        return value
    raise ValueError("monthly_maturity_proof_source_settlement_root_invalid")


def _require_non_empty_ref(value: object, token: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(token)
    if len(value.encode("utf-8")) > MAX_MATURITY_REF_BYTES:
        raise ValueError(f"{token}_exceeds_max_bytes")
    return value


__all__ = [
    "CDL_027_REF",
    "EPOCH_MATURITY_GATE_VERSION",
    "EPOCH_ZERO_NONZERO_SETTLEMENT_NOT_MATURE_TOKEN",
    "MAX_MATURITY_REF_BYTES",
    "MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN",
    "MONTHLY_ISSUANCE_MATURITY_PROOF_ACCEPTED_TOKEN",
    "MONTHLY_ISSUANCE_MATURITY_PROOF_REQUIRED_TOKEN",
    "MONTHLY_ISSUANCE_MATURITY_PROOF_SCHEMA_VERSION",
    "MonthlyIssuanceMaturityProof",
    "VALIDATION_EPOCH_TRANSITION_NOT_MONTHLY_MATURITY_TOKEN",
    "require_monthly_issuance_maturity_proof",
]
