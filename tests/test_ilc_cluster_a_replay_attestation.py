"""
Tests for ILC Cluster A Replay Attestation.
Phase 141.
"""
import pytest
from ilc_core.protocol.ilc_cluster_a_acceptance_evidence import build_cluster_a_acceptance_evidence
from ilc_core.protocol.ilc_cluster_a_replay_attestation import attest_cluster_a_replay, E_HASH_MISMATCH, E_DECISION_MISMATCH, E_CONST_MISMATCH, E_SCHEMA_INVALID, E_CONTRACT_HASH_MISMATCH

# ... existing fixtures ...

def test_attest_contract_hash_mismatch(base_inputs, valid_evidence):
    rec, app, conf = base_inputs
    # We need to simulate a case where individual fields match but the contract hash check fails.
    # This is hard if contract hash is just a function of the fields we already check.
    # However, if we manually insert a 'valid' evidence but change something that is NOT checked by individual checks
    # but IS checked by digest, we can trigger it.
    # BUT our `attest_cluster_a_replay` implementation performs Deep Equality checks on basically everything in the contract.
    # So if we change something, it will likely fail an individual check first.
    # The only way to trigger ONLY E_CONTRACT_HASH_MISMATCH is if the `canonical_evidence_contract_digest`
    # includes something we missed in individual checks OR if the canonicalization logic handles something differently.
    
    # Actually, E_CONTRACT_HASH_MISMATCH is redundant if we check everything perfectly, but it acts as a "checksum"
    # to guarantee we didn't miss anything.
    # Let's try to tamper with something that might slip through?
    # Maybe order? But we normalize order.
    # Maybe we can mock `canonical_evidence_contract_digest` to return a different value for the "recomputed" evidence?
    
    # Or, we can just tamper with one of the fields and expect BOTH the specific error AND the hash error.
    # Let's tamper with `conformance_ok`.
    
    bad_ev = {**valid_evidence, "conformance_ok": not valid_evidence["conformance_ok"]}
    
    res = attest_cluster_a_replay(
        evidence=bad_ev,
        governance_record=rec,
        apply_result=app,
        conformance_result=conf
    )
    assert res["ok"] is False
    # Should see specific mismatch
    assert "context_violation:evidence_conformance_mismatch" in res["errors"]
    # AND likely the hash mismatch
    assert E_CONTRACT_HASH_MISMATCH in res["errors"] 


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
    bad_ev = {**valid_evidence, "record_hash_sha256": "a" * 64}
    
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
    # New validator returns schema_violation:missing_field_<fieldname>
    assert "schema_violation:missing_field_record_hash_sha256" in res["errors"]

def test_attest_schema_fail_invalid_types(base_inputs, valid_evidence):
    rec, app, conf = base_inputs
    
    # helper to run check
    def run(ev):
        return attest_cluster_a_replay(
            evidence=ev, governance_record=rec, apply_result=app, conformance_result=conf
        )
    
    # 1. Accepted is not bool
    bad_ev_1 = {**valid_evidence, "accepted": "yes"}
    res_1 = run(bad_ev_1)
    assert res_1["ok"] is False
    assert "schema_violation:invalid_type_accepted" in res_1["errors"]
    
    # 2. Errors is not list of strings
    bad_ev_2 = {**valid_evidence, "acceptance_errors": [123]}
    res_2 = run(bad_ev_2)
    assert res_2["ok"] is False
    assert "schema_violation:invalid_item_type_acceptance_errors" in res_2["errors"]
    
    # 2b. Errors is not a list
    bad_ev_2b = {**valid_evidence, "acceptance_errors": "not-a-list"}
    res_2b = run(bad_ev_2b)
    assert res_2b["ok"] is False
    assert "schema_violation:invalid_type_acceptance_errors" in res_2b["errors"]
    
    # 3. Constitution checks is not list of dicts
    bad_ev_3 = {**valid_evidence, "constitution_checks": "invalid"}
    res_3 = run(bad_ev_3)
    assert res_3["ok"] is False
    assert "schema_violation:invalid_type_constitution_checks" in res_3["errors"]
    
    bad_ev_4 = {**valid_evidence, "constitution_checks": ["not-a-dict"]}
    res_4 = run(bad_ev_4)
    assert res_4["ok"] is False
    # Checks items
    assert "schema_violation:invalid_type_constitution_check_item_0" in res_4["errors"]
