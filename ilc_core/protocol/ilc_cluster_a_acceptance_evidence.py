"""
ILC Constitution Cluster A - Acceptance Evidence Artifact Builder.
Phase 141.

Provides deterministic evidence generation for governance acceptance decisions.
"""

import datetime
from typing import Any, Dict, List, Optional

from ilc_core.protocol.ilc_cluster_a_ingest import canonical_governance_record_digest

def _sorted_unique_str(values: Optional[List[str]]) -> List[str]:
    """Return sorted unique list of strings. Raises TypeError if values contains non-strings."""
    if not values:
        return []
        
    if not isinstance(values, list):
         raise TypeError("Values must be a list")
         
    for v in values:
        if not isinstance(v, str):
            raise TypeError(f"List must contain only strings, found {type(v)}")
            
    return sorted(list(set(values)))

def _normalize_constitution_checks(checks: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Normalize constitution checks list:
    - Deduplicate by check_id (last wins or stable? Logic says unique check_ids usually).
    - Sort locally by check_id.
    """
    if not checks:
        return []
        
    unique = {}
    # Preserving order of occurrence for dedup if duplicates exist, but we sort at end.
    for c in checks:
        cid = c.get("check_id")
        if isinstance(cid, str):
            unique[cid] = c
            
    # Deterministic sort by check_id
    return [unique[k] for k in sorted(unique.keys())]

def build_cluster_a_acceptance_evidence(
    *, 
    governance_record: Dict[str, Any], 
    apply_result: Dict[str, Any], 
    conformance_result: Dict[str, Any], 
    runtime_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Build a deterministic acceptance evidence artifact.
    
    Args:
        governance_record: The raw input record.
        apply_result: Result from apply_governance_record.
        conformance_result: Result from conformance_check_cluster_a_artifact.
        runtime_context: Optional context containing "timestamp" (ISO-8601). 
                        If missing, strict UTC now is used.

    Returns:
        Deterministic dictionary representing the evidence artifact.
    """
    
    # 1. Resolve Timestamp
    # Use context timestamp if valid, else strictly generated now-time.
    to_use_ts = None
    if runtime_context and "timestamp" in runtime_context:
        ctx_ts = runtime_context["timestamp"]
        # Strict ISO-8601 UTC format check (must end in Z)
        # Regex: YYYY-MM-DDTHH:MM:SS.mmmmmmZ or similar.
        # Minimalist check: must be string, must end in 'Z', and parseable.
        if not isinstance(ctx_ts, str) or not ctx_ts.endswith("Z"):
             raise ValueError("runtime_context['timestamp'] must be a strict ISO-8601 UTC string ending in 'Z'")
        to_use_ts = ctx_ts
        
    if not to_use_ts:
        # Strict UTC ISO-8601
        to_use_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if not to_use_ts.endswith("Z"):
            # Ensure Z suffix behavior for python < 3.11 if needed, 
            # though isoformat() with timezone.utc usually adds +00:00.
            # We enforce Z for consistency with spec.
            to_use_ts = to_use_ts.replace("+00:00", "Z")

    # 2. Derive Identity & Hash
    record_uid = governance_record.get("gov_record_id")
    # Strict reliance on ingest logic for canonical hash
    record_hash = canonical_governance_record_digest(governance_record)

    # 3. Decision Logic
    # Acceptance requires both apply and conformance to be OK.
    # We rely on the caller to have made the final decision, but here we synthesize
    # the evidence based on the passed results.
    # Usually, if apply_result["ok"] AND conformance_result["ok"], then accepted=True.
    app_ok = apply_result.get("ok", False)
    conf_ok = conformance_result.get("ok", False)
    accepted = app_ok and conf_ok

    # 4. Collect Errors/Warnings (Sorted Unique)
    app_errs = apply_result.get("errors", [])
    conf_errs = conformance_result.get("errors", [])
    all_errors = _sorted_unique_str(app_errs + conf_errs)
    
    app_warns = apply_result.get("warnings", [])
    conf_warns = conformance_result.get("warnings", [])
    all_warnings = _sorted_unique_str(app_warns + conf_warns)

    # 5. Extract Constitution Checks
    # Usually in conformance_result["constitution_checks"]["checks"]
    const_checks_block = conformance_result.get("constitution_checks", {})
    raw_checks = const_checks_block.get("checks", []) if isinstance(const_checks_block, dict) else []
    
    # Flatten if needed or just normalize.
    # Existing structure from Phase 140 is list of dicts.
    normalized_checks = _normalize_constitution_checks(raw_checks)

    # 6. Extract Delta
    # apply_result["data"]["policy_state_delta"] if present
    policy_delta = None
    app_data = apply_result.get("data")
    if app_data and isinstance(app_data, dict):
        policy_delta = app_data.get("policy_state_delta")

    # 7. Build Artifact
    return {
        "artifact_kind": "cluster_a_acceptance_evidence",
        "artifact_version": "v0.1",
        "record_uid": record_uid,
        "record_hash_sha256": record_hash,
        "transcript_hash_sha256": None, # Future scope or from context if needed
        "conformance_ok": conf_ok,
        "constitution_checks": normalized_checks,
        "accepted": accepted,
        "acceptance_errors": all_errors,
        "acceptance_warnings": all_warnings,
        "policy_state_delta": policy_delta, # Can be None/null
        "generated_at": to_use_ts,
    }
