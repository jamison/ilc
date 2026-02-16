import pytest
from ilc_core.exceptions import ClauseBindingValidationError
from ilc_core.protocol.ilc_cluster_a_clause_binding import (
    evaluate_cluster_a_constitution_checks,
    CheckStatus,
    REQUIRED_CHECKS,
    _validate_check_shape,
)

def test_binding_perfect_pass():
    """Verify all checks pass when context is perfect."""
    ctx = {
        "ingest_ok": True,
        "binding_valid": True,
        "context_match": True,
        "expectations_provided": True,
        "all_errors": []
    }
    res = evaluate_cluster_a_constitution_checks(ctx)
    assert res["ok"] is True
    assert len(res["errors"]) == 0
    assert len(res["checks"]) == 4
    for c in res["checks"]:
        assert c["status"] == "pass"

def test_const_001_fail_envelope():
    """CONST-001 fails if ingest failed with schema error."""
    ctx = {
        "ingest_ok": False,
        "binding_valid": True,
        "context_match": True,
        "expectations_provided": True,
        "all_errors": ["schema_violation:root"]
    }
    res = evaluate_cluster_a_constitution_checks(ctx)
    assert res["ok"] is False
    assert "context_violation:non_deterministic_envelope" in res["errors"]
    c001 = next(c for c in res["checks"] if c["check_id"] == "CONST-001")
    assert c001["status"] == "fail"

def test_const_002_fail_binding():
    """CONST-002 fails if binding is invalid."""
    ctx = {
        "ingest_ok": True,
        "binding_valid": False,
        "context_match": True,
        "expectations_provided": True,
        "all_errors": ["value_violation:invalid_policy_hash"]
    }
    res = evaluate_cluster_a_constitution_checks(ctx)
    assert res["ok"] is False
    assert "context_violation:identity_binding_invariant_failed" in res["errors"]
    c002 = next(c for c in res["checks"] if c["check_id"] == "CONST-002")
    assert c002["status"] == "fail"

def test_const_003_fail_context():
    """CONST-003 fails if context mismatch."""
    ctx = {
        "ingest_ok": True,
        "binding_valid": True,
        "context_match": False,
        "expectations_provided": True,
        "all_errors": ["context_violation:policy_hash_mismatch"]
    }
    res = evaluate_cluster_a_constitution_checks(ctx)
    assert res["ok"] is False
    assert "context_violation:signature_context_invariant_failed" in res["errors"]
    c003 = next(c for c in res["checks"] if c["check_id"] == "CONST-003")
    assert c003["status"] == "fail"

def test_const_004_fail_no_expectations():
    """CONST-004 fails if no expectations provided (not policy bound)."""
    ctx = {
        "ingest_ok": True,
        "binding_valid": True,
        "context_match": True,
        "expectations_provided": False,
        "all_errors": []
    }
    res = evaluate_cluster_a_constitution_checks(ctx)
    assert res["ok"] is False
    assert "context_violation:policy_bound_check_invariant_failed" in res["errors"]
    c004 = next(c for c in res["checks"] if c["check_id"] == "CONST-004")
    assert c004["status"] == "fail"

def test_check_determinism():
    """Verify check list is sorted and unique."""
    ctx = {
        "ingest_ok": True,
        "binding_valid": True,
        "context_match": True,
        "expectations_provided": True,
        "all_errors": []
    }
    res = evaluate_cluster_a_constitution_checks(ctx)
    ids = [c["check_id"] for c in res["checks"]]
    assert ids == sorted(ids)
    assert len(ids) == len(set(ids))

def test_required_checks_present():
    """Verify all logic-required checks are in the output."""
    ctx = {
        "ingest_ok": True,
        "binding_valid": True,
        "context_match": True,
        "expectations_provided": True,
        "all_errors": []
    }
    res = evaluate_cluster_a_constitution_checks(ctx)
    ids = {c["check_id"] for c in res["checks"]}
    assert set(REQUIRED_CHECKS).issubset(ids)


def test_check_shape_raises_clause_binding_validation_error():
    with pytest.raises(ClauseBindingValidationError, match="missing_check_id"):
        _validate_check_shape({"status": "pass"})
