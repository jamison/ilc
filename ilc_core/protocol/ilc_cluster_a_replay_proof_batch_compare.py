import json
from typing import Any, Dict, List, Optional
from pathlib import Path
from jsonschema import Draft7Validator

# Load schema once
_SCHEMA_PATH = Path(__file__).parent.parent.parent / "docs" / "specs" / "ilc_cluster_a_replay_proof_batch_report_v0.1.json"
try:
    with open(_SCHEMA_PATH, "r", encoding="utf-8") as f:
        _BATCH_REPORT_SCHEMA = json.load(f)
except Exception:
    # Fail closed through schema_invalid_* response if schema is unavailable.
    _BATCH_REPORT_SCHEMA = {}

_BATCH_REPORT_VALIDATOR = Draft7Validator(_BATCH_REPORT_SCHEMA) if _BATCH_REPORT_SCHEMA else None

def _escape_path_token(token: str) -> str:
    """Escape path token per JSON Pointer (RFC 6901)."""
    return token.replace("~", "~0").replace("/", "~1")

def _path_join(parent: str, key: str) -> str:
    """Append key to parent path."""
    token = _escape_path_token(str(key))
    if parent in ("", "/"):
        return f"/{token}"
    return f"{parent}/{token}"

def _validate_schema(data: Any) -> Optional[str]:
    """
    Validate data against batch report schema.
    Returns error string if invalid, None if valid.
    """
    if _BATCH_REPORT_VALIDATOR is None:
        return "internal_error:schema_not_loaded"

    errors = list(_BATCH_REPORT_VALIDATOR.iter_errors(data))
    if not errors:
        return None
    errors.sort(key=lambda e: (list(e.absolute_path), e.message))
    return f"schema_validation_failed: {errors[0].message}"

def _schema_invalid_report(reason: str, left: Any, right: Any, detail: str) -> Dict[str, Any]:
    """Build deterministic schema-invalid compare response."""
    return {
        "compare_version": "v0.1",
        "ok": False,
        "left_report_version": left.get("report_version") if isinstance(left, dict) else None,
        "right_report_version": right.get("report_version") if isinstance(right, dict) else None,
        "mismatch_count": 1,
        "mismatches": [{
            "path": "/",
            "reason": reason,
            "detail": detail,
            "left": None,
            "right": None
        }]
    }

def _compare_recursive(path: str, left: Any, right: Any, mismatches: List[Dict[str, Any]]) -> None:
    """
    Recursively compare left and right structures.
    Populates mismatches list.
    """
    # Type mismatch is value mismatch
    if type(left) != type(right):
        mismatches.append({
            "path": path,
            "reason": "value_mismatch",
            "left": left,
            "right": right
        })
        return

    # Dict comparison
    if isinstance(left, dict):
        left_keys = set(left.keys())
        right_keys = set(right.keys())
        
        all_keys = sorted(left_keys | right_keys)
        
        for k in all_keys:
            new_path = _path_join(path, k)
            
            if k not in left_keys:
                mismatches.append({
                    "path": new_path,
                    "reason": "missing_left",
                    "left": None,
                    "right": right[k]
                })
            elif k not in right_keys:
                mismatches.append({
                    "path": new_path,
                    "reason": "missing_right",
                    "left": left[k],
                    "right": None
                })
            else:
                _compare_recursive(new_path, left[k], right[k], mismatches)
        return

    # List comparison
    if isinstance(left, list):
        if len(left) != len(right):
            # If lengths differ, it's a value mismatch on the list itself? 
            # Or should we compare element by element?
            # Prompt says "structural comparison".
            # Usually lists are compared by index.
            # If length differs, we can flag value_mismatch on the list, 
            # OR iterate up to max length.
            # Let's iterate up to max length to be granular.
            pass
            
        max_len = max(len(left), len(right))
        for i in range(max_len):
            new_path = _path_join(path, str(i))
            
            if i >= len(left):
                 mismatches.append({
                    "path": new_path,
                    "reason": "missing_left",
                    "left": None,
                    "right": right[i]
                })
            elif i >= len(right):
                 mismatches.append({
                    "path": new_path,
                    "reason": "missing_right",
                    "left": left[i],
                    "right": None
                })
            else:
                _compare_recursive(new_path, left[i], right[i], mismatches)
        return

    # Primitive comparison
    if left != right:
        mismatches.append({
            "path": path,
            "reason": "value_mismatch",
            "left": left,
            "right": right
        })

def compare_cluster_a_replay_proof_batch_reports(left: Any, right: Any) -> Dict[str, Any]:
    """
    Compare two batch reports structurally and return deterministic diff report.
    """
    # 1. Schema Validation
    left_err = _validate_schema(left)
    if left_err:
        return _schema_invalid_report("schema_invalid_left", left, right, left_err)

    right_err = _validate_schema(right)
    if right_err:
        return _schema_invalid_report("schema_invalid_right", left, right, right_err)
        
    # 2. Deep Compare
    mismatches: List[Dict[str, Any]] = []
    _compare_recursive("/", left, right, mismatches)
    
    # 3. Sort Deterministically
    # Sort by path, then reason
    mismatches.sort(key=lambda x: (x["path"], x["reason"]))
    
    return {
        "compare_version": "v0.1",
        "ok": len(mismatches) == 0,
        "left_report_version": left.get("report_version"),
        "right_report_version": right.get("report_version"),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches
    }
