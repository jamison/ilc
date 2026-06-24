
import pytest
from ilc_core.protocol.ilc_cluster_a_acceptance_evidence import (
    validate_evidence_schema,
    canonical_evidence_contract_digest,
    build_cluster_a_acceptance_evidence
)

@pytest.fixture
def valid_evidence():
    return {
        "artifact_kind": "cluster_a_acceptance_evidence",
        "artifact_version": "v0.1",
        "record_uid": "rec_001",
        "record_hash_sha256": "a" * 64,
        "transcript_hash_sha256": None,
        "generated_at": "2025-01-01T12:00:00Z",
        "accepted": True,
        "conformance_ok": True,
        "acceptance_errors": [],
        "acceptance_warnings": [],
        "constitution_checks": [
            {"check_id": "C1", "status": "pass"},
            {"check_id": "C2", "status": "fail", "error_code": "E1"}
        ],
        "policy_state_delta": None
    }

def test_validate_schema_valid_sample(valid_evidence):
    errors = validate_evidence_schema(valid_evidence)
    assert errors == []

def test_validate_schema_missing_field(valid_evidence):
    del valid_evidence["record_uid"]
    errors = validate_evidence_schema(valid_evidence)
    assert "schema_violation:missing_field_record_uid" in errors

def test_validate_schema_invalid_types(valid_evidence):
    valid_evidence["accepted"] = "yes"
    errors = validate_evidence_schema(valid_evidence)
    assert "schema_violation:invalid_type_accepted" in errors

def test_validate_schema_invalid_const_check(valid_evidence):
    # Invalid item in list
    valid_evidence["constitution_checks"].append({"check_id": "C3"}) # missing status
    errors = validate_evidence_schema(valid_evidence)
    # Index is implementation-dependent; assert canonical missing-field token shape.
    assert any(
        e.startswith("schema_violation:missing_field_constitution_check_item_")
        and e.endswith("_status")
        for e in errors
    )

def test_canonical_digest_stability(valid_evidence):
    # Digest should be stable
    d1 = canonical_evidence_contract_digest(valid_evidence)
    d2 = canonical_evidence_contract_digest(valid_evidence)
    assert d1 == d2
    assert len(d1) == 64

def test_canonical_digest_excludes_metadata(valid_evidence):
    d1 = canonical_evidence_contract_digest(valid_evidence)
    
    # Change timestamp - generated_at is EXCLUDED
    valid_evidence["generated_at"] = "2099-01-01T12:00:00Z"
    d2 = canonical_evidence_contract_digest(valid_evidence)
    
    assert d1 == d2

def test_canonical_digest_includes_contract_fields(valid_evidence):
    d1 = canonical_evidence_contract_digest(valid_evidence)
    
    # Change acceptance - INCLUDED
    valid_evidence["accepted"] = False
    d2 = canonical_evidence_contract_digest(valid_evidence)
    
    assert d1 != d2


def test_canonical_digest_rejects_non_finite_contract_values(valid_evidence):
    valid_evidence["constitution_checks"][0]["details"] = {"score": float("nan")}

    with pytest.raises(ValueError, match="Out of range float values"):
        canonical_evidence_contract_digest(valid_evidence)


def test_builder_enforces_schema():
    # Helper to test builder raises on bad schema if we were to somehow inject junk
    # But builder is typed and controlled. 
    # We can test that builder output PASSES schema.
    
    gov_rec = {"gov_record_id": "rec_1", "payload": "abc"}
    apply_res = {"ok": True}
    conf_res = {"ok": True, "constitution_checks": {"checks": []}}
    
    ev = build_cluster_a_acceptance_evidence(
        governance_record=gov_rec,
        apply_result=apply_res,
        conformance_result=conf_res
    )
    
    assert validate_evidence_schema(ev) == []
