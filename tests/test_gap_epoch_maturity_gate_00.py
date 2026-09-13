from __future__ import annotations

from decimal import Decimal

import pytest

from ilc_core.epoch.epoch_distribution_writer import (
    EpochDistributionInput,
    commit_epoch_distribution,
    compute_epoch_distribution,
)
from ilc_core.epoch.epoch_maturity_gate import (
    EPOCH_MATURITY_GATE_VERSION,
    MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
    MONTHLY_ISSUANCE_MATURITY_PROOF_REQUIRED_TOKEN,
    MONTHLY_ISSUANCE_MATURITY_PROOF_SCHEMA_VERSION,
    VALIDATION_EPOCH_TRANSITION_NOT_MONTHLY_MATURITY_TOKEN,
    MonthlyIssuanceMaturityProof,
)


ROOT_HEX = "d" * 64
CIDV1_ROOT_HEX = "01711220" + "d" * 64


class RecordingBatchLifecycle:
    ilc_atomic_epoch_batch_writer = True

    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def commit_settled_epoch_batch(
        self,
        *,
        settlements: dict[str, Decimal],
        epoch_id: str,
    ) -> list[dict[str, object]]:
        self.calls.append({"settlements": settlements, "epoch_id": epoch_id})
        return [{"ok": True, "token": "recorded", "data": {}}]


def _input(
    *,
    issuance_epoch: int = 1,
    total_epoch_fees_ilc: Decimal = Decimal("0"),
    proof: MonthlyIssuanceMaturityProof | None = None,
    source_settlement_root_hex: str = ROOT_HEX,
) -> EpochDistributionInput:
    return EpochDistributionInput(
        issuance_epoch=issuance_epoch,
        total_epoch_fees_ilc=total_epoch_fees_ilc,
        genesis_cumulative_accrual_ilc=Decimal("0"),
        eligible_agents={"agent:a": Decimal("1")},
        prior_carry_forward_records=[],
        source_settlement_root_hex=source_settlement_root_hex,
        allow_default_source_settlement_root=False,
        monthly_maturity_proof=proof,
    )


def _proof(
    *,
    distribution_issuance_epoch: int = 1,
    source_settlement_root_hex: str = ROOT_HEX,
    opening_validation_epoch: int = 0,
    closing_validation_epoch: int = MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
) -> MonthlyIssuanceMaturityProof:
    return MonthlyIssuanceMaturityProof(
        matured_issuance_epoch=distribution_issuance_epoch - 1,
        distribution_issuance_epoch=distribution_issuance_epoch,
        source_settlement_root_hex=source_settlement_root_hex,
        opening_validation_epoch=opening_validation_epoch,
        closing_validation_epoch=closing_validation_epoch,
        validator_quorum_certificate_ref=f"validator_quorum_sha256:{'a' * 64}",
        evidence_ref=f"monthly_close_evidence_sha256:{'b' * 64}",
    )


def test_maturity_gate_exports_version_and_schema() -> None:
    assert EPOCH_MATURITY_GATE_VERSION == "epoch_maturity_gate_GAP_EPOCH_MATURITY_GATE_00.v0.1"
    assert (
        MONTHLY_ISSUANCE_MATURITY_PROOF_SCHEMA_VERSION
        == "monthly_issuance_maturity_proof_GAP_EPOCH_MATURITY_GATE_00.v0.1"
    )


def test_epoch_one_nonzero_emission_requires_monthly_maturity_proof() -> None:
    with pytest.raises(ValueError, match=MONTHLY_ISSUANCE_MATURITY_PROOF_REQUIRED_TOKEN):
        compute_epoch_distribution(_input(proof=None))


def test_validation_epoch_zero_to_one_is_not_monthly_maturity() -> None:
    with pytest.raises(ValueError, match=VALIDATION_EPOCH_TRANSITION_NOT_MONTHLY_MATURITY_TOKEN):
        _proof(closing_validation_epoch=1)


def test_matured_monthly_proof_allows_epoch_one_distribution() -> None:
    output = compute_epoch_distribution(_input(proof=_proof()))

    assert output.issuance_epoch == 1
    assert output.monthly_maturity_proof is not None
    assert output.monthly_maturity_proof.matured_issuance_epoch == 0
    assert output.conservation_record.current_emission_ilc > Decimal("0")


def test_matured_monthly_proof_accepts_cidv1_source_root() -> None:
    output = compute_epoch_distribution(
        _input(
            source_settlement_root_hex=CIDV1_ROOT_HEX,
            proof=_proof(source_settlement_root_hex=CIDV1_ROOT_HEX),
        )
    )

    assert output.source_settlement_root_hex == CIDV1_ROOT_HEX
    assert output.monthly_maturity_proof is not None
    assert output.monthly_maturity_proof.source_settlement_root_hex == CIDV1_ROOT_HEX


def test_wrong_distribution_epoch_proof_rejected() -> None:
    with pytest.raises(ValueError, match="monthly_maturity_proof_distribution_epoch_mismatch"):
        compute_epoch_distribution(
            _input(
                issuance_epoch=2,
                proof=_proof(distribution_issuance_epoch=1),
            )
        )


def test_wrong_source_root_proof_rejected() -> None:
    with pytest.raises(ValueError, match="monthly_maturity_proof_source_settlement_root_mismatch"):
        compute_epoch_distribution(_input(proof=_proof(source_settlement_root_hex="e" * 64)))


def test_malformed_proof_mapping_rejected() -> None:
    bad_proof = _proof().to_canonical_record()
    bad_proof["maturity_status"] = "validation_epoch_closed"

    with pytest.raises(ValueError, match="monthly_maturity_proof_status_invalid"):
        compute_epoch_distribution(_input(proof=bad_proof))


def test_commit_epoch_one_nonzero_settlement_without_proof_writes_nothing() -> None:
    lifecycle = RecordingBatchLifecycle()

    with pytest.raises(ValueError, match=MONTHLY_ISSUANCE_MATURITY_PROOF_REQUIRED_TOKEN):
        commit_epoch_distribution(_input(proof=None), lifecycle)

    assert lifecycle.calls == []


def test_commit_epoch_one_with_maturity_proof_writes_after_gate() -> None:
    lifecycle = RecordingBatchLifecycle()

    output = commit_epoch_distribution(_input(proof=_proof()), lifecycle)

    assert output.issuance_epoch == 1
    assert len(lifecycle.calls) == 1
    assert lifecycle.calls[0]["epoch_id"] == "0000000001"


def test_zero_epoch_zero_value_bookkeeping_needs_no_maturity_proof() -> None:
    lifecycle = RecordingBatchLifecycle()

    output = commit_epoch_distribution(
        EpochDistributionInput(
            issuance_epoch=0,
            total_epoch_fees_ilc=Decimal("0"),
            genesis_cumulative_accrual_ilc=Decimal("0"),
            eligible_agents={},
            prior_carry_forward_records=[],
            source_settlement_root_hex=ROOT_HEX,
            allow_default_source_settlement_root=False,
        ),
        lifecycle,
    )

    assert output.issuance_epoch == 0
    assert output.conservation_record.total_debit_ilc == Decimal("0")
    assert lifecycle.calls == []


def test_epoch_zero_explicit_maturity_proof_is_rejected() -> None:
    with pytest.raises(ValueError, match="monthly_maturity_proof_not_defined_for_epoch_zero"):
        compute_epoch_distribution(
            EpochDistributionInput(
                issuance_epoch=0,
                total_epoch_fees_ilc=Decimal("0"),
                genesis_cumulative_accrual_ilc=Decimal("0"),
                eligible_agents={},
                prior_carry_forward_records=[],
                source_settlement_root_hex=ROOT_HEX,
                allow_default_source_settlement_root=False,
                monthly_maturity_proof=_proof(),
            )
        )
