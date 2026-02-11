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

def test_build_strict_timestamp_validation(mock_gov_record, mock_apply_res, mock_conf_res):
    # 1. Invalid type
    with pytest.raises(ValueError, match="strict ISO-8601 UTC string"):
        build_cluster_a_acceptance_evidence(
            governance_record=mock_gov_record,
            apply_result=mock_apply_res,
            conformance_result=mock_conf_res,
            runtime_context={"timestamp": 12345}
        )
        
    # 2. Missing Z suffix
    with pytest.raises(ValueError, match="strict ISO-8601 UTC string"):
        build_cluster_a_acceptance_evidence(
            governance_record=mock_gov_record,
            apply_result=mock_apply_res,
            conformance_result=mock_conf_res,
            runtime_context={"timestamp": "2026-02-10T12:00:00"}
        )

def test_normalization_type_safety():
    from ilc_core.protocol.ilc_cluster_a_acceptance_evidence import _sorted_unique_str
    
    # Valid
    assert _sorted_unique_str(["b", "a"]) == ["a", "b"]
    
    # Invalid: not a list
    with pytest.raises(TypeError):
        _sorted_unique_str("not-a-list")
        
    # Invalid: list contains int
    with pytest.raises(TypeError):
        _sorted_unique_str(["a", 1])

def test_validate_evidence_rejection_extra_fields(mock_gov_record, mock_apply_res, mock_conf_res):
    from ilc_core.protocol.ilc_cluster_a_acceptance_evidence import validate_evidence_schema
    ev = build_cluster_a_acceptance_evidence(
        governance_record=mock_gov_record,
        apply_result=mock_apply_res,
        conformance_result=mock_conf_res
    )
    # Valid initially
    assert validate_evidence_schema(ev) == []
    
    # Introduce extra field
    ev["extra_field"] = "should not be here"
    errors = validate_evidence_schema(ev)
    assert "schema_violation:unknown_field_extra_field" in errors

def test_validate_evidence_rejection_bad_hash(mock_gov_record, mock_apply_res, mock_conf_res):
    from ilc_core.protocol.ilc_cluster_a_acceptance_evidence import validate_evidence_schema
    ev = build_cluster_a_acceptance_evidence(
        governance_record=mock_gov_record,
        apply_result=mock_apply_res,
        conformance_result=mock_conf_res
    )
    
    # Bad hash length
    ev["record_hash_sha256"] = "badhash"
    errors = validate_evidence_schema(ev)
    assert "schema_violation:invalid_format_record_hash_sha256" in errors
    
    # Non-string
    ev["record_hash_sha256"] = 123
    errors = validate_evidence_schema(ev)
    assert "schema_violation:invalid_type_record_hash_sha256" in errors

def test_validate_evidence_rejection_bad_timestamp_format(mock_gov_record, mock_apply_res, mock_conf_res):
    from ilc_core.protocol.ilc_cluster_a_acceptance_evidence import validate_evidence_schema
    ev = build_cluster_a_acceptance_evidence(
        governance_record=mock_gov_record,
        apply_result=mock_apply_res,
        conformance_result=mock_conf_res
    )
    
    # Missing Z
    ev["generated_at"] = "2026-02-10T12:00:00" 
    errors = validate_evidence_schema(ev)
    assert "schema_violation:invalid_format_generated_at_utc_suffix" in errors
    
    # Bad ISO
    ev["generated_at"] = "not-a-timestampZ"
    errors = validate_evidence_schema(ev)
    assert "schema_violation:invalid_format_generated_at_iso8601" in errors

def test_validate_evidence_rejection_missing_fields(mock_gov_record, mock_apply_res, mock_conf_res):
    from ilc_core.protocol.ilc_cluster_a_acceptance_evidence import validate_evidence_schema
    ev = build_cluster_a_acceptance_evidence(
        governance_record=mock_gov_record,
        apply_result=mock_apply_res,
        conformance_result=mock_conf_res
    )
    
    del ev["artifact_kind"]
    errors = validate_evidence_schema(ev)
    assert "schema_violation:missing_field_artifact_kind" in errors

def test_validate_evidence_rejection_check_item_shape(mock_gov_record, mock_apply_res, mock_conf_res):
    from ilc_core.protocol.ilc_cluster_a_acceptance_evidence import validate_evidence_schema
    ev = build_cluster_a_acceptance_evidence(
        governance_record=mock_gov_record,
        apply_result=mock_apply_res,
        conformance_result=mock_conf_res
    )
    
    # 1. Invalid Check ID Type
    ev["constitution_checks"] = [{"check_id": 123, "status": "pass"}]
    errors = validate_evidence_schema(ev)
    assert "schema_violation:invalid_type_constitution_check_item_0_check_id" in errors
    
    # 2. Empty Check ID
    ev["constitution_checks"] = [{"check_id": "", "status": "pass"}]
    errors = validate_evidence_schema(ev)
    assert "schema_violation:invalid_length_constitution_check_item_0_check_id" in errors

    # 3. Invalid Status Value
    ev["constitution_checks"] = [{"check_id": "C1", "status": "maybe"}]
    errors = validate_evidence_schema(ev)
    assert "schema_violation:invalid_value_constitution_check_item_0_status" in errors

    # 4. Unknown Field in Item
    ev["constitution_checks"] = [{"check_id": "C1", "status": "pass", "unknown": "field"}]
    errors = validate_evidence_schema(ev)
    assert "schema_violation:unknown_field_constitution_check_item_0_unknown" in errors

    # 5. Missing Status
    ev["constitution_checks"] = [{"check_id": "C1"}]
    errors = validate_evidence_schema(ev)
    assert "schema_violation:missing_field_constitution_check_item_0_status" in errors

def test_validate_evidence_rejection_uid_length(mock_gov_record, mock_apply_res, mock_conf_res):
    from ilc_core.protocol.ilc_cluster_a_acceptance_evidence import validate_evidence_schema
    ev = build_cluster_a_acceptance_evidence(
        governance_record=mock_gov_record,
        apply_result=mock_apply_res,
        conformance_result=mock_conf_res
    )
    
    ev["record_uid"] = ""
    errors = validate_evidence_schema(ev)
    assert "schema_violation:invalid_length_record_uid" in errors

def test_validate_evidence_rejection_bad_check_status_legacy(mock_gov_record, mock_apply_res, mock_conf_res):
    from ilc_core.protocol.ilc_cluster_a_acceptance_evidence import validate_evidence_schema
    ev = build_cluster_a_acceptance_evidence(
        governance_record=mock_gov_record,
        apply_result=mock_apply_res,
        conformance_result=mock_conf_res
    )
    
    # 1. Warn (removed)
    ev["constitution_checks"] = [{"check_id": "C1", "status": "warn"}]
    errors = validate_evidence_schema(ev)
    assert "schema_violation:invalid_value_constitution_check_item_0_status" in errors
    
    # 2. Skip (removed)
    ev["constitution_checks"] = [{"check_id": "C1", "status": "skip"}]
    errors = validate_evidence_schema(ev)
    assert "schema_violation:invalid_value_constitution_check_item_0_status" in errors
    
    # 3. Not Applicable (Valid)
    ev["constitution_checks"] = [{"check_id": "C1", "status": "not_applicable"}]
    errors = validate_evidence_schema(ev)
    assert errors == []

