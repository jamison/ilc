"""
ILC Constitution Cluster A - Replay Attestation Logic.
Phase 141.

Verifies that an acceptance evidence artifact is consistent with a 
re-computed execution of the governance logic against the original inputs.
"""

from typing import Any, Dict, List, Optional, Set
from ilc_core.protocol.ilc_cluster_a_ingest import canonical_governance_record_digest
from ilc_core.protocol.ilc_cluster_a_acceptance_evidence import _sorted_unique_str, _normalize_constitution_checks

# --- Failure Tokens ---
E_HASH_MISMATCH = "context_violation:evidence_record_hash_mismatch"
E_CONST_MISMATCH = "context_violation:evidence_constitution_checks_mismatch"
E_DECISION_MISMATCH = "context_violation:evidence_acceptance_decision_mismatch"
E_CONFORMANCE_MISMATCH = "context_violation:evidence_conformance_mismatch"
E_ERROR_SET_MISMATCH = "context_violation:evidence_error_set_mismatch"
E_WARNING_SET_MISMATCH = "context_violation:evidence_warning_set_mismatch"
E_SCHEMA_INVALID = "schema_violation:invalid_acceptance_evidence_shape"
E_MISSING_FIELD = "schema_violation:evidence_missing_required_field"

def _emit_check(name: str, ok: bool, error_code: Optional[str] = None) -> Dict[str, Any]:
    return {
        "check": name,
        "status": "pass" if ok else "fail",
        "error_code": error_code if not ok else None,
    }

def attest_cluster_a_replay(
    *, 
    evidence: Dict[str, Any], 
    governance_record: Dict[str, Any], 
    apply_result: Dict[str, Any], 
    conformance_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Attest that the provided evidence matches a re-execution of logic.
    
    Args:
        evidence: The artifact to verify.
        governance_record: Original input record.
        apply_result: Re-run apply result.
        conformance_result: Re-run conformance result.
        
    Returns:
        Dict with "ok", "errors", "warnings", "checks".
    """
    errors: List[str] = []
    checks: List[Dict[str, Any]] = []
    
    # 0. Schema Check
    required_fields = {
        "record_hash_sha256", "conformance_ok", "constitution_checks", 
        "accepted", "acceptance_errors", "acceptance_warnings"
    }
    missing = [f for f in required_fields if f not in evidence]
    if missing:
        errors.append(E_MISSING_FIELD)
        return {
            "ok": False,
            "errors": sorted(errors),
            "warnings": [],
            "checks": [],
            "missing_fields": sorted(missing)
        }

    # 1. Check Record Hash
    # Recompute strictly
    recomputed_hash = canonical_governance_record_digest(governance_record)
    evidence_hash = evidence["record_hash_sha256"]
    hash_match = (recomputed_hash == evidence_hash)
    if not hash_match:
        errors.append(E_HASH_MISMATCH)
    checks.append(_emit_check("check_record_hash_match", hash_match, E_HASH_MISMATCH))

    # 2. Check Acceptance Decision
    # Recompute locally
    app_ok = apply_result.get("ok", False)
    conf_ok = conformance_result.get("ok", False)
    recomputed_accepted = app_ok and conf_ok
    evidence_accepted = evidence["accepted"]
    
    decision_match = (recomputed_accepted == evidence_accepted)
    if not decision_match:
        errors.append(E_DECISION_MISMATCH)
    checks.append(_emit_check("check_acceptance_decision_match", decision_match, E_DECISION_MISMATCH))

    # 3. Check Conformance Status
    conf_match = (conf_ok == evidence["conformance_ok"])
    if not conf_match:
        errors.append(E_CONFORMANCE_MISMATCH)
    checks.append(_emit_check("check_conformance_ok_match", conf_match, E_CONFORMANCE_MISMATCH))

    # 4. Check Constitution Checks (Deep Equality)
    # Normalize both sides to be safe against stable sort differences if any
    ev_checks = _normalize_constitution_checks(evidence["constitution_checks"])
    re_checks_raw = conformance_result.get("constitution_checks", {}).get("checks", [])
    if not isinstance(re_checks_raw, list):
        re_checks_raw = []
    re_checks = _normalize_constitution_checks(re_checks_raw)
    
    # Compare
    # Exact JSON equality of list of dicts is sufficient if normalized
    const_match = (ev_checks == re_checks)
    if not const_match:
        errors.append(E_CONST_MISMATCH)
    checks.append(_emit_check("check_constitution_checks_match", const_match, E_CONST_MISMATCH))

    # 5. Check Error Sets
    app_errs = apply_result.get("errors", [])
    conf_errs = conformance_result.get("errors", [])
    recomputed_errors = _sorted_unique_str(app_errs + conf_errs)
    evidence_errors = _sorted_unique_str(evidence["acceptance_errors"])
    
    err_match = (recomputed_errors == evidence_errors)
    if not err_match:
        errors.append(E_ERROR_SET_MISMATCH)
    checks.append(_emit_check("check_error_sets_match", err_match, E_ERROR_SET_MISMATCH))

    # 6. Check Warning Sets
    app_warns = apply_result.get("warnings", [])
    conf_warns = conformance_result.get("warnings", [])
    recomputed_warns = _sorted_unique_str(app_warns + conf_warns)
    evidence_warns = _sorted_unique_str(evidence["acceptance_warnings"])
    
    warn_match = (recomputed_warns == evidence_warns)
    if not warn_match:
        errors.append(E_WARNING_SET_MISMATCH)
    checks.append(_emit_check("check_warning_sets_match", warn_match, E_WARNING_SET_MISMATCH))

    # Final Result
    is_ok = (len(errors) == 0)
    
    # Sort errors
    errors.sort()
    
    return {
        "ok": is_ok,
        "errors": errors,
        "warnings": [],
        "checks": checks,
    }
