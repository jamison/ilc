"""
Validator for ILC Protocol Wire Format v0.1.
Validates events against the canonical JSON schema.
"""
import json
import jsonschema  # type: ignore
from pathlib import Path
from typing import Any, Dict, Union, Optional, List
import re

# Load schema relative to this file
_SCHEMA_PATH = Path(__file__).parent / "schemas" / "ilc_protocol_wire_format_v0.1.json"

def _load_schema() -> Dict[str, Any]:
    with open(_SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# Cache schema in module scope to avoid re-reading
_SCHEMA = _load_schema()

def _err(prefix: str, name: str) -> str:
    return f"{prefix}:{name}"

def _result(ok: bool, *, errors=None, warnings=None, version=None) -> Dict[str, Any]:
    return {
        "ok": ok,
        "errors": sorted(errors or []),
        "warnings": sorted(warnings or []),
        "version": version,
    }

def _map_error(error: Any) -> str:
    """Map jsonschema error to stable machine code."""
    path = ".".join(str(p) for p in error.path)
    if not path:
        path = "root"

    if error.validator == "required":
        match = error.message.split("'")[1] if "'" in error.message else "unknown"
        return _err("schema_violation:missing_field", match)
    
    if error.validator == "type":
        return _err("schema_violation:invalid_type", path)
    
    if error.validator == "additionalProperties":
         m = re.search(r"'(.*?)' was unexpected", error.message)
         field = m.group(1) if m else "unknown"
         return _err("schema_violation:unknown_field", field)
    
    if error.validator == "unevaluatedProperties":
         m = re.search(r"'(.*?)' was unexpected", error.message)
         field = m.group(1) if m else "unknown"
         field_path = f"{path}.{field}" if path != "root" else field
         return _err("schema_violation:unknown_field", field_path)
    
    if error.validator == "enum":
        return _err("value_violation:invalid_enum", path)
    
    if error.validator == "pattern":
        return _err("value_violation:invalid_format", path)
    
    if error.validator == "const":
         return _err("value_violation:const_mismatch", path)
    
    return _err(f"schema_violation:{error.validator}", path)

def validate_wire_event(path_or_obj: Union[str, Path, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate a wire format event object or file.
    
    Args:
        path_or_obj: JSON object (dict) or path to JSON file.
        
    Returns:
        Dict with keys: ok, errors, warnings, version.
    """
    errors: List[str] = []
    warnings: List[str] = []
    obj: Dict[str, Any] = {}

    # 1. Load context
    if isinstance(path_or_obj, (str, Path)):
        try:
            p = Path(path_or_obj)
            if not p.exists():
                return _result(False, errors=["file_not_found"])
            text = p.read_text(encoding="utf-8")
            obj = json.loads(text)
        except OSError:
            return _result(False, errors=["file_read_error"])
        except json.JSONDecodeError:
            return _result(False, errors=["invalid_json"])
    else:
        if not isinstance(path_or_obj, dict):
            return _result(False, errors=["schema_violation:invalid_type:root"])
        obj = path_or_obj

    version = obj.get("protocol_version")

    # 2. Validate against JSON Schema
    validator = jsonschema.Draft202012Validator(_SCHEMA)
    
    for error in validator.iter_errors(obj):
        errors.append(_map_error(error))

    # 3. Finalize
    return _result(len(errors) == 0, errors=errors, warnings=warnings, version=version)
