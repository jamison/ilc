from typing import Any, Dict, List

def _is_number(value: Any) -> bool:
    """Return True if value is int or float and NOT bool."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)

def validate_canon_export_v0_1(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate a dictionary against the Canon Export Format v0.1 rules.
    
    Returns:
        Dict with keys: "ok" (bool), "errors" (List[str]), "warnings" (List[str])
    """
    errors: List[str] = []
    warnings: List[str] = []

    # 1. Required Top-Level Keys
    required_keys = ["canon_export_format", "canon_hash", "exported_at", "meta", "epochs", "snapshots"]
    for key in required_keys:
        if key not in doc:
            errors.append(f"Missing required top-level key: '{key}'")

    # If basics are missing, return early to avoid crash on deeper checks
    if errors:
         return {"ok": False, "errors": errors, "warnings": warnings}

    # 2. Format Version Check
    if doc.get("canon_export_format") != "v0.1":
        errors.append(f"Invalid format version: expected 'v0.1', got '{doc.get('canon_export_format')}'")

    # 3. Meta Object Validation
    meta = doc.get("meta")
    if not isinstance(meta, dict):
        errors.append("Field 'meta' must be a dictionary")
    else:
        meta_required = ["canon_export_version", "epoch_count", "snapshot_count", "balance_count"]
        for key in meta_required:
            if key not in meta:
                errors.append(f"Missing meta key: '{key}'")
        
        # Type checks for meta counts
        if not isinstance(meta.get("epoch_count"), int): errors.append("meta.epoch_count must be an integer")
        if not isinstance(meta.get("snapshot_count"), int): errors.append("meta.snapshot_count must be an integer")
        if not isinstance(meta.get("balance_count"), int): errors.append("meta.balance_count must be an integer")
        if not isinstance(meta.get("canon_export_version"), str): errors.append("meta.canon_export_version must be a string")

    # 4. Epochs Validation
    epochs = doc.get("epochs")
    if not isinstance(epochs, list):
        errors.append("Field 'epochs' must be a list")
    else:
        for idx, item in enumerate(epochs):
            if not isinstance(item, dict):
                errors.append(f"epochs[{idx}] must be a dictionary")
                continue
            if "epoch_id" not in item:
                errors.append(f"epochs[{idx}] missing 'epoch_id'")
            elif not isinstance(item["epoch_id"], str):
                errors.append(f"epochs[{idx}].epoch_id must be a string")

    # 5. Snapshots Validation
    snapshots = doc.get("snapshots")
    if not isinstance(snapshots, list):
        errors.append("Field 'snapshots' must be a list")
    else:
        for idx, item in enumerate(snapshots):
            if not isinstance(item, dict):
                errors.append(f"snapshots[{idx}] must be a dictionary")
                continue
            
            if "epoch_id" not in item:
                errors.append(f"snapshots[{idx}] missing 'epoch_id'")
                
            balances = item.get("balances")
            if balances is not None:
                if not isinstance(balances, dict):
                    errors.append(f"snapshots[{idx}].balances must be a dictionary")
                else:
                    # Validate numeric values
                    for agent_id, amount in balances.items():
                        if not _is_number(amount):
                            errors.append(f"snapshots[{idx}].balances['{agent_id}'] must be a number")

    # 6. Warnings (Soft Checks)
    if "computed_hash" not in doc:
        warnings.append("Missing optional field 'computed_hash'")
    
    if "kpis" not in doc:
        warnings.append("Missing optional field 'kpis'")
        
    if isinstance(epochs, list) and isinstance(snapshots, list):
        if len(epochs) == 0 and len(snapshots) == 0:
            warnings.append("Export contains no epochs and no snapshots (empty dataset?)")

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }
