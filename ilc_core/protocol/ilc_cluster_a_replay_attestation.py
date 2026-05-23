# SPDX-License-Identifier: AGPL-3.0-or-later
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


def _emit_schema_failure(schema_errors: List[str]) -> Dict[str, Any]:
    ordered = sorted(schema_errors)
    return {
        "ok": False,
        "errors": ordered,
        "warnings": [],
        "checks": [_emit_check("check_evidence_schema_valid", False, err) for err in ordered],
    }


def _record_check(
    checks: List[Dict[str, Any]],
    errors: List[str],
    name: str,
    is_ok: bool,
    token: str,
) -> None:
    if not is_ok:
        errors.append(token)
    checks.append(_emit_check(name, is_ok, token))


def _extract_recomputed_constitution_checks(conformance_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    raw_checks = conformance_result.get("constitution_checks", {}).get("checks", [])
    if not isinstance(raw_checks, list):
        raw_checks = []
    return _normalize_constitution_checks(raw_checks)


def _build_recomputed_canonical_payload(
    recomputed_hash: str,
    conformance_ok: bool,
    constitution_checks: List[Dict[str, Any]],
    accepted: bool,
    acceptance_errors: List[str],
    acceptance_warnings: List[str],
) -> Dict[str, Any]:
    return {
        "record_hash_sha256": recomputed_hash,
        "conformance_ok": conformance_ok,
        "constitution_checks": constitution_checks,
        "accepted": accepted,
        "acceptance_errors": acceptance_errors,
        "acceptance_warnings": acceptance_warnings,
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

    schema_errors = validate_evidence_schema(evidence)
    if schema_errors:
        return _emit_schema_failure(schema_errors)
    checks.append(_emit_check("check_evidence_schema_valid", True))

    recomputed_hash = canonical_governance_record_digest(governance_record)
    _record_check(
        checks,
        errors,
        "check_record_hash_match",
        recomputed_hash == evidence["record_hash_sha256"],
        E_HASH_MISMATCH,
    )

    app_ok = apply_result.get("ok", False)
    conf_ok = conformance_result.get("ok", False)
    recomputed_accepted = app_ok and conf_ok
    _record_check(
        checks,
        errors,
        "check_acceptance_decision_match",
        recomputed_accepted == evidence["accepted"],
        E_DECISION_MISMATCH,
    )
    _record_check(
        checks,
        errors,
        "check_conformance_ok_match",
        conf_ok == evidence["conformance_ok"],
        E_CONFORMANCE_MISMATCH,
    )

    ev_checks = _normalize_constitution_checks(evidence["constitution_checks"])
    re_checks = _extract_recomputed_constitution_checks(conformance_result)
    _record_check(
        checks,
        errors,
        "check_constitution_checks_match",
        ev_checks == re_checks,
        E_CONST_MISMATCH,
    )

    recomputed_errors = _sorted_unique_str(
        apply_result.get("errors", []) + conformance_result.get("errors", [])
    )
    evidence_errors = _sorted_unique_str(evidence["acceptance_errors"])
    _record_check(
        checks,
        errors,
        "check_error_sets_match",
        recomputed_errors == evidence_errors,
        E_ERROR_SET_MISMATCH,
    )

    recomputed_warns = _sorted_unique_str(
        apply_result.get("warnings", []) + conformance_result.get("warnings", [])
    )
    evidence_warns = _sorted_unique_str(evidence["acceptance_warnings"])
    _record_check(
        checks,
        errors,
        "check_warning_sets_match",
        recomputed_warns == evidence_warns,
        E_WARNING_SET_MISMATCH,
    )

    input_digest = canonical_evidence_contract_digest(evidence)
    recomputed_canonical = _build_recomputed_canonical_payload(
        recomputed_hash=recomputed_hash,
        conformance_ok=conf_ok,
        constitution_checks=re_checks,
        accepted=recomputed_accepted,
        acceptance_errors=recomputed_errors,
        acceptance_warnings=recomputed_warns,
    )
    recomputed_digest = canonical_evidence_contract_digest(recomputed_canonical)
    _record_check(
        checks,
        errors,
        "check_contract_hash_match",
        input_digest == recomputed_digest,
        E_CONTRACT_HASH_MISMATCH,
    )

    errors.sort()

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": [],
        "checks": checks,
    }
