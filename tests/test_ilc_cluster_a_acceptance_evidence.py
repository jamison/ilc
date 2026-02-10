"""
Tests for ILC Cluster A Acceptance Evidence Builder.
Phase 141.
"""
import pytest
import datetime
from ilc_core.protocol.ilc_cluster_a_acceptance_evidence import build_cluster_a_acceptance_evidence

# Fixtures
@pytest.fixture
def mock_gov_record():
    return {
        "gov_record_id": "rec-1",
        "payload": {"foo": "bar"},
        "signatures": []
    }

@pytest.fixture
def mock_apply_res():
    return {
        "ok": True,
        "errors": [],
        "warnings": ["warn_a", "warn_b"],
        "data": {"policy_state_delta": {"k": "v"}}
    }

@pytest.fixture
def mock_conf_res():
    return {
        "ok": True,
        "errors": [],
        "warnings": ["warn_c"],
        "constitution_checks": {
            "checks": [
                {"check_id": "CONST-002", "status": "pass"},
                {"check_id": "CONST-001", "status": "pass"}
            ]
        }
    }

def test_evidence_structure(mock_gov_record, mock_apply_res, mock_conf_res):
    evidence = build_cluster_a_acceptance_evidence(
        governance_record=mock_gov_record,
        apply_result=mock_apply_res,
        conformance_result=mock_conf_res
    )
    
    assert evidence["artifact_kind"] == "cluster_a_acceptance_evidence"
    assert evidence["artifact_version"] == "v0.1"
    assert evidence["record_uid"] == "rec-1"
    assert isinstance(evidence["record_hash_sha256"], str)
    assert evidence["accepted"] is True
    assert evidence["conformance_ok"] is True
    
    # Check sorting of warnings
    assert evidence["acceptance_warnings"] == ["warn_a", "warn_b", "warn_c"]
    
    # Check sorting of constitution checks
    checks = evidence["constitution_checks"]
    assert len(checks) == 2
    assert checks[0]["check_id"] == "CONST-001"
    assert checks[1]["check_id"] == "CONST-002"

def test_evidence_timestamp_strict_iso():
    rec = {"gov_record_id": "rec-1"}
    ev = build_cluster_a_acceptance_evidence(
        governance_record=rec, apply_result={}, conformance_result={}
    )
    ts = ev["generated_at"]
    # Should be valid ISO
    dt = datetime.datetime.fromisoformat(ts)
    assert dt.tzinfo is not None

def test_determinism_sorting():
    rec = {"gov_record_id": "rec-1", "signatures": []}
    apply_res = {"ok": False, "errors": ["err_z", "err_a"], "warnings": []}
    conf_res = {"ok": False, "errors": ["err_m"], "warnings": []}
    
    ctx = {"timestamp": "2026-02-10T00:00:00Z"}
    ev1 = build_cluster_a_acceptance_evidence(
        governance_record=rec, apply_result=apply_res, conformance_result=conf_res, runtime_context=ctx
    )
    ev2 = build_cluster_a_acceptance_evidence(
        governance_record=rec, apply_result=apply_res, conformance_result=conf_res, runtime_context=ctx
    )
    
    assert ev1["acceptance_errors"] == ["err_a", "err_m", "err_z"]
    assert ev1 == ev2 # strict equality
