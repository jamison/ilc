# SPDX-License-Identifier: AGPL-3.0-only
import argparse
import hashlib
import json

import pytest

from ilc_core.cli import main as cli_main
from ilc_core.validator import (
    CANDIDATE_VALIDATOR_RECORD_SCHEMA_VERSION,
    CANDIDATE_VALIDATOR_REQUIRED_NON_CLAIMS,
    CandidateValidatorRecord,
    build_candidate_validator_record,
)
from ilc_core.validator.validator_admission_ejection_production_path import (
    VALIDATOR_ADMISSION_NOT_ACTIVATED,
)


AGENT_ID = "a" * 96
SHA384 = "b" * 96


def _connectivity_receipt(**overrides):
    receipt = {
        "connectivity_receipt_sha384": SHA384,
        "relay_endpoint": "https://164.90.201.11:51151",
    }
    receipt.update(overrides)
    return receipt


def _capsule_record(**overrides):
    evidence = {"bootstrap_fetch_bundle_cid": "cid:relay-bootstrap-capsule"}
    evidence.update(overrides)
    return {"invite_bootstrap_capsule_evidence": evidence}


def test_candidate_record_defaults_are_zero_weight_and_non_rewarding():
    record = build_candidate_validator_record(agent_id=AGENT_ID)
    body = record.to_canonical_record()

    assert body["validator_mode"] == "candidate"
    assert body["consensus_weight"] == 0
    assert body["bft_quorum_weight"] == 0
    assert body["active_validator_set_member"] is False
    assert body["reward_eligible"] is False
    assert body["settlement_eligible"] is False
    assert body["schema_version"] == CANDIDATE_VALIDATOR_RECORD_SCHEMA_VERSION


@pytest.mark.parametrize(
    ("field", "value", "token"),
    [
        ("validator_mode", "provisional", "candidate_validator_mode_must_be_candidate"),
        ("consensus_weight", 1, "candidate_validator_consensus_weight_must_be_zero"),
        ("consensus_weight", False, "candidate_validator_consensus_weight_must_be_zero"),
        ("bft_quorum_weight", 1, "candidate_validator_bft_quorum_weight_must_be_zero"),
        (
            "active_validator_set_member",
            True,
            "candidate_validator_active_membership_must_be_false",
        ),
        ("reward_eligible", True, "candidate_validator_reward_must_be_false"),
        ("settlement_eligible", True, "candidate_validator_settlement_must_be_false"),
        (
            "trust_tier_consecutive_missed_epochs",
            0,
            "candidate_validator_trust_tier_missed_epochs_must_be_none",
        ),
        (
            "trust_tier_equivocation_state",
            False,
            "candidate_validator_trust_tier_equivocation_must_be_none",
        ),
    ],
)
def test_candidate_record_rejects_admission_or_economic_fields(field, value, token):
    kwargs = {"agent_id": AGENT_ID, field: value}
    with pytest.raises(ValueError, match=token):
        CandidateValidatorRecord(**kwargs)


def test_candidate_record_requires_cdl_107_source_ref():
    with pytest.raises(ValueError, match="candidate_validator_source_cdl_ref_invalid"):
        CandidateValidatorRecord(agent_id=AGENT_ID, source_cdl_ref="CDL-017")


def test_candidate_record_requires_all_non_claims():
    missing = tuple(CANDIDATE_VALIDATOR_REQUIRED_NON_CLAIMS[:-1])
    with pytest.raises(ValueError, match="candidate_validator_required_non_claim_missing"):
        CandidateValidatorRecord(agent_id=AGENT_ID, non_claims=missing)


def test_candidate_record_rejects_duplicate_non_claims():
    duplicate = CANDIDATE_VALIDATOR_REQUIRED_NON_CLAIMS + (
        CANDIDATE_VALIDATOR_REQUIRED_NON_CLAIMS[0],
    )
    with pytest.raises(ValueError, match="candidate_validator_non_claims_duplicate"):
        CandidateValidatorRecord(agent_id=AGENT_ID, non_claims=duplicate)


def test_candidate_record_canonical_json_is_stable_and_ascii():
    record = build_candidate_validator_record(
        agent_id=AGENT_ID,
        connectivity_receipt_ref=SHA384,
        bootstrap_capsule_ref="cid:relay-bootstrap-capsule",
    )

    first = record.to_canonical_json()
    second = record.to_canonical_json()

    assert first == second
    assert json.loads(first)["agent_id"] == AGENT_ID
    assert first == json.dumps(
        json.loads(first),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def test_install_candidate_record_helper_writes_record_and_receipt_ref(tmp_path):
    args = argparse.Namespace(no_validator=False)
    result = cli_main._install_candidate_validator_record_fields(
        args,
        install_dir=tmp_path,
        agent_id=AGENT_ID,
        network_id="public-rc",
        connectivity_receipt=_connectivity_receipt(),
        capsule_record=_capsule_record(),
    )

    record_path = tmp_path / ".ilc" / "validator" / "candidate_validator_record.json"
    payload = record_path.read_bytes()
    expected_sha384 = hashlib.sha384(payload.rstrip(b"\n")).hexdigest()

    assert result["candidate_validator_record_status"] == "written"
    assert result["candidate_validator_record_ref"]["path"] == str(record_path)
    assert result["candidate_validator_record_ref"]["sha384"] == expected_sha384
    assert result["candidate_validator_record_sha384"] == expected_sha384
    assert result["validator_mode"] == "candidate"
    assert result["validator_participation_enabled"] is True
    assert json.loads(payload)["consensus_weight"] == 0


def test_install_candidate_record_helper_preserves_selected_network_id(tmp_path):
    args = argparse.Namespace(no_validator=False)
    cli_main._install_candidate_validator_record_fields(
        args,
        install_dir=tmp_path,
        agent_id=AGENT_ID,
        network_id="testnet-rc",
        connectivity_receipt=_connectivity_receipt(),
        capsule_record=_capsule_record(),
    )

    record_path = tmp_path / ".ilc" / "validator" / "candidate_validator_record.json"
    assert json.loads(record_path.read_text(encoding="utf-8"))["network_id"] == "testnet-rc"


def test_install_candidate_record_helper_opt_out_writes_no_file(tmp_path):
    args = argparse.Namespace(no_validator=True)
    result = cli_main._install_candidate_validator_record_fields(
        args,
        install_dir=tmp_path,
        agent_id=AGENT_ID,
        network_id="public-rc",
        connectivity_receipt=_connectivity_receipt(),
        capsule_record=_capsule_record(),
    )

    assert result == {
        "candidate_validator_record_ref": None,
        "candidate_validator_record_sha384": None,
        "candidate_validator_record_status": "opted_out",
        "validator_mode": "opted_out",
        "validator_participation_enabled": False,
    }
    assert not (tmp_path / ".ilc" / "validator" / "candidate_validator_record.json").exists()


def test_install_candidate_record_helper_rejects_bad_connectivity_ref(tmp_path):
    args = argparse.Namespace(no_validator=False)
    with pytest.raises(ValueError, match="candidate_validator_connectivity_receipt_ref_invalid"):
        cli_main._install_candidate_validator_record_fields(
            args,
            install_dir=tmp_path,
            agent_id=AGENT_ID,
            network_id="public-rc",
            connectivity_receipt=_connectivity_receipt(connectivity_receipt_sha384=123),
            capsule_record=_capsule_record(),
        )


def test_install_candidate_record_helper_rejects_bad_capsule_evidence(tmp_path):
    args = argparse.Namespace(no_validator=False)
    with pytest.raises(ValueError, match="candidate_validator_bootstrap_capsule_evidence_invalid"):
        cli_main._install_candidate_validator_record_fields(
            args,
            install_dir=tmp_path,
            agent_id=AGENT_ID,
            network_id="public-rc",
            connectivity_receipt=_connectivity_receipt(),
            capsule_record={"invite_bootstrap_capsule_evidence": []},
        )


def test_install_candidate_record_helper_never_calls_admission_transition(monkeypatch, tmp_path):
    def fail_transition(*args, **kwargs):  # pragma: no cover - must not be called
        raise AssertionError("validator admission path must not be used")

    monkeypatch.setattr(
        "ilc_core.validator.validator_admission_ejection_production_path."
        "build_validator_set_transition_result",
        fail_transition,
    )

    result = cli_main._install_candidate_validator_record_fields(
        argparse.Namespace(no_validator=False),
        install_dir=tmp_path,
        agent_id=AGENT_ID,
        network_id="public-rc",
        connectivity_receipt=_connectivity_receipt(),
        capsule_record=_capsule_record(),
    )

    assert result["candidate_validator_record_status"] == "written"


def test_install_parser_exposes_no_validator_opt_out():
    parser = cli_main._build_parser()
    args = parser.parse_args(["install", "--from-invite", "{}", "--no-validator"])

    assert args.no_validator is True


def test_validator_admission_guard_remains_closed():
    assert VALIDATOR_ADMISSION_NOT_ACTIVATED is True
