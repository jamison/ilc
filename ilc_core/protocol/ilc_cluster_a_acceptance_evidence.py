# SPDX-License-Identifier: AGPL-3.0-only
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


_ALLOWED_EVIDENCE_KEYS = {
    "artifact_kind",
    "artifact_version",
    "record_uid",
    "record_hash_sha256",
    "transcript_hash_sha256",
    "conformance_ok",
    "constitution_checks",
    "accepted",
    "acceptance_errors",
    "acceptance_warnings",
    "policy_state_delta",
    "generated_at",
}
_REQUIRED_EVIDENCE_KEYS = {
    "artifact_kind",
    "artifact_version",
    "record_uid",
    "record_hash_sha256",
    "generated_at",
    "accepted",
    "conformance_ok",
    "acceptance_errors",
    "acceptance_warnings",
    "constitution_checks",
}
_ALLOWED_CONSTITUTION_CHECK_KEYS = {"check_id", "status", "error_code", "details"}
_REQUIRED_CONSTITUTION_CHECK_KEYS = {"check_id", "status"}
_ALLOWED_CONSTITUTION_STATUSES = {"pass", "fail", "not_applicable"}
_SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")


def _validate_unknown_and_missing_root_fields(present_keys: set[str]) -> List[str]:
    errors: List[str] = []
    for key in sorted(present_keys - _ALLOWED_EVIDENCE_KEYS):
        errors.append(f"schema_violation:unknown_field_{key}")
    for key in sorted(_REQUIRED_EVIDENCE_KEYS - present_keys):
        errors.append(f"schema_violation:missing_field_{key}")
    return errors


def _validate_record_uid(value: Any) -> List[str]:
    if not isinstance(value, str):
        return ["schema_violation:invalid_type_record_uid"]
    if len(value) < 1:
        return ["schema_violation:invalid_length_record_uid"]
    return []


def _validate_required_sha256(value: Any, field: str) -> List[str]:
    if not isinstance(value, str):
        return [f"schema_violation:invalid_type_{field}"]
    if not _SHA256_PATTERN.match(value):
        return [f"schema_violation:invalid_format_{field}"]
    return []


def _validate_optional_sha256(value: Any, field: str) -> List[str]:
    if value is None:
        return []
    return _validate_required_sha256(value, field)


def _validate_string_list(value: Any, field: str) -> List[str]:
    if not isinstance(value, list):
        return [f"schema_violation:invalid_type_{field}"]
    for item in value:
        if not isinstance(item, str):
            return [f"schema_violation:invalid_item_type_{field}"]
    return []


def _validate_constitution_check_item(item: Any, index: int) -> List[str]:
    if not isinstance(item, dict):
        return [f"schema_violation:invalid_type_constitution_check_item_{index}"]

    errors: List[str] = []
    item_keys = set(item.keys())
    for key in sorted(item_keys - _ALLOWED_CONSTITUTION_CHECK_KEYS):
        errors.append(f"schema_violation:unknown_field_constitution_check_item_{index}_{key}")
    for key in sorted(_REQUIRED_CONSTITUTION_CHECK_KEYS - item_keys):
        errors.append(f"schema_violation:missing_field_constitution_check_item_{index}_{key}")

    check_id = item.get("check_id")
    if "check_id" in item:
        if not isinstance(check_id, str):
            errors.append(f"schema_violation:invalid_type_constitution_check_item_{index}_check_id")
        elif len(check_id) < 1:
            errors.append(f"schema_violation:invalid_length_constitution_check_item_{index}_check_id")

    status = item.get("status")
    if "status" in item and status not in _ALLOWED_CONSTITUTION_STATUSES:
        errors.append(f"schema_violation:invalid_value_constitution_check_item_{index}_status")

    error_code = item.get("error_code")
    if "error_code" in item and error_code is not None and not isinstance(error_code, str):
        errors.append(f"schema_violation:invalid_type_constitution_check_item_{index}_error_code")

    details = item.get("details")
    if "details" in item and details is not None and not isinstance(details, dict):
        errors.append(f"schema_violation:invalid_type_constitution_check_item_{index}_details")
    return errors


def _validate_constitution_checks(value: Any) -> List[str]:
    if not isinstance(value, list):
        return ["schema_violation:invalid_type_constitution_checks"]
    errors: List[str] = []
    for index, item in enumerate(value):
        errors.extend(_validate_constitution_check_item(item, index))
    return errors


def _validate_generated_at(value: Any) -> List[str]:
    if not isinstance(value, str):
        return ["schema_violation:invalid_type_generated_at"]
    if not value.endswith("Z"):
        return ["schema_violation:invalid_format_generated_at_utc_suffix"]
    try:
        datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return ["schema_violation:invalid_format_generated_at_iso8601"]
    return []


def _validate_policy_state_delta(value: Any) -> List[str]:
    if value is not None and not isinstance(value, dict):
        return ["schema_violation:invalid_type_policy_state_delta"]
    return []




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
    payload = json.dumps(
        canonical,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

def validate_evidence_schema(evidence: Dict[str, Any]) -> List[str]:
    """
    Validate evidence against the JSON schema strictly.
    Enforces types, formats, and no extraneous fields.
    Returns sorted list of deterministic error tokens.
    """
    errors: List[str] = []

    # 0. Root Type
    if not isinstance(evidence, dict):
        return ["schema_violation:evidence_not_dict"]

    # 1. Root field membership checks
    errors.extend(_validate_unknown_and_missing_root_fields(set(evidence.keys())))

    # 2. Value validation checks
    if "artifact_kind" in evidence and evidence["artifact_kind"] != "cluster_a_acceptance_evidence":
        errors.append("schema_violation:invalid_kind")
    if "artifact_version" in evidence and evidence["artifact_version"] != "v0.1":
        errors.append("schema_violation:invalid_version")

    if "record_uid" in evidence:
        errors.extend(_validate_record_uid(evidence["record_uid"]))

    if "record_hash_sha256" in evidence:
        errors.extend(_validate_required_sha256(evidence["record_hash_sha256"], "record_hash_sha256"))

    if "transcript_hash_sha256" in evidence:
        errors.extend(
            _validate_optional_sha256(evidence["transcript_hash_sha256"], "transcript_hash_sha256")
        )

    for f in ["accepted", "conformance_ok"]:
        if f in evidence and not isinstance(evidence[f], bool):
            errors.append(f"schema_violation:invalid_type_{f}")

    for f in ["acceptance_errors", "acceptance_warnings"]:
        if f in evidence:
            errors.extend(_validate_string_list(evidence[f], f))

    if "constitution_checks" in evidence:
        errors.extend(_validate_constitution_checks(evidence["constitution_checks"]))

    if "generated_at" in evidence:
        errors.extend(_validate_generated_at(evidence["generated_at"]))

    if "policy_state_delta" in evidence:
        errors.extend(_validate_policy_state_delta(evidence["policy_state_delta"]))

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
                        If missing, a deterministic fallback is used.

    Returns:
        Deterministic dictionary representing the evidence artifact.
    """
    
    # 1. Resolve Timestamp
    # Use context timestamp if valid, else a deterministic record-scoped fallback.
    to_use_ts = _resolve_generated_at(governance_record, runtime_context)

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


def _resolve_generated_at(
    governance_record: Dict[str, Any],
    runtime_context: Optional[Dict[str, Any]],
) -> str:
    if runtime_context and "timestamp" in runtime_context:
        return _require_strict_utc_timestamp(
            runtime_context["timestamp"],
            source="runtime_context['timestamp']",
        )

    if "timestamp" in governance_record and governance_record["timestamp"] is not None:
        return _require_strict_utc_timestamp(
            governance_record["timestamp"],
            source="governance_record['timestamp']",
        )

    return "1970-01-01T00:00:00Z"


def _require_strict_utc_timestamp(value: Any, *, source: str) -> str:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"{source} must be a strict ISO-8601 UTC string ending in 'Z'")
    try:
        datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{source} must be a strict ISO-8601 UTC string ending in 'Z'") from exc
    return value
