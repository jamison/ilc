"""
ILC Constitution Cluster A - Replay Attestation Logic.
Phase 141.

Verifies that an acceptance evidence artifact is consistent with a 
re-computed execution of the governance logic against the original inputs.
"""

from typing import Any, Dict, List, Optional, Set
from ilc_core.protocol.ilc_cluster_a_ingest import canonical_governance_record_digest
from ilc_core.protocol.ilc_cluster_a_acceptance_evidence import (
    _sorted_unique_str, 
    _normalize_constitution_checks,
    validate_evidence_schema,
    canonical_evidence_contract_digest
)

# --- Failure Tokens ---
E_HASH_MISMATCH = "context_violation:evidence_record_hash_mismatch"
E_CONST_MISMATCH = "context_violation:evidence_constitution_checks_mismatch"
E_DECISION_MISMATCH = "context_violation:evidence_acceptance_decision_mismatch"
E_CONFORMANCE_MISMATCH = "context_violation:evidence_conformance_mismatch"
E_ERROR_SET_MISMATCH = "context_violation:evidence_error_set_mismatch"
E_WARNING_SET_MISMATCH = "context_violation:evidence_warning_set_mismatch"
E_CONTRACT_HASH_MISMATCH = "context_violation:evidence_contract_hash_mismatch"
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
    Attest that the provided evidence matches a re-execution of the logic.
    
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
    
    # 0. Schema Validation (Fail-Safe)
    # Uses the shared strict validator
    schema_errors = validate_evidence_schema(evidence)
    if schema_errors:
        # Schema failure is fatal to attestation logic but handled safely here.
        return {
            "ok": False,
            "errors": sorted(schema_errors),
            "warnings": [],
            "checks": [
                _emit_check("check_evidence_schema_valid", False, e) 
                for e in sorted(schema_errors)
            ],
        }
    checks.append(_emit_check("check_evidence_schema_valid", True))

    # 1. Check Record Hash
    # Recompute strictly
    recomputed_hash = canonical_governance_record_digest(governance_record)
    evidence_hash = evidence["record_hash_sha256"]
    hash_match = (recomputed_hash == evidence_hash)
    if not hash_match:
        errors.append(E_HASH_MISMATCH)
    checks.append(_emit_check("check_record_hash_match", hash_match, E_HASH_MISMATCH))

    # 2. Check Acceptance Decision
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

    # 7. Check Contract Hash Match (Canonical Digest)
    # We rebuild the evidence *as if* we were the builder, effectively recomputing the full artifact,
    # then compare the canonical digest of the input evidence vs our recomputed evidence.
    # This catches ANY deviation in the contract fields (which are 90% of the above, but hash check is absolute).
    
    # We can reuse the build function to get a 'clean' recomputed evidence object
    # passing the SAME governance record to get the same ID/Hash
    # but we need to match the timestamp if we want full equality?
    # Spec says "Canonical Hash Contract" excludes generated_at.
    # So we can just compare the digests!
    
    # Compute digest of the INPUT evidence
    input_digest = canonical_evidence_contract_digest(evidence)
    
    # Compute digest of the RECOMPUTED evidence
    # We manually build the dict for digest to avoid timestamp/metadata noise
    # OR we use the builder with the *input* timestamp if we wanted full check?
    # But digest excludes timestamp.
    
    # Let's construct the "recomputed" canonical subset directly from our recomputed vars
    recomputed_canonical = {
        "record_hash_sha256": recomputed_hash,
        "conformance_ok": conf_ok,
        "constitution_checks": re_checks,
        "accepted": recomputed_accepted,
        "acceptance_errors": recomputed_errors,
        "acceptance_warnings": recomputed_warns
    }
    
    # We can assume the input evidence has a digest that matches its own content (it's properties).
    # What we really want to check is if the input evidence's digest matches the recomputed digest.
    # Be careful: `canonical_evidence_contract_digest` takes a full evidence dict.
    # We can pass `recomputed_canonical` to it IF it handles missing metadata fields gracefully?
    # The function access specific keys. `recomputed_canonical` has them all.
    # So we can call it.
    
    # Note: `recomputed_canonical` must look like evidence for the digest fn.
    recomputed_digest = canonical_evidence_contract_digest(recomputed_canonical)
    
    contract_match = (input_digest == recomputed_digest)
    if not contract_match:
        # If specific fields matched but hash didn't, implies normalization/serialization diffs?
        # Or I missed a field above?
        errors.append(E_CONTRACT_HASH_MISMATCH)
        
    checks.append(_emit_check("check_contract_hash_match", contract_match, E_CONTRACT_HASH_MISMATCH))

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
