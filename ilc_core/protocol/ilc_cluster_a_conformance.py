"""
ILC Constitution Cluster A - Conformance Hardening.
Phase 137.

Provides a deterministic conformance gate that binds runtime validation 
of artifacts to an explicit policy context, with strict artifact-class rules.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
import re
import json

from ilc_core.protocol.ilc_cluster_a_ingest import ingest_cluster_a_artifact
from ilc_core.protocol.ilc_cluster_a_clause_binding import evaluate_cluster_a_constitution_checks

# --- Internal Helpers ---

def _stable_result(
    ok: bool,
    *,
    artifact_kind: Optional[str] = None,
    errors: List[str] = None,
    warnings: List[str] = None,
    version: Optional[str] = None,
    policy_binding: Optional[Dict[str, Any]] = None,
    constitution_checks: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    # Deduplicate errors and warnings while preserving sort
    errors = sorted(list(set(errors or [])))
    warnings = sorted(list(set(warnings or [])))
    
    return {
        "ok": ok,
        "artifact_kind": artifact_kind,
        "errors": errors,
        "warnings": warnings,
        "version": version,
        "policy_binding": policy_binding,
        "constitution_checks": constitution_checks,
        "data": data,
    }

def _validate_hex_64(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    return bool(re.fullmatch(r"^[a-f0-9]{64}$", value))

def _load_and_extract(artifact: Union[Dict[str, Any], str, Path]) -> Tuple[Dict[str, Any], Dict[str, Any], List[str]]:
    """
    Load artifact, extract policy fields, and return (cleaned_obj, binding, errors).
    """
    obj = {}
    errors = []
    
    # Load
    if isinstance(artifact, (str, Path)):
        try:
            p = Path(artifact)
            if not p.exists():
                return {}, {}, ["file_not_found"]
            obj = json.loads(p.read_text(encoding="utf-8"))
        except OSError:
            return {}, {}, ["file_read_error"]
        except json.JSONDecodeError:
            return {}, {}, ["invalid_json"]
    elif isinstance(artifact, dict):
        obj = artifact.copy() # Shallow copy enough if we only pop top-level
    else:
        return {}, {}, ["schema_violation:invalid_type:root"]

    # Extract & Strip
    binding = {
        "policy_hash": obj.pop("policy_hash", None),
        "policy_epoch": obj.pop("policy_epoch", None),
        "policy_window": obj.pop("policy_window", None),
    }
    
    return obj, binding, errors

def _validate_binding_values(binding: Dict[str, Any]) -> List[str]:
    """Validate format of extracted binding fields."""
    errors = []
    p_hash = binding["policy_hash"]
    p_epoch = binding["policy_epoch"]
    p_window = binding["policy_window"]
    
    if p_hash is not None and not _validate_hex_64(p_hash):
        errors.append("value_violation:invalid_policy_hash")
    
    if p_epoch is not None:
        # `bool` is a subclass of `int`; require a strict integer type.
        if type(p_epoch) is not int or p_epoch < 0:
            errors.append("value_violation:invalid_policy_epoch")
            
    if p_window is not None:
        if not isinstance(p_window, str) or len(p_window) == 0:
            errors.append("value_violation:invalid_policy_window")
            
    return errors

def _validate_binding_structure(
    binding: Dict[str, Any],
    artifact_kind: str
) -> List[str]:
    """
    Validate binding structure based on artifact kind.
    Returns list of structural errors.
    """
    errors = []
    
    # Check presence of fields
    present_fields = {k for k, v in binding.items() if v is not None}
    missing_fields = {k for k in binding.keys() if k not in present_fields}
    all_present = len(missing_fields) == 0
    none_present = len(present_fields) == 0
    partial_present = not all_present and not none_present

    # Rule 1: Governance Record -> Must have full binding
    if artifact_kind == "governance_record":
        if not all_present:
             errors.append("context_violation:missing_policy_binding")

    # Rule 2: Transcript -> All or Nothing
    elif artifact_kind == "transcript":
        if partial_present:
             errors.append("context_violation:partial_policy_binding")
    
    return errors


def _validate_binding_context(
    binding: Dict[str, Any],
    expected: Dict[str, Any],
    value_errors: List[str]
) -> List[str]:
    """Compare extracted binding with expectations."""
    errors = []
    
    # Helper to check if a specific field has a value violation
    def has_val_err(err_name):
        return err_name in value_errors

    # Hash
    if expected["hash"] is not None:
        if binding["policy_hash"] is None:
            if "context_violation:missing_policy_binding" not in errors:
                errors.append("context_violation:missing_policy_binding")
        elif binding["policy_hash"] != expected["hash"] and not has_val_err("value_violation:invalid_policy_hash"):
             errors.append("context_violation:policy_hash_mismatch")

    # Epoch
    if expected["epoch"] is not None:
        if binding["policy_epoch"] is None:
             if "context_violation:missing_policy_binding" not in errors:
                errors.append("context_violation:missing_policy_binding")
        elif binding["policy_epoch"] != expected["epoch"] and not has_val_err("value_violation:invalid_policy_epoch"):
             errors.append("context_violation:policy_epoch_mismatch")

    # Window
    if expected["window"] is not None:
        if binding["policy_window"] is None:
             if "context_violation:missing_policy_binding" not in errors:
                errors.append("context_violation:missing_policy_binding")
        elif binding["policy_window"] != expected["window"] and not has_val_err("value_violation:invalid_policy_window"):
             errors.append("context_violation:policy_window_mismatch")
             
    return errors

# --- Public API ---

def _check_unchecked_warning(
    expectations_provided: bool,
    binding: Dict[str, Any],
    struct_errors: List[str],
    current_warnings: List[str]
) -> List[str]:
    """Appends warning if artifact is unchecked and unbound."""
    warnings = list(current_warnings)
    no_expectations = not expectations_provided
    has_any_binding = any(v is not None for v in binding.values())
    
    # Warning only if: No expectations AND No binding AND No structural errors
    if no_expectations and not has_any_binding and not struct_errors:
        warnings.append("policy_binding_absent_unchecked")
    return warnings

def _assemble_final_result(
    ingest_res: Dict[str, Any],
    val_errors: List[str],
    struct_errors: List[str],
    ctx_errors: List[str],
    warnings: List[str],
    binding: Dict[str, Any],
    constitution_checks: Dict[str, Any]
) -> Dict[str, Any]:
    """Assembles the final deterministic result envelope."""
    all_errors = val_errors + struct_errors + ctx_errors
    # Dedupe and sort handled by _stable_result, but we do it here for is_ok check logic?
    # Actually just pass to _stable_result.
    
    is_ok = len(all_errors) == 0
    if not constitution_checks["ok"]:
        is_ok = False
    
    binding_status = {
        "policy_hash": binding["policy_hash"],
        "policy_epoch": binding["policy_epoch"],
        "policy_window": binding["policy_window"],
        "binding_ok": is_ok
    }
    
    return _stable_result(
        is_ok,
        artifact_kind=ingest_res["artifact_kind"],
        errors=all_errors,
        warnings=warnings,
        version=ingest_res["version"],
        policy_binding=binding_status,
        constitution_checks=constitution_checks,
        data=ingest_res["data"] if is_ok else None
    )

def conformance_check_cluster_a_artifact(
    artifact: Union[Dict[str, Any], str, Path],
    *,
    expected_policy_hash: Optional[str] = None,
    expected_policy_epoch: Optional[int] = None,
    expected_policy_window: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Ingest an artifact and verify it binds to the expected policy context.
    """
    # 1. Load and Extract Policy Fields (Strip them from ingest input)
    clean_obj, binding, load_errors = _load_and_extract(artifact)
    if load_errors:
        return _stable_result(False, errors=load_errors, policy_binding=None)

    # 2. Ingest (Phase 135) - Use CLEAN object
    ingest_res = ingest_cluster_a_artifact(clean_obj)
    if not ingest_res["ok"]:
        return _stable_result(
            False,
            artifact_kind=ingest_res.get("artifact_kind"),
            errors=ingest_res.get("errors"),
            warnings=ingest_res.get("warnings"),
            version=ingest_res.get("version"),
            policy_binding=None,
            data=None
        )

    # 3. Validate Binding Values
    val_errors = _validate_binding_values(binding)
    
    # 4. Validate Structure (Artifact Kind Rules)
    expectations_provided = (expected_policy_hash is not None or 
                             expected_policy_epoch is not None or 
                             expected_policy_window is not None)

    # Note: strict_mode removed as handled by context validation
    struct_errors = _validate_binding_structure(
        binding, 
        ingest_res["artifact_kind"]
    )
    
    # 5. Compare Context
    expectations = {
        "hash": expected_policy_hash,
        "epoch": expected_policy_epoch,
        "window": expected_policy_window
    }
    ctx_errors = _validate_binding_context(binding, expectations, val_errors)
    
    # 6. Check Warnings
    final_warnings = _check_unchecked_warning(
        expectations_provided, binding, struct_errors, ingest_res["warnings"]
    )

    # 7. Constitution Checks (Phase 140)
    # Prepare context for binder
    binder_ctx = {
         "ingest_ok": ingest_res["ok"],
         "binding_valid": (len(val_errors) == 0 and len(struct_errors) == 0),
         "context_match": len(ctx_errors) == 0,
         "expectations_provided": expectations_provided,
         "all_errors": ingest_res.get("errors", []) + val_errors + struct_errors + ctx_errors
    }
    const_checks = evaluate_cluster_a_constitution_checks(binder_ctx)

    # 8. Result Assembly
    return _assemble_final_result(
        ingest_res, val_errors, struct_errors, ctx_errors, final_warnings, binding, const_checks
    )

def _has_error_prefix(errors: List[str], prefixes: Union[str, Tuple[str, ...]]) -> bool:
    """Helper to detect error codes with specific prefixes."""
    if isinstance(prefixes, str):
        prefixes = (prefixes,)
    return any(e.startswith(prefixes) for e in errors)

def classify_conformance_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic summary helper for replay/audit.
    """
    ok = result["ok"]
    errors = result.get("errors", [])
    warnings = result.get("warnings", [])
    
    if ok:
        return {
            "ok": True,
            "category": "pass",
            "error_count": 0,
            "warning_count": len(warnings)
        }

    # Failure Categorization - using helper to reduce nesting depth
    category = "unknown_failure"
    
    # Priority 1: Ingest Failure
    is_ingest = (result.get("policy_binding") is None) or \
                _has_error_prefix(errors, ("file_", "invalid_json", "schema_violation", "context_violation:unknown_artifact_kind"))
    
    if is_ingest:
         category = "ingest_failure"
    
    # Priority 2: Value Failure
    elif _has_error_prefix(errors, "value_violation:invalid_policy_"):
         category = "binding_value_failure"
         
    # Priority 3: Structure Failure
    # Exact match check
    elif any(e in ("context_violation:missing_policy_binding", "context_violation:partial_policy_binding") for e in errors):
         category = "binding_structure_failure"
         
    # Priority 4: Context Mismatch
    elif _has_error_prefix(errors, "context_violation:policy_"):
         category = "binding_context_mismatch"

    return {
        "ok": False,
        "category": category,
        "error_count": len(errors),
        "warning_count": len(warnings)
    }
