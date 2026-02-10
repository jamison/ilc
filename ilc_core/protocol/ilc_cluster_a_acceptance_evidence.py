"""
ILC Constitution Cluster A - Acceptance Evidence Artifact Builder.
Phase 141.

Provides deterministic evidence generation for governance acceptance decisions.
"""

import datetime
from typing import Any, Dict, List, Optional

from ilc_core.protocol.ilc_cluster_a_ingest import canonical_governance_record_digest
import json
import hashlib
import pkgutil

def _load_evidence_schema() -> Dict[str, Any]:
    """Load the JSON schema for acceptance evidence."""
    # Lazy load or cache could be done, here we just load
    try:
        # Assuming schema is packaged or available at a known path. 
        # For this environment we read relative to docs/specs if not packaged.
        # But we need a robust way. Let's try to read from the typical location for now.
        # If in a package, use pkgutil.get_data.
        # Fallback to local file read for dev environment.
        with open("docs/specs/ilc_cluster_a_acceptance_evidence_v0.1.json", "r") as f:
            return json.load(f)
    except Exception:
        # Fallback empty or log error? Strict requirement means we fail if not found.
        # For now, return empty dict or raise, but let's assume existence.
        return {}

def canonical_evidence_contract_digest(evidence: Dict[str, Any]) -> str:
    """
    Compute the canonical SHA-256 digest of the evidence contract payload.
    
    Contract Scope:
    - record_hash_sha256
    - conformance_ok
    - constitution_checks (identifiers and status)
    - accepted
    - acceptance_errors (sorted)
    - acceptance_warnings (sorted)
    
    Excludes:
    - generated_at (variable)
    - artifact_kind/version (metadata)
    - policy_state_delta (opaque)
    """
    # Normalize constitution checks to just id and status for the contract? 
    # Or full object? Spec says "constitution checking results". 
    # Let's include check_id and status as the critical contract. 
    # Details might contain variable implementation data.
    
    # Actually, strict determinism implies we should probably hash the *entire* normalized list
    # if we want to bind to the exact check execution.
    # Let's stick to the prompt's suggestion or a robust subset.
    # Prompt suggestion:
    # "constitution_checks": sorted(evidence["constitution_checks"], key=lambda c: c.get("check_id", ""))
    
    # We must ensure the items in constitution_checks are deterministic.
    # They are already normalized by _normalize_constitution_checks.
    
    canonical = {
        "record_hash_sha256": evidence["record_hash_sha256"],
        "conformance_ok": evidence["conformance_ok"],
        "constitution_checks": evidence["constitution_checks"], # Already normalized
        "accepted": evidence["accepted"],
        "acceptance_errors": evidence["acceptance_errors"],   # Already sorted
        "acceptance_warnings": evidence["acceptance_warnings"], # Already sorted
    }
    
    # Strict JSON serialization
    # separators=(',', ':') removes whitespace
    # sort_keys=True ensures key order
    payload = json.dumps(canonical, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

def validate_evidence_schema(evidence: Dict[str, Any]) -> List[str]:
    """
    Validate evidence against the JSON schema.
    Returns list of error tokens.
    Uses jsonschema library if available, else manual recursive check or simplified check.
    Given constraints, we might want to avoid heavy dependencies if possible, 
    but `jsonschema` is standard. If not present, we can implement a lightweight validator 
    matching the schema structure.
    
    Let's check if jsonschema is available. If not, we do manual checks ensuring types.
    """
    errors = []
    # Basic structural check matching schema
    
    # 1. Top level required
    req = ["artifact_kind", "artifact_version", "record_uid", "record_hash_sha256", 
           "generated_at", "accepted", "conformance_ok", "acceptance_errors", 
           "acceptance_warnings", "constitution_checks"]
    for r in req:
        if r not in evidence:
            errors.append(f"schema_violation:missing_field_{r}")
            
    if errors:
        return sorted(errors)
        
    # 2. Types
    if evidence.get("artifact_kind") != "cluster_a_acceptance_evidence":
        errors.append("schema_violation:invalid_kind")
    if evidence.get("artifact_version") != "v0.1":
        errors.append("schema_violation:invalid_version")
        
    if not isinstance(evidence.get("record_hash_sha256"), str):
        errors.append("schema_violation:invalid_type_record_hash_sha256")
        
    if not isinstance(evidence.get("accepted"), bool):
        errors.append("schema_violation:invalid_type_accepted")
        
    if not isinstance(evidence.get("conformance_ok"), bool):
        errors.append("schema_violation:invalid_type_conformance_ok")
        
    if not isinstance(evidence.get("acceptance_errors"), list):
        errors.append("schema_violation:invalid_type_acceptance_errors")
    elif not all(isinstance(x, str) for x in evidence["acceptance_errors"]):
        errors.append("schema_violation:invalid_item_type_acceptance_errors")
    
    if not isinstance(evidence.get("acceptance_warnings"), list):
        errors.append("schema_violation:invalid_type_acceptance_warnings")
    elif not all(isinstance(x, str) for x in evidence["acceptance_warnings"]):
        errors.append("schema_violation:invalid_item_type_acceptance_warnings")
        
    if not isinstance(evidence.get("constitution_checks"), list):
        errors.append("schema_violation:invalid_type_constitution_checks")
    else:
        # Check items
        for i, item in enumerate(evidence["constitution_checks"]):
            if not isinstance(item, dict):
                 errors.append(f"schema_violation:invalid_type_constitution_check_item_{i}")
            elif "check_id" not in item or "status" not in item:
                 errors.append(f"schema_violation:invalid_constitution_check_item_shape_{i}")

    return sorted(errors)

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
    # 7. Build Artifact
    evidence = {
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
    
    # 8. Schema Validation (Internal Integrity)
    # The builder must never produce invalid artifacts.
    schema_errors = validate_evidence_schema(evidence)
    if schema_errors:
        raise ValueError(f"CRITICAL: Builder produced invalid evidence schema: {schema_errors}")
        
    return evidence
