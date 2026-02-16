"""
ILC Constitution Cluster A - Clause Binding Engine.
Phase 140.

Provides deterministic mapping of abstract constitutional requirements (CONST-*)
to executable runtime checks.
"""

from typing import Any, Dict, List, Optional
import enum

from ilc_core.exceptions import ClauseBindingValidationError

# --- Constants ---

class CheckStatus(str, enum.Enum):
    PASS = "pass"
    FAIL = "fail"
    NOT_APPLICABLE = "not_applicable"

REQUIRED_CHECKS = ["CONST-001", "CONST-002", "CONST-003", "CONST-004"]

def _normalize_checks(checks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize check list: unique check_id, sorted by check_id.
    """
    unique = {}
    for c in checks:
        cid = c["check_id"]
        # Last write wins? Or first? Let's use first to be safe, or just enforce uniqueness.
        if cid not in unique:
            unique[cid] = c
            
    return [unique[k] for k in sorted(unique.keys())]

def _validate_check_shape(c: Dict[str, Any]) -> None:
    """
    Enforce strict shape and status enum.
    """
    if "check_id" not in c:
        raise ClauseBindingValidationError("missing_check_id")
    if c.get("status") not in [s.value for s in CheckStatus]:
        raise ClauseBindingValidationError(f"invalid_check_status:{c.get('status')}")

def _result(check_id: str, status: CheckStatus, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    res = {
        "check_id": check_id,
        "status": status.value,
        "error_code": error_code,
        "details": details
    }
    _validate_check_shape(res)
    return res

# --- Check Implementations ---

def _eval_const_001(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    CONST-001: Deterministic Envelope & Ordering.
    Verified if ingest phase passed without schema violations.
    """
    ingest_ok = context.get("ingest_ok", False)
    # If ingest is OK, schema is valid strict envelope.
    # If ingest failed due to schema, this fails.
    if ingest_ok:
        return _result("CONST-001", CheckStatus.PASS)
    
    # Check if failure was schema related
    errors = context.get("all_errors", [])
    if any("schema_violation" in e or "invalid_json" in e for e in errors):
         return _result("CONST-001", CheckStatus.FAIL, "context_violation:non_deterministic_envelope")
    
    # If ingest failed for other reasons (like file not found), technically envelope didn't pass,
    # but maybe N/A? Let's stick to fail if we rely on envelope.
    return _result("CONST-001", CheckStatus.FAIL, "context_violation:non_deterministic_envelope")

def _eval_const_002(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    CONST-002: Identity Binding & Replay Resistance.
    Verified if binding values (hash, epoch, window) are structurally valid.
    """
    # Assuming "binding_valid" boolean in context, derived from val_errors + struct_errors
    binding_valid = context.get("binding_valid", False)
    
    if binding_valid:
        return _result("CONST-002", CheckStatus.PASS)
    
    return _result("CONST-002", CheckStatus.FAIL, "context_violation:identity_binding_invariant_failed")

def _eval_const_003(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    CONST-003: Signature/Context Integrity.
    Verified if the *expected* context matches the *bound* context.
    """
    # Assuming "context_match" boolean in context
    context_match = context.get("context_match", False)
    
    if context_match:
         return _result("CONST-003", CheckStatus.PASS)
         
    return _result("CONST-003", CheckStatus.FAIL, "context_violation:signature_context_invariant_failed")

def _eval_const_004(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    CONST-004: Policy-Bound Conformance Check Path Active.
    Meta-check: verifies that binding expectations were actually provided/checked.
    """
    expectations_provided = context.get("expectations_provided", False)
    
    # If we are checking conformance without expectations, we are not strictly "policy bound"
    # in the sense of enforcing a specific governance state context.
    # However, if expectations were NOT provided, we might be in a loose check mode.
    # CONST-004 requires that we ARE performing a policy-bound check for the acceptance path.
    
    if expectations_provided:
        return _result("CONST-004", CheckStatus.PASS)
        
    # If no expectations provided, we are just looking at the artifact in isolation.
    # The prompt says: "CONST-004 -> policy-bound conformance check path active"
    # Fail code: context_violation:policy_bound_check_invariant_failed
    
    # Implementation decision: If expectations are missing, is it a FAIL or N/A?
    # For "Acceptance Integrity", we REQUIRE the acceptance path to define the policy.
    # So if we run this without expectations, we fail this invariant for *Acceptance* purposes.
    
    return _result("CONST-004", CheckStatus.FAIL, "context_violation:policy_bound_check_invariant_failed")


# --- Main Entrypoint ---

def evaluate_cluster_a_constitution_checks(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return deterministic check results for configured CONST-* subset.
    
    Context expected keys:
    - ingest_ok: bool
    - binding_valid: bool (values + structure)
    - context_match: bool
    - expectations_provided: bool
    - all_errors: List[str]
    """
    
    raw_checks = [
        _eval_const_001(context),
        _eval_const_002(context),
        _eval_const_003(context),
        _eval_const_004(context),
    ]
    
    checks = _normalize_checks(raw_checks)
    
    failed_required = [
        c for c in checks 
        if c["check_id"] in REQUIRED_CHECKS and c["status"] == CheckStatus.FAIL.value
    ]
    
    errors = sorted(list({c["error_code"] for c in failed_required if c.get("error_code")}))
    
    return {
        "ok": len(failed_required) == 0,
        "version": "v0.1",
        "required_check_ids": sorted(REQUIRED_CHECKS),
        "checks": checks,
        "errors": errors,
        "warnings": [],
    }
