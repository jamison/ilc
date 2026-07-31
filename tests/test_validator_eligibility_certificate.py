from __future__ import annotations

import inspect
from decimal import Decimal

import pytest

from ilc_core.validator import validator_eligibility_certificate as eligibility
from ilc_core.validator.validator_eligibility_certificate import (
    BOOTSTRAP_ACTIVE_RATIONALE,
    CANDIDATE,
    CANDIDATE_EVIDENCE_RATIONALE,
    CDL_106_DEPENDENCY,
    CDL_107_DEPENDENCY,
    OFFICIAL,
    OFFICIAL_EVIDENCE_RATIONALE,
    PRODUCTION_ELIGIBILITY_NOT_ACTIVATED_TOKEN,
    PROVISIONAL,
    PROVISIONAL_EVIDENCE_RATIONALE,
    VALIDATOR_ELIGIBILITY_CERT_VERSION,
    GenesisBootstrapAuthorityCertificate,
    ValidatorEligibilityCertificate,
    evaluate_eligibility,
    require_production_eligibility_activation,
)

AGENT_ID = "a" * 96
GENESIS_AGENT_ID = "b" * 96
REPUTATION_ROOT = "1" * 64
WORK_SCORE_ROOT = "2" * 64
LIVENESS_ROOT = "3" * 64


def _bootstrap(sunset: int = 4) -> GenesisBootstrapAuthorityCertificate:
    return GenesisBootstrapAuthorityCertificate(
        genesis_agent_id=GENESIS_AGENT_ID,
        authorized_agent_id=AGENT_ID,
        bootstrap_sunset_epoch=sunset,
        authority_token="genesis_bootstrap_authority_opened_GAP_REPUTATION_03",
    )


def test_no_evidence_yields_candidate() -> None:
    cert = evaluate_eligibility(agent_id=AGENT_ID, epoch=5)

    assert cert.eligibility_verdict == CANDIDATE
    assert cert.verdict_rationale == CANDIDATE_EVIDENCE_RATIONALE


def test_partial_evidence_yields_provisional() -> None:
    cert = evaluate_eligibility(
        agent_id=AGENT_ID,
        epoch=5,
        reputation_evidence_root=REPUTATION_ROOT,
    )

    assert cert.eligibility_verdict == PROVISIONAL
    assert cert.verdict_rationale == PROVISIONAL_EVIDENCE_RATIONALE


def test_all_three_evidence_roots_yield_official() -> None:
    cert = evaluate_eligibility(
        agent_id=AGENT_ID,
        epoch=5,
        reputation_evidence_root=REPUTATION_ROOT,
        earned_ecu_work_score_root=WORK_SCORE_ROOT,
        liveness_root=LIVENESS_ROOT,
    )

    assert cert.eligibility_verdict == OFFICIAL
    assert cert.verdict_rationale == OFFICIAL_EVIDENCE_RATIONALE


def test_bootstrap_authority_within_sunset_yields_official() -> None:
    cert = evaluate_eligibility(agent_id=AGENT_ID, epoch=4, bootstrap_authority=_bootstrap())

    assert cert.eligibility_verdict == OFFICIAL
    assert cert.verdict_rationale == BOOTSTRAP_ACTIVE_RATIONALE


def test_bootstrap_authority_and_evidence_roots_can_coexist_with_bootstrap_precedence() -> None:
    cert = evaluate_eligibility(
        agent_id=AGENT_ID,
        epoch=3,
        reputation_evidence_root=REPUTATION_ROOT,
        earned_ecu_work_score_root=WORK_SCORE_ROOT,
        liveness_root=LIVENESS_ROOT,
        bootstrap_authority=_bootstrap(),
    )

    assert cert.eligibility_verdict == OFFICIAL
    assert cert.verdict_rationale == BOOTSTRAP_ACTIVE_RATIONALE
    assert cert.reputation_evidence_root == REPUTATION_ROOT


def test_bootstrap_authority_is_bound_to_authorized_agent_id() -> None:
    bootstrap = GenesisBootstrapAuthorityCertificate(
        genesis_agent_id=GENESIS_AGENT_ID,
        authorized_agent_id="c" * 96,
        bootstrap_sunset_epoch=4,
        authority_token="genesis_bootstrap_authority_opened_GAP_REPUTATION_03",
    )

    with pytest.raises(ValueError, match="bootstrap_authority_agent_mismatch"):
        evaluate_eligibility(agent_id=AGENT_ID, epoch=1, bootstrap_authority=bootstrap)


def test_expired_bootstrap_falls_through_to_official_when_all_roots_exist() -> None:
    cert = evaluate_eligibility(
        agent_id=AGENT_ID,
        epoch=5,
        reputation_evidence_root=REPUTATION_ROOT,
        earned_ecu_work_score_root=WORK_SCORE_ROOT,
        liveness_root=LIVENESS_ROOT,
        bootstrap_authority=_bootstrap(),
    )

    assert cert.eligibility_verdict == OFFICIAL
    assert cert.verdict_rationale == OFFICIAL_EVIDENCE_RATIONALE


def test_expired_bootstrap_falls_through_to_candidate_without_evidence() -> None:
    cert = evaluate_eligibility(agent_id=AGENT_ID, epoch=5, bootstrap_authority=_bootstrap())

    assert cert.eligibility_verdict == CANDIDATE
    assert cert.verdict_rationale == CANDIDATE_EVIDENCE_RATIONALE


def test_certificate_rejects_mismatched_direct_verdict() -> None:
    with pytest.raises(ValueError, match="eligibility_verdict_mismatch"):
        ValidatorEligibilityCertificate(
            agent_id=AGENT_ID,
            epoch=5,
            reputation_evidence_root=REPUTATION_ROOT,
            earned_ecu_work_score_root=WORK_SCORE_ROOT,
            liveness_root=LIVENESS_ROOT,
            bootstrap_authority=None,
            eligibility_verdict=CANDIDATE,
            verdict_rationale=CANDIDATE_EVIDENCE_RATIONALE,
        )


def test_invalid_agent_id_rejected() -> None:
    with pytest.raises(ValueError, match="agent_id_must_be_96_lower_hex"):
        evaluate_eligibility(agent_id="not-hex", epoch=0)


def test_invalid_root_rejected() -> None:
    with pytest.raises(ValueError, match="reputation_evidence_root_must_be_sha256_hex_or_none"):
        evaluate_eligibility(
            agent_id=AGENT_ID,
            epoch=0,
            reputation_evidence_root="not-a-root",
        )


def test_negative_epoch_rejected() -> None:
    with pytest.raises(ValueError, match="epoch_must_be_non_negative_int"):
        evaluate_eligibility(agent_id=AGENT_ID, epoch=-1)


def test_non_finite_decimal_rejected() -> None:
    with pytest.raises(ValueError, match="epoch_non_finite_decimal"):
        evaluate_eligibility(agent_id=AGENT_ID, epoch=Decimal("NaN"))


def test_float_input_rejected() -> None:
    with pytest.raises(ValueError, match="epoch_float_not_allowed"):
        evaluate_eligibility(agent_id=AGENT_ID, epoch=1.0)


def test_production_guard_raises() -> None:
    with pytest.raises(ValueError, match=PRODUCTION_ELIGIBILITY_NOT_ACTIVATED_TOKEN):
        require_production_eligibility_activation()


def test_canonical_record_and_hash_are_deterministic() -> None:
    cert = evaluate_eligibility(
        agent_id=AGENT_ID,
        epoch=5,
        reputation_evidence_root=REPUTATION_ROOT,
        earned_ecu_work_score_root=WORK_SCORE_ROOT,
        liveness_root=LIVENESS_ROOT,
    )
    first = cert.certificate_sha256()
    second = evaluate_eligibility(
        agent_id=AGENT_ID,
        epoch=5,
        earned_ecu_work_score_root=WORK_SCORE_ROOT,
        liveness_root=LIVENESS_ROOT,
        reputation_evidence_root=REPUTATION_ROOT,
    ).certificate_sha256()

    assert first == second
    assert len(first) == 64
    assert cert.to_canonical_record()["schema_version"] == VALIDATOR_ELIGIBILITY_CERT_VERSION
    assert cert.to_canonical_record()["cdl_106_dependency"] == CDL_106_DEPENDENCY
    assert cert.to_canonical_record()["cdl_107_dependency"] == CDL_107_DEPENDENCY


def test_canonical_json_uses_required_hash_settings() -> None:
    source = inspect.getsource(eligibility)

    assert "sort_keys=True" in source
    assert 'separators=(",", ":")' in source
    assert "allow_nan=False" in source
