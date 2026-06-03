# SPDX-License-Identifier: AGPL-3.0-only
"""
Validator for ILC Governance Record Schema v0.1.
Enforces schema validity and signature presence.
"""
import json
import jsonschema  # type: ignore
from pathlib import Path
from typing import Any, Dict, List, Union
import re

_SCHEMA_PATH = Path(__file__).parent / "schemas" / "ilc_governance_record_schema_v0.1.json"

def _load_schema() -> Dict[str, Any]:
    with open(_SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

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
    path = ".".join(str(p) for p in error.path) or "root"
    
    if error.validator == "required":
        m = re.search(r"'(.*?)' is a required property", error.message)
        field = m.group(1) if m else "unknown"
        return _err("schema_violation:missing_field", field)
    
    if error.validator == "type":
        return _err("schema_violation:invalid_type", path)
    
    if error.validator == "additionalProperties":
        m = re.search(r"'(.*?)' was unexpected", error.message)
        field = m.group(1) if m else "unknown"
        field_path = f"{path}.{field}" if path != "root" else field
        return _err("schema_violation:unknown_field", field_path)
    
    if error.validator == "minItems":
         return _err("schema_violation:minItems", path)
    
    if error.validator == "enum":
         return _err("value_violation:invalid_enum", path)
    
    if error.validator == "pattern":
         return _err("value_violation:invalid_format", path)
    
    return _err(f"schema_violation:{error.validator}", path)

def validate_governance_record(path_or_obj: Union[str, Path, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate a governance record.
    """
    errors: List[str] = []
    warnings: List[str] = []
    
    # 1. Load context
    if isinstance(path_or_obj, (str, Path)):
        try:
            p = Path(path_or_obj)
            if not p.exists():
                return _result(False, errors=["file_not_found"])
            obj = json.loads(p.read_text(encoding="utf-8"))
        except OSError:
            return _result(False, errors=["file_read_error"])
        except json.JSONDecodeError:
            return _result(False, errors=["invalid_json"])
    else:
        if not isinstance(path_or_obj, dict):
            return _result(False, errors=["schema_violation:invalid_type:root"])
        obj = path_or_obj

    version = obj.get("protocol_version")

    # 2. Validate Schema
    validator = jsonschema.Draft202012Validator(_SCHEMA, format_checker=jsonschema.FormatChecker())
    for error in validator.iter_errors(obj):
        errors.append(_map_error(error))

    return _result(len(errors) == 0, errors=errors, warnings=warnings, version=version)
