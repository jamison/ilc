"""
Validator for ILC Canonical Transcript Schema v0.1.
Enforces schema validity and deterministic record ordering.
"""
import json
import jsonschema  # type: ignore
from pathlib import Path
from typing import Any, Dict, List, Union, Tuple
import re
from ilc_core.protocol.ilc_receipt_validate import validate_receipt_record
from ilc_core.protocol.ilc_wire_validate import validate_wire_event

_SCHEMA_PATH = Path(__file__).parent / "schemas" / "ilc_canonical_transcript_schema_v0.1.json"

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

def _get_sort_key(record: Dict[str, Any]) -> Tuple[str, str, str]:
    # Key: (timestamp, event_kind, event_id)
    return (
        record.get("timestamp", ""),
        record.get("event_kind", ""),
        record.get("event_id", "")
    )

def _map_error(error: Any) -> str:
    path = ".".join(str(p) for p in error.path) or "root"
    
    if error.validator == "required":
        m = re.search(r"'(.*?)' is a required property", error.message)
        field = m.group(1) if m else "unknown"
        return _err("schema_violation:missing_field", field)
    
    if error.validator == "type":
        # If path indicates an array index (e.g. records.0), it's still invalid_type
        return _err("schema_violation:invalid_type", path)
    
    if error.validator == "additionalProperties":
        m = re.search(r"'(.*?)' was unexpected", error.message)
        field = m.group(1) if m else "unknown"
        field_path = f"{path}.{field}" if path != "root" else field
        return _err("schema_violation:unknown_field", field_path)
    
    if error.validator == "pattern":
        return _err("value_violation:invalid_format", path)
    
    if error.validator == "enum":
        return _err("value_violation:invalid_enum", path)
    
    return _err(f"schema_violation:{error.validator}", path)

def validate_transcript(path_or_obj: Union[str, Path, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate a canonical transcript.
    Check schema and deterministic ordering.
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
    validator = jsonschema.Draft202012Validator(_SCHEMA)
    for error in validator.iter_errors(obj):
        errors.append(_map_error(error))

    # 3. Validate Ordering (Semantic check)
    # Only if schema validation passed for structure, otherwise might crash
    records = obj.get("records")
    if isinstance(records, list):
        # Extract keys
        pk_list = [_get_sort_key(r) for r in records if isinstance(r, dict)]
        if pk_list != sorted(pk_list):
            errors.append(_err("ordering_violation", "records"))

        # Each record must validate as either a wire event or receipt.
        for idx, record in enumerate(records):
            if not isinstance(record, dict):
                continue
            wire_result = validate_wire_event(record)
            receipt_result = validate_receipt_record(record)
            if not wire_result["ok"] and not receipt_result["ok"]:
                errors.append(_err("context_violation", f"record_not_wire_or_receipt:{idx}"))

    return _result(len(errors) == 0, errors=errors, warnings=warnings, version=version)
