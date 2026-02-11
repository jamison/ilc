"""
ILC Constitution Cluster A - Acceptance Evidence Artifact Builder.
Phase 141.

Provides deterministic evidence generation for governance acceptance decisions.
"""

import datetime
from typing import Any, Dict, List, Optional

from ilc_core.protocol.ilc_cluster_a_ingest import canonical_governance_record_digest
import re
import json
import hashlib




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
    Validate evidence against the JSON schema strictly.
    Enforces types, formats, and no extraneous fields.
    Returns sorted list of deterministic error tokens.
    """
    errors = []
    
    # 0. Root Type
    if not isinstance(evidence, dict):
        return ["schema_violation:evidence_not_dict"]

    # 1. Unknown Fields (additionalProperties: false)
    ALLOWED_KEYS = {
        "artifact_kind", "artifact_version", "record_uid", "record_hash_sha256",
        "transcript_hash_sha256", "conformance_ok", "constitution_checks",
        "accepted", "acceptance_errors", "acceptance_warnings",
        "policy_state_delta", "generated_at"
    }
    
    present_keys = set(evidence.keys())
    unknown_keys = present_keys - ALLOWED_KEYS
    for k in sorted(unknown_keys):
        errors.append(f"schema_violation:unknown_field_{k}")

    # 2. Required Fields
    REQUIRED_KEYS = {
        "artifact_kind", "artifact_version", "record_uid", "record_hash_sha256",
        "generated_at", "accepted", "conformance_ok", 
        "acceptance_errors", "acceptance_warnings", "constitution_checks"
    }
    missing_keys = REQUIRED_KEYS - present_keys
    for k in sorted(missing_keys):
        errors.append(f"schema_violation:missing_field_{k}")
        
    # 3. Value Validation (for present fields)
    
    # Constant Checks
    if "artifact_kind" in evidence and evidence["artifact_kind"] != "cluster_a_acceptance_evidence":
        errors.append("schema_violation:invalid_kind")
    if "artifact_version" in evidence and evidence["artifact_version"] != "v0.1":
        errors.append("schema_violation:invalid_version")
        
    # UID
    if "record_uid" in evidence:
        uid = evidence["record_uid"]
        if not isinstance(uid, str):
            errors.append("schema_violation:invalid_type_record_uid")
        elif len(uid) < 1:
            errors.append("schema_violation:invalid_length_record_uid")
        
    # Hash Format (SHA-256 hex)
    sha256_pattern = re.compile(r"^[a-f0-9]{64}$")
    
    if "record_hash_sha256" in evidence:
        val = evidence["record_hash_sha256"]
        if not isinstance(val, str):
            errors.append("schema_violation:invalid_type_record_hash_sha256")
        elif not sha256_pattern.match(val):
            errors.append("schema_violation:invalid_format_record_hash_sha256")
            
    if "transcript_hash_sha256" in evidence:
        val = evidence["transcript_hash_sha256"]
        if val is not None:
             if not isinstance(val, str):
                 errors.append("schema_violation:invalid_type_transcript_hash_sha256")
             elif not sha256_pattern.match(val):
                 errors.append("schema_violation:invalid_format_transcript_hash_sha256")
                 
    # Booleans
    for f in ["accepted", "conformance_ok"]:
        if f in evidence and not isinstance(evidence[f], bool):
            errors.append(f"schema_violation:invalid_type_{f}")
            
    # Lists of Strings
    for f in ["acceptance_errors", "acceptance_warnings"]:
        if f in evidence:
            val = evidence[f]
            if not isinstance(val, list):
                errors.append(f"schema_violation:invalid_type_{f}")
            else:
                for i, item in enumerate(val):
                    if not isinstance(item, str):
                        errors.append(f"schema_violation:invalid_item_type_{f}")
                        break

    # Constitution Checks
    if "constitution_checks" in evidence:
        val = evidence["constitution_checks"]
        if not isinstance(val, list):
            errors.append("schema_violation:invalid_type_constitution_checks")
        else:
            ALLOWED_ITEM_KEYS = {"check_id", "status", "error_code", "details"}
            REQUIRED_ITEM_KEYS = {"check_id", "status"}
            
            for i, item in enumerate(val):
                if not isinstance(item, dict):
                    errors.append(f"schema_violation:invalid_type_constitution_check_item_{i}")
                    continue
                
                # Unknown keys
                item_keys = set(item.keys())
                unknown_item_keys = item_keys - ALLOWED_ITEM_KEYS
                for k in sorted(unknown_item_keys):
                    errors.append(f"schema_violation:unknown_field_constitution_check_item_{i}_{k}")
                    
                # Required keys
                missing_item_keys = REQUIRED_ITEM_KEYS - item_keys
                for k in sorted(missing_item_keys):
                    errors.append(f"schema_violation:missing_field_constitution_check_item_{i}_{k}")
                    
                # check_id validation
                if "check_id" in item:
                    cid = item["check_id"]
                    if not isinstance(cid, str):
                        errors.append(f"schema_violation:invalid_type_constitution_check_item_{i}_check_id")
                    elif len(cid) < 1:
                        errors.append(f"schema_violation:invalid_length_constitution_check_item_{i}_check_id")
                
                # status validation
                if "status" in item:
                    status = item["status"]
                    if status not in {"pass", "fail", "not_applicable"}:
                        # Note: 'not_applicable' added based on implementation plan/prompt update
                        # Prompt said: "pass, fail, not_applicable". Wait, let me check carefully.
                        # Prompt: "status must be exactly one of: pass, fail, not_applicable"
                        # But earlier code used "pass", "fail", "warn", "skip".
                        # Plan says: "enum: pass/fail/not_applicable".
                        # If I strictly follow plan, I might break existing code providing "warn" or "skip".
                        # I should probably allow "warn" and "skip" too if they are legacy, but plan says "exact".
                        # Let's check existing tests or logic.
                        # Test output earlier showed: "warn_c", "warn_a".
                        # Wait, those were warnings in 'acceptance_warnings', not check statuses.
                        # `constitution_checks` fixture in tests says: `[{"check_id": "CONST-002", "status": "pass"}]`.
                        # I will support "pass", "fail", "not_applicable" as per plan instructions.
                        # I will ADD "warn" and "skip" if safe, or stick to plan?
                        # Plan Anti-patterns: "Do not broaden accepted status enums (no warn/skip aliases in evidence contract logic)."
                        # Uh oh. Previous code had `{"pass", "fail", "warn", "skip"}`.
                        # The plan explicitly says "status must be exactly one of: pass, fail, not_applicable".
                        # This implies "warn" and "skip" are NOT allowed in the strict schema.
                        # I will follow the plan strictly.
                        errors.append(f"schema_violation:invalid_value_constitution_check_item_{i}_status")

                # error_code validation (nullable string)
                if "error_code" in item:
                    ec = item["error_code"]
                    if ec is not None and not isinstance(ec, str):
                         errors.append(f"schema_violation:invalid_type_constitution_check_item_{i}_error_code")
                         
                # details validation (nullable dict)
                if "details" in item:
                    dt = item["details"]
                    if dt is not None and not isinstance(dt, dict):
                         errors.append(f"schema_violation:invalid_type_constitution_check_item_{i}_details")

    # Timestamp
    if "generated_at" in evidence:
        val = evidence["generated_at"]
        if not isinstance(val, str):
            errors.append("schema_violation:invalid_type_generated_at")
        else:
            # Strict ISO 8601 UTC (ends in Z)
            # YYYY-MM-DDTHH:MM:SS.mmmmmmZ or YYYY-MM-DDTHH:MM:SSZ
            # Simple check:
            if not val.endswith("Z"):
                 errors.append("schema_violation:invalid_format_generated_at_utc_suffix")
            else:
                try:
                    # Validate parsing
                    # remove Z for fromisoformat if < 3.11, but explicit Z check is main gate
                    dt = datetime.datetime.fromisoformat(val.replace("Z", "+00:00"))
                except ValueError:
                    errors.append("schema_violation:invalid_format_generated_at_iso8601")

    # Policy Delta (Nullable Dict)
    if "policy_state_delta" in evidence:
        val = evidence["policy_state_delta"]
        if val is not None and not isinstance(val, dict):
            errors.append("schema_violation:invalid_type_policy_state_delta")

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
