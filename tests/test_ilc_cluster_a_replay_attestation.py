"""
Tests for ILC Cluster A Replay Attestation.
Phase 141.
"""
import pytest
from ilc_core.protocol.ilc_cluster_a_acceptance_evidence import build_cluster_a_acceptance_evidence
from ilc_core.protocol.ilc_cluster_a_replay_attestation import attest_cluster_a_replay, E_HASH_MISMATCH, E_DECISION_MISMATCH, E_CONST_MISMATCH, E_SCHEMA_INVALID

@pytest.fixture
def base_inputs():
    rec = {"gov_record_id": "r1", "signatures": []}
    app = {"ok": True, "errors": [], "warnings": [], "data": {}}
    conf = {
        "ok": True, 
        "errors": [], 
        "warnings": [], 
        "constitution_checks": {
            "checks": [{"check_id": "C1", "status": "pass"}]
        }
    }
    return rec, app, conf

@pytest.fixture
def valid_evidence(base_inputs):
    rec, app, conf = base_inputs
    return build_cluster_a_acceptance_evidence(
        governance_record=rec, apply_result=app, conformance_result=conf
    )

def test_attestation_pass(base_inputs, valid_evidence):
    rec, app, conf = base_inputs
    res = attest_cluster_a_replay(
        evidence=valid_evidence,
        governance_record=rec,
        apply_result=app,
        conformance_result=conf
    )
    assert res["ok"] is True
    assert res["errors"] == []
    
    # Check individual checks
    checks = {c["check"] for c in res["checks"]}
    assert "check_record_hash_match" in checks
    assert "check_constitution_checks_match" in checks

def test_attest_hash_mismatch(base_inputs, valid_evidence):
    rec, app, conf = base_inputs
    # Tamper with evidence hash
    bad_ev = {**valid_evidence, "record_hash_sha256": "badbeef"}
    
    res = attest_cluster_a_replay(
        evidence=bad_ev,
        governance_record=rec,
        apply_result=app,
        conformance_result=conf
    )
    assert res["ok"] is False
    assert E_HASH_MISMATCH in res["errors"]

def test_attest_constitution_mismatch(base_inputs, valid_evidence):
    rec, app, conf = base_inputs
    # Tamper with checks
    checks = valid_evidence["constitution_checks"]
    bad_checks = [{"check_id": "C1", "status": "fail"}] # was pass
    bad_ev = {**valid_evidence, "constitution_checks": bad_checks}
    
    res = attest_cluster_a_replay(
        evidence=bad_ev,
        governance_record=rec,
        apply_result=app,
        conformance_result=conf
    )
    assert res["ok"] is False
    assert E_CONST_MISMATCH in res["errors"]

def test_attest_decision_mismatch(base_inputs, valid_evidence):
    rec, app, conf = base_inputs
    # Tamper: evidence says accepted, but replay says failed (if we change app result)
    # OR change evidence accepted=False
    bad_ev = {**valid_evidence, "accepted": False}
    
    res = attest_cluster_a_replay(
        evidence=bad_ev,
        governance_record=rec,
        apply_result=app,
        conformance_result=conf
    )
    assert res["ok"] is False
    assert E_DECISION_MISMATCH in res["errors"]

def test_attest_schema_fail(base_inputs, valid_evidence):
    rec, app, conf = base_inputs
    # Remove required field
    bad_ev = {k:v for k,v in valid_evidence.items() if k != "record_hash_sha256"}
    
    res = attest_cluster_a_replay(
        evidence=bad_ev,
        governance_record=rec,
        apply_result=app,
        conformance_result=conf
    )
    assert res["ok"] is False
    assert "schema_violation:evidence_missing_required_field" in res["errors"]
