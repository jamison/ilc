"""
ILC Constitution Cluster A - Conformance and Policy Binding.
Phase 136.

Provides a deterministic conformance gate that binds runtime validation 
of artifacts to an explicit policy context.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
import re
import json

from ilc_core.protocol.ilc_cluster_a_ingest import ingest_cluster_a_artifact

# --- Internal Helpers ---

def _stable_result(
    ok: bool,
    *,
    artifact_kind: Optional[str] = None,
    errors: List[str] = None,
    warnings: List[str] = None,
    version: Optional[str] = None,
    policy_binding: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "ok": ok,
        "artifact_kind": artifact_kind,
        "errors": sorted(errors or []),
        "warnings": sorted(warnings or []),
        "version": version,
        "policy_binding": policy_binding,
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
        # Pre-ingest failure (e.g. file read, json error)
        # Ingest would report these same errors if called on path.
        # But we need to return extracted binding? No, if load fails, no binding.
        return _stable_result(False, errors=load_errors, policy_binding=None)

    # 2. Ingest (Phase 135) - Use CLEAN object
    ingest_res = ingest_cluster_a_artifact(clean_obj)
    
    if not ingest_res["ok"]:
        return _stable_result(
            False,
            artifact_kind=ingest_res["artifact_kind"],
            errors=ingest_res["errors"],
            warnings=ingest_res["warnings"],
            version=ingest_res["version"],
            policy_binding=None, # Ingest failure -> strict None binding
            data=None
        )

    # 3. Validate Binding Values
    val_errors = _validate_binding_values(binding)
    
    # 4. Compare Context
    expectations = {
        "hash": expected_policy_hash,
        "epoch": expected_policy_epoch,
        "window": expected_policy_window
    }
    ctx_errors = _validate_binding_context(binding, expectations, val_errors)
    
    # 5. Check Warnings
    warnings = list(ingest_res["warnings"])
    no_expectations = all(v is None for v in expectations.values())
    has_any_binding = any(v is not None for v in binding.values())
    
    if no_expectations and not has_any_binding:
        warnings.append("policy_binding_absent_unchecked")

    # 6. Result
    all_errors = val_errors + ctx_errors
    is_ok = len(all_errors) == 0
    
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
        data=ingest_res["data"] if is_ok else None
    )
