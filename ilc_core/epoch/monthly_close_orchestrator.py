# SPDX-License-Identifier: AGPL-3.0-only
"""Local monthly issuance close orchestration helpers."""

from __future__ import annotations

import hashlib
from decimal import Decimal
from typing import Any, Mapping

from ilc_core.epoch.ecu_accrual_evidence import EcuAccrualEvidence
from ilc_core.epoch.epoch_distribution_writer import (
    EpochDistributionInput,
    EpochDistributionOutput,
    compute_epoch_distribution,
)
from ilc_core.epoch.epoch_maturity_gate import (
    MonthlyIssuanceMaturityProof,
    require_monthly_issuance_maturity_proof,
)


MONTHLY_CLOSE_ORCHESTRATOR_VERSION = (
    "monthly_close_orchestrator_GAP_MONTHLY_ISSUANCE_CLOSE_ORCHESTRATOR_00a.v0.1"
)
MAX_EPOCH_RECORD_AGG_SIG_BYTES = 4_096


def build_monthly_close_proof_from_epoch_record(
    epoch_record: object,
    *,
    matured_issuance_epoch: int,
    distribution_issuance_epoch: int,
    opening_validation_epoch: int,
    closing_validation_epoch: int,
    evidence_ref: str,
) -> MonthlyIssuanceMaturityProof:
    """Build a monthly maturity proof from an injected consensus epoch record."""
    _require_epoch_record_found(epoch_record)
    root_bytes = _require_state_root_bytes(epoch_record)
    proof = MonthlyIssuanceMaturityProof(
        matured_issuance_epoch=matured_issuance_epoch,
        distribution_issuance_epoch=distribution_issuance_epoch,
        source_settlement_root_hex=root_bytes.hex(),
        opening_validation_epoch=opening_validation_epoch,
        closing_validation_epoch=closing_validation_epoch,
        validator_quorum_certificate_ref=_quorum_certificate_ref(epoch_record),
        evidence_ref=evidence_ref,
    )
    return require_monthly_issuance_maturity_proof(
        proof,
        distribution_issuance_epoch=distribution_issuance_epoch,
        source_settlement_root_hex=root_bytes.hex(),
    )


def build_settlement_input_from_ecu_accrual(
    ecu_accrual_evidence: EcuAccrualEvidence,
    *,
    distribution_issuance_epoch: int,
    proof: MonthlyIssuanceMaturityProof,
    total_epoch_fees_ilc: Decimal | int | str,
    genesis_cumulative_accrual_ilc: Decimal | int | str,
    prior_carry_forward_records: tuple[Any, ...] = (),
    cumulative_issued_before_epoch_ilc: Decimal | int | str = "0",
    eligible_auditor_agents: Mapping[str, Decimal | int | str] | None = None,
) -> EpochDistributionInput:
    """Turn validated ECU accrual evidence into an epoch distribution input."""
    if not isinstance(ecu_accrual_evidence, EcuAccrualEvidence):
        raise ValueError("ecu_accrual_evidence_required")
    if not isinstance(proof, MonthlyIssuanceMaturityProof):
        raise ValueError("monthly_maturity_proof_required")
    return EpochDistributionInput(
        issuance_epoch=distribution_issuance_epoch,
        total_epoch_fees_ilc=total_epoch_fees_ilc,
        genesis_cumulative_accrual_ilc=genesis_cumulative_accrual_ilc,
        eligible_agents=ecu_accrual_evidence.agent_ecu_weights,
        prior_carry_forward_records=prior_carry_forward_records,
        cumulative_issued_before_epoch_ilc=cumulative_issued_before_epoch_ilc,
        eligible_auditor_agents=eligible_auditor_agents,
        source_settlement_root_hex=proof.source_settlement_root_hex,
        allow_default_source_settlement_root=False,
        monthly_maturity_proof=proof,
    )


def verify_close_dry_run(distribution_input: EpochDistributionInput) -> EpochDistributionOutput:
    """Compute and verify a distribution without committing wallet state."""
    output = compute_epoch_distribution(distribution_input)
    if output.conservation_verified is not True:
        raise ValueError("monthly_close_dry_run_conservation_not_verified")
    if output.conservation_record.difference_ilc != Decimal("0"):
        raise ValueError("monthly_close_dry_run_conservation_difference_nonzero")
    return output


def _require_state_root_bytes(epoch_record: object) -> bytes:
    root = getattr(epoch_record, "state_root", None)
    if not isinstance(root, bytes):
        raise ValueError("epoch_record_state_root_bytes_required")
    if len(root) == 32:
        return root
    if len(root) == 36 and root.hex().startswith("01711220"):
        return root
    raise ValueError("epoch_record_state_root_length_invalid")


def _require_epoch_record_found(epoch_record: object) -> None:
    if getattr(epoch_record, "found", None) is not True:
        raise ValueError("epoch_record_not_found")


def _quorum_certificate_ref(epoch_record: object) -> str:
    agg_sig = getattr(epoch_record, "agg_sig", None)
    if not isinstance(agg_sig, bytes) or not agg_sig:
        raise ValueError("epoch_record_agg_sig_bytes_required")
    if len(agg_sig) > MAX_EPOCH_RECORD_AGG_SIG_BYTES:
        raise ValueError("epoch_record_agg_sig_exceeds_max_bytes")
    return f"epoch_record_agg_sig_sha256:{hashlib.sha256(agg_sig).hexdigest()}"


__all__ = [
    "MAX_EPOCH_RECORD_AGG_SIG_BYTES",
    "MONTHLY_CLOSE_ORCHESTRATOR_VERSION",
    "build_monthly_close_proof_from_epoch_record",
    "build_settlement_input_from_ecu_accrual",
    "verify_close_dry_run",
]
