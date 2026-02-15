
import pytest
import copy
from ilc_core.exceptions import ReplayProofPackageError
from ilc_core.protocol.ilc_cluster_a_replay_proof_package import (
    build_cluster_a_replay_proof_package,
    verify_cluster_a_replay_proof_package,
    _canonical_package_digest,
    E_SCHEMA_INVALID_PACKAGE,
    E_MISSING_FIELD_PACKAGE,
    E_HASH_MISMATCH_PACKAGE,
    E_CONTRACT_HASH_MISMATCH,
    E_RECORD_HASH_MISMATCH,
    E_ATTESTATION_FAILED
)
from ilc_core.protocol.ilc_cluster_a_acceptance_evidence import build_cluster_a_acceptance_evidence

@pytest.fixture
def governance_record():
    return {
        "gov_record_id": "rec_001",
        "proposal_id": "prop_1",
        "state": "proposed",
        "payload": {"foo": "bar"},
        "signatures": [] # Normally signatures here
    }

@pytest.fixture
def apply_result():
    return {"ok": True, "errors": [], "warnings": []}

@pytest.fixture
def conformance_result():
    return {
        "ok": True, 
        "errors": [], 
        "warnings": [], 
        "constitution_checks": {
            "checks": [{"check_id": "C1", "status": "pass"}]
        }
    }

@pytest.fixture
def evidence(governance_record, apply_result, conformance_result):
    return build_cluster_a_acceptance_evidence(
        governance_record=governance_record,
        apply_result=apply_result,
        conformance_result=conformance_result
    )

def test_build_and_verify_success(governance_record, apply_result, conformance_result, evidence):
    package = build_cluster_a_replay_proof_package(
        evidence=evidence,
        governance_record=governance_record,
        apply_result=apply_result,
        conformance_result=conformance_result
    )
    
    assert package["package_version"] == "v0.1"
    assert "package_hash_sha256" in package
    
    # Verify
    res = verify_cluster_a_replay_proof_package(package)
    assert res["ok"] is True
    assert res["errors"] == []
    
    checks = {c["check"] for c in res["checks"]}
    assert "check_package_hash_match" in checks
    assert "check_evidence_contract_hash_match" in checks
    assert "check_record_hash_match" in checks
    assert "check_replay_attest" in checks


def test_build_fails_with_domain_exception_on_invalid_evidence(governance_record, apply_result, conformance_result):
    with pytest.raises(ReplayProofPackageError, match="schema_violation:invalid_evidence_input"):
        build_cluster_a_replay_proof_package(
            evidence="bad-evidence-object",
            governance_record=governance_record,
            apply_result=apply_result,
            conformance_result=conformance_result,
        )


def test_build_fails_with_domain_exception_on_missing_record_hash(
    governance_record, apply_result, conformance_result, evidence
):
    bad_evidence = copy.deepcopy(evidence)
    bad_evidence.pop("record_hash_sha256", None)
    with pytest.raises(ReplayProofPackageError, match="schema_violation:evidence_missing_record_hash_sha256"):
        build_cluster_a_replay_proof_package(
            evidence=bad_evidence,
            governance_record=governance_record,
            apply_result=apply_result,
            conformance_result=conformance_result,
        )

def test_verify_fails_package_hash_mismatch(governance_record, apply_result, conformance_result, evidence):
    package = build_cluster_a_replay_proof_package(
        evidence=evidence,
        governance_record=governance_record,
        apply_result=apply_result,
        conformance_result=conformance_result
    )
    
    # Tamper payload without updating hash
    package["evidence"]["accepted"] = not package["evidence"]["accepted"]
    
    res = verify_cluster_a_replay_proof_package(package)
    assert res["ok"] is False
    assert E_HASH_MISMATCH_PACKAGE in res["errors"]

def test_verify_fails_contract_hash_mismatch(governance_record, apply_result, conformance_result, evidence):
    package = build_cluster_a_replay_proof_package(
        evidence=evidence,
        governance_record=governance_record,
        apply_result=apply_result,
        conformance_result=conformance_result
    )
    
    # Tamper hash field
    package["evidence_contract_hash_sha256"] = "bad" * 16 # roughly hex-ish length
    # Update package hash to match the tampering of the hash field, so we pass package hash check
    # But specifically, we need to bypass package hash check to reach contract hash check?
    # verify_cluster_a_replay_proof_package stops at package hash check if mismatch.
    # So we MUST update package hash.
    
    # Re-sign the package with the bad contract hash
    package["package_hash_sha256"] = _canonical_package_digest(package)
    
    res = verify_cluster_a_replay_proof_package(package)
    assert res["ok"] is False
    # Should flag contract hash mismatch (claimed vs computed from evidence)
    assert E_CONTRACT_HASH_MISMATCH in res["errors"]

def test_verify_fails_record_hash_mismatch(governance_record, apply_result, conformance_result, evidence):
    package = build_cluster_a_replay_proof_package(
        evidence=evidence,
        governance_record=governance_record,
        apply_result=apply_result,
        conformance_result=conformance_result
    )
    
    # Tamper record inside replay_contract
    package["replay_contract"]["governance_record"]["payload"]["foo"] = "baz"
    
    # Update package hash
    package["package_hash_sha256"] = _canonical_package_digest(package)
    
    res = verify_cluster_a_replay_proof_package(package)
    assert res["ok"] is False
    assert E_RECORD_HASH_MISMATCH in res["errors"]

def test_verify_fails_attestation_mismatch(governance_record, apply_result, conformance_result, evidence):
    package = build_cluster_a_replay_proof_package(
        evidence=evidence,
        governance_record=governance_record,
        apply_result=apply_result,
        conformance_result=conformance_result
    )
    
    # Change conformance result in contract (e.g. say it failed)
    package["replay_contract"]["conformance_result"]["ok"] = False
    
    # Update package hash
    package["package_hash_sha256"] = _canonical_package_digest(package)
    
    res = verify_cluster_a_replay_proof_package(package)
    assert res["ok"] is False
    assert E_ATTESTATION_FAILED in res["errors"]
    # Should also see specific mismatch from attest
    assert any("evidence_conformance_mismatch" in e for e in res["errors"])

def test_verify_fails_missing_field(governance_record, apply_result, conformance_result, evidence):
    package = build_cluster_a_replay_proof_package(
        evidence=evidence,
        governance_record=governance_record,
        apply_result=apply_result,
        conformance_result=conformance_result
    )
    
    del package["replay_contract"]
    
    res = verify_cluster_a_replay_proof_package(package)
    assert res["ok"] is False
    assert E_MISSING_FIELD_PACKAGE in res["errors"]

def test_verify_fails_malformed_input():
    # Test non-dict input
    res = verify_cluster_a_replay_proof_package(None)
    assert res["ok"] is False
    assert E_SCHEMA_INVALID_PACKAGE in res["errors"]
    assert res["checks"][0]["check"] == "check_package_root_type"

    res = verify_cluster_a_replay_proof_package("not a dict")
    assert res["ok"] is False
    assert E_SCHEMA_INVALID_PACKAGE in res["errors"]

    res = verify_cluster_a_replay_proof_package([])
    assert res["ok"] is False
    assert E_SCHEMA_INVALID_PACKAGE in res["errors"]

def test_verify_fails_invalid_version(governance_record, apply_result, conformance_result, evidence):
    package = build_cluster_a_replay_proof_package(
        evidence=evidence,
        governance_record=governance_record,
        apply_result=apply_result,
        conformance_result=conformance_result
    )
    
    package["package_version"] = "v0.99"
    # Recalculate hash to bypass hash check, so we hit version check validity?
    # No, version check is 0.1, before hash check.
    
    res = verify_cluster_a_replay_proof_package(package)
    assert res["ok"] is False
    assert E_SCHEMA_INVALID_PACKAGE in res["errors"]
    assert res["checks"][0]["check"] == "check_package_version"

def test_verify_fails_malformed_evidence(governance_record, apply_result, conformance_result, evidence):
    package = build_cluster_a_replay_proof_package(
        evidence=evidence,
        governance_record=governance_record,
        apply_result=apply_result,
        conformance_result=conformance_result
    )
    
    # Malform evidence (not a dict)
    package["evidence"] = "not a dict"
    
    # Recalculate package hash to pass step 2
    package["package_hash_sha256"] = _canonical_package_digest(package)
    
    res = verify_cluster_a_replay_proof_package(package)
    assert res["ok"] is False
    assert E_SCHEMA_INVALID_PACKAGE in res["errors"]
    # Should fail at check_evidence_type
    assert any(c["check"] == "check_evidence_type" for c in res["checks"])

def test_verify_fails_malformed_contract(governance_record, apply_result, conformance_result, evidence):
    package = build_cluster_a_replay_proof_package(
        evidence=evidence,
        governance_record=governance_record,
        apply_result=apply_result,
        conformance_result=conformance_result
    )
    
    # Malform replay_contract (not a dict)
    package["replay_contract"] = "not a dict"
    
    res = verify_cluster_a_replay_proof_package(package)
    assert res["ok"] is False
    assert E_SCHEMA_INVALID_PACKAGE in res["errors"]
    # We allow checks to vary slightly but at least one should fail on type
    assert any(c["check"] == "check_replay_contract_type" for c in res["checks"])


def test_verify_fails_unknown_package_field(governance_record, apply_result, conformance_result, evidence):
    package = build_cluster_a_replay_proof_package(
        evidence=evidence,
        governance_record=governance_record,
        apply_result=apply_result,
        conformance_result=conformance_result
    )
    
    # Add unknown top-level field
    package["unknown_garbage"] = "bad"
    
    res = verify_cluster_a_replay_proof_package(package)
    assert res["ok"] is False
    assert E_SCHEMA_INVALID_PACKAGE in res["errors"]
    assert res["checks"][0]["check"] == "check_package_unknown_fields"


def test_verify_fails_unknown_contract_field(governance_record, apply_result, conformance_result, evidence):
    package = build_cluster_a_replay_proof_package(
        evidence=evidence,
        governance_record=governance_record,
        apply_result=apply_result,
        conformance_result=conformance_result
    )
    
    # Add unknown contract field
    package["replay_contract"]["extra_stuff"] = {}
    
    # Recalculate package hash because modifying deeper structure changes hash? 
    # Yes, contract is part of package. But wait, verification fails schema BEFORE hash check.
    # So we don't even need to fix the hash to see the schema failure.
    
    res = verify_cluster_a_replay_proof_package(package)
    assert res["ok"] is False
    assert E_SCHEMA_INVALID_PACKAGE in res["errors"]
    assert res["checks"][0]["check"] == "check_replay_contract_unknown_fields"
