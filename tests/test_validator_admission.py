from __future__ import annotations

from decimal import Decimal

import pytest

from ilc_core.validator import (
    GENESIS_BOOTSTRAP_AUTHORITY_TOKEN,
    OFFICIAL,
    PRODUCTION_VALIDATOR_ADMISSION_ACTIVATION_TOKEN,
    PRODUCTION_VALIDATOR_ADMISSION_NOT_ACTIVATED_TOKEN,
    PROVISIONAL,
    VALIDATOR_ADMISSION_CDL055_BOND_SURFACE_TOKEN,
    VALIDATOR_ROLE_RECORD_VERSION,
    GenesisBootstrapAuthorityCertificate,
    ValidatorRoleRecord,
    admit_validator,
    build_validator_role_record,
    evaluate_eligibility,
)


AGENT_ID = "a" * 96
GENESIS_AGENT_ID = "b" * 96
NETWORK_ID = "ilc-rc01"
REPUTATION_ROOT = "1" * 64
WORK_SCORE_ROOT = "2" * 64
LIVENESS_ROOT = "3" * 64
VALIDATOR_KEY = "c" * 96
VALIDATOR_ENDPOINT = "100.101.102.103:9101"


def _bootstrap() -> GenesisBootstrapAuthorityCertificate:
    return GenesisBootstrapAuthorityCertificate(
        genesis_agent_id=GENESIS_AGENT_ID,
        authorized_agent_id=AGENT_ID,
        network_id=NETWORK_ID,
        bootstrap_effective_from_epoch=1,
        bootstrap_sunset_epoch=4,
        authority_token=GENESIS_BOOTSTRAP_AUTHORITY_TOKEN,
    )


def _official_certificate():
    return evaluate_eligibility(
        agent_id=AGENT_ID,
        network_id=NETWORK_ID,
        epoch=1,
        earned_ecu_work_score_root=WORK_SCORE_ROOT,
        liveness_root=LIVENESS_ROOT,
        bootstrap_authority=_bootstrap(),
    )


def test_phase_1589_official_bootstrap_activation_requires_operational_roots() -> None:
    cert = _official_certificate()

    decision = admit_validator(
        current_epoch=0,
        active_from_epoch=1,
        current_validator_ids=[1, 2, 3, 4],
        current_agent_ids=[],
        validator_id=5,
        agent_id=AGENT_ID,
        stake_ecu=Decimal("400"),
        activation_token=PRODUCTION_VALIDATOR_ADMISSION_ACTIVATION_TOKEN,
        network_id=NETWORK_ID,
        validator_key=VALIDATOR_KEY,
        validator_endpoint=VALIDATOR_ENDPOINT,
        eligibility_certificate=cert,
    )

    role = decision.validator_role_record
    assert decision.production_validator_admission_activated is True
    assert decision.decision_token == PRODUCTION_VALIDATOR_ADMISSION_ACTIVATION_TOKEN
    assert isinstance(role, ValidatorRoleRecord)
    assert role.schema_version == VALIDATOR_ROLE_RECORD_VERSION
    assert role.role_status == OFFICIAL
    assert role.quorum_weight == 1
    assert role.rust_validator_set_eligible is True
    assert role.reputation_evidence_root is None
    assert role.earned_ecu_work_score_root == WORK_SCORE_ROOT
    assert role.liveness_state_root == LIVENESS_ROOT
    assert role.cdl055_bond_surface_token == VALIDATOR_ADMISSION_CDL055_BOND_SURFACE_TOKEN


def test_phase_1589_bootstrap_without_operational_roots_cannot_activate() -> None:
    cert = evaluate_eligibility(
        agent_id=AGENT_ID,
        network_id=NETWORK_ID,
        epoch=1,
        bootstrap_authority=_bootstrap(),
    )

    assert cert.eligibility_verdict == PROVISIONAL
    with pytest.raises(ValueError, match="validator_activation_requires_official_role_phase_1589"):
        admit_validator(
            current_epoch=0,
            active_from_epoch=1,
            current_validator_ids=[1, 2, 3, 4],
            validator_id=5,
            agent_id=AGENT_ID,
            stake_ecu=Decimal("400"),
            activation_token=PRODUCTION_VALIDATOR_ADMISSION_ACTIVATION_TOKEN,
            network_id=NETWORK_ID,
            validator_key=VALIDATOR_KEY,
            validator_endpoint=VALIDATOR_ENDPOINT,
            eligibility_certificate=cert,
        )


def test_phase_1589_candidate_and_provisional_records_have_zero_quorum() -> None:
    candidate = build_validator_role_record(
        agent_id=AGENT_ID,
        validator_id=5,
        validator_key=VALIDATOR_KEY,
        validator_endpoint=VALIDATOR_ENDPOINT,
        effective_from_epoch=1,
        network_id=NETWORK_ID,
    )

    assert candidate.role_status == "candidate"
    assert candidate.quorum_weight == 0
    assert candidate.rust_validator_set_eligible is False

    with pytest.raises(ValueError, match="non_official_validator_quorum_weight_must_be_zero"):
        build_validator_role_record(
            agent_id=AGENT_ID,
            validator_id=5,
            validator_key=VALIDATOR_KEY,
            validator_endpoint=VALIDATOR_ENDPOINT,
            effective_from_epoch=1,
            network_id=NETWORK_ID,
            role_status=PROVISIONAL,
            quorum_weight=1,
        )


def test_phase_1589_rejects_mismatched_eligibility_certificate() -> None:
    cert = evaluate_eligibility(
        agent_id="d" * 96,
        network_id=NETWORK_ID,
        epoch=1,
        reputation_evidence_root=REPUTATION_ROOT,
        earned_ecu_work_score_root=WORK_SCORE_ROOT,
        liveness_root=LIVENESS_ROOT,
    )

    with pytest.raises(ValueError, match="eligibility_certificate_agent_mismatch_phase_1589"):
        build_validator_role_record(
            agent_id=AGENT_ID,
            validator_id=5,
            validator_key=VALIDATOR_KEY,
            validator_endpoint=VALIDATOR_ENDPOINT,
            effective_from_epoch=1,
            network_id=NETWORK_ID,
            eligibility_certificate=cert,
        )


def test_phase_1589_default_off_path_remains_available_without_activation_token() -> None:
    decision = admit_validator(
        current_epoch=0,
        active_from_epoch=1,
        current_validator_ids=[1, 2, 3, 4],
        validator_id=5,
        agent_id=AGENT_ID,
        stake_ecu=Decimal("400"),
    )

    assert decision.production_validator_admission_activated is False
    assert decision.decision_token == PRODUCTION_VALIDATOR_ADMISSION_NOT_ACTIVATED_TOKEN
    assert decision.validator_role_record is None


def test_phase_1589_default_off_role_record_uses_not_activated_authority() -> None:
    decision = admit_validator(
        current_epoch=0,
        active_from_epoch=1,
        current_validator_ids=[1, 2, 3, 4],
        validator_id=5,
        agent_id=AGENT_ID,
        stake_ecu=Decimal("400"),
        network_id=NETWORK_ID,
        validator_key=VALIDATOR_KEY,
        validator_endpoint=VALIDATOR_ENDPOINT,
    )

    assert decision.production_validator_admission_activated is False
    assert decision.validator_role_record is not None
    assert (
        decision.validator_role_record.admission_authority_token
        == PRODUCTION_VALIDATOR_ADMISSION_NOT_ACTIVATED_TOKEN
    )


def test_phase_1589_activation_rejects_role_authority_token_mismatch() -> None:
    cert = _official_certificate()

    with pytest.raises(ValueError, match="validator_role_record_authority_token_mismatch_phase_1589"):
        admit_validator(
            current_epoch=0,
            active_from_epoch=1,
            current_validator_ids=[1, 2, 3, 4],
            current_agent_ids=[],
            validator_id=5,
            agent_id=AGENT_ID,
            stake_ecu=Decimal("400"),
            activation_token=PRODUCTION_VALIDATOR_ADMISSION_ACTIVATION_TOKEN,
            network_id=NETWORK_ID,
            validator_key=VALIDATOR_KEY,
            validator_endpoint=VALIDATOR_ENDPOINT,
            eligibility_certificate=cert,
            admission_authority_token="wrong_authority_token",
        )
