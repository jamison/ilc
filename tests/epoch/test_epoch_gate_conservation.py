from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest

import ilc_core.epoch as epoch
from ilc_core.epoch.epoch_conservation_gate import (
    EPOCH_0_TO_1_CONSERVATION_ENFORCED_TOKEN,
    EPOCH_CONSERVATION_GATE_VERSION,
    EPOCH_GATE_CONSERVATION_CHECK_ADDED_TOKEN,
    NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN,
    verify_epoch_conservation_before_commit,
)
from ilc_core.epoch.epoch_distribution_writer import (
    EpochDistributionInput,
    compute_epoch_distribution,
)
from ilc_core.epoch.epoch_maturity_gate import (
    MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
    MonthlyIssuanceMaturityProof,
)


ROOT_HEX = "c" * 64
AGENT_ID = "a" * 96


def _output(issuance_epoch: int = 1):
    proof = None
    if issuance_epoch > 0:
        proof = MonthlyIssuanceMaturityProof(
            matured_issuance_epoch=issuance_epoch - 1,
            distribution_issuance_epoch=issuance_epoch,
            source_settlement_root_hex=ROOT_HEX,
            opening_validation_epoch=0,
            closing_validation_epoch=MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
            validator_quorum_certificate_ref=f"validator_quorum_sha256:{'a' * 64}",
            evidence_ref=f"monthly_close_evidence_sha256:{'b' * 64}",
        )
    return compute_epoch_distribution(
        EpochDistributionInput(
            issuance_epoch=issuance_epoch,
            total_epoch_fees_ilc=Decimal("100"),
            genesis_cumulative_accrual_ilc=Decimal("0"),
            eligible_agents={AGENT_ID: Decimal("1")},
            prior_carry_forward_records=[],
            source_settlement_root_hex=ROOT_HEX,
            monthly_maturity_proof=proof,
        )
    )


def test_gate_passes_verified_balanced_output() -> None:
    output = _output()

    assert verify_epoch_conservation_before_commit(output) is None


def test_gate_rejects_unverified_output_with_phase_token() -> None:
    bad_unverified = replace(_output(), conservation_verified=False)

    with pytest.raises(ValueError, match=NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN):
        verify_epoch_conservation_before_commit(bad_unverified)


def test_gate_rejects_nonzero_difference_even_if_verified() -> None:
    valid_output = _output()
    bad_difference = replace(
        valid_output,
        conservation_record=replace(
            valid_output.conservation_record,
            difference_ilc=Decimal("0.000000001"),
        ),
    )

    with pytest.raises(ValueError, match=NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN):
        verify_epoch_conservation_before_commit(bad_difference)


def test_gate_rejects_forged_total_credit_even_if_difference_is_zero() -> None:
    valid_output = _output()
    forged_record = replace(
        valid_output.conservation_record,
        total_credit_ilc=valid_output.conservation_record.total_credit_ilc
        + Decimal("0.000000001"),
        difference_ilc=Decimal("0"),
    )
    forged_output = replace(valid_output, conservation_record=forged_record)

    with pytest.raises(ValueError, match=NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN):
        verify_epoch_conservation_before_commit(forged_output)


def test_gate_rejects_forged_total_debit_even_if_difference_is_zero() -> None:
    valid_output = _output()
    forged_record = replace(
        valid_output.conservation_record,
        total_debit_ilc=valid_output.conservation_record.total_debit_ilc
        - Decimal("0.000000001"),
        difference_ilc=Decimal("0"),
    )
    forged_output = replace(valid_output, conservation_record=forged_record)

    with pytest.raises(ValueError, match=NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN):
        verify_epoch_conservation_before_commit(forged_output)


@pytest.mark.parametrize("bad_difference", [Decimal("NaN"), Decimal("Infinity")])
def test_gate_rejects_non_finite_difference_with_phase_token(
    bad_difference: Decimal,
) -> None:
    valid_output = _output()
    bad_output = replace(
        valid_output,
        conservation_record=replace(
            valid_output.conservation_record,
            difference_ilc=bad_difference,
        ),
    )

    with pytest.raises(ValueError, match=NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN):
        verify_epoch_conservation_before_commit(bad_output)


def test_gate_is_idempotent_for_verified_balanced_output() -> None:
    output = _output()

    assert verify_epoch_conservation_before_commit(output) is None
    assert verify_epoch_conservation_before_commit(output) is None


def test_gate_rejects_wrong_type() -> None:
    with pytest.raises(ValueError, match="conservation_gate_requires_epoch_distribution_output"):
        verify_epoch_conservation_before_commit({"conservation_verified": True})  # type: ignore[arg-type]


def test_epoch_zero_output_has_no_bypass_and_passes_when_conserved() -> None:
    output = _output(issuance_epoch=0)

    assert output.issuance_epoch == 0
    assert output.conservation_verified is True
    assert verify_epoch_conservation_before_commit(output) is None


def test_epoch_package_exports_conservation_gate_surface() -> None:
    assert epoch.EPOCH_CONSERVATION_GATE_VERSION == EPOCH_CONSERVATION_GATE_VERSION
    assert (
        epoch.EPOCH_GATE_CONSERVATION_CHECK_ADDED_TOKEN
        == EPOCH_GATE_CONSERVATION_CHECK_ADDED_TOKEN
    )
    assert (
        epoch.EPOCH_0_TO_1_CONSERVATION_ENFORCED_TOKEN
        == EPOCH_0_TO_1_CONSERVATION_ENFORCED_TOKEN
    )
    assert epoch.NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN == NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN
    assert epoch.verify_epoch_conservation_before_commit is verify_epoch_conservation_before_commit
