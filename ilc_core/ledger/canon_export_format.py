from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List


def export_canon_format_v0_1(canon_state: Dict[str, Any], exported_at: Optional[str] = None) -> Dict[str, Any]:
    """
    Transform a raw canon_state dict into the standardized v0.1 export format.

    Args:
        canon_state: The raw canon state dictionary. Must contain 'canon_hash' and 'canon_export_version'.
                     Optional keys 'epochs' (list), 'snapshots' (list), 'balances' (dict) are used if present.
        exported_at: Optional ISO-8601 timestamp string. If None, current UTC time is used.

    Returns:
        Dict conforming to the canon_export_format_v0.1 schema.

    Raises:
        ValueError: If required keys are missing or types are incorrect.
    """
    if "canon_hash" not in canon_state or "canon_export_version" not in canon_state:
        raise ValueError("canon_state missing required keys: 'canon_hash' and 'canon_export_version' are mandatory")

    exported_at = exported_at or datetime.now(timezone.utc).isoformat()

    # Extract core data with defaults
    epochs: List[Any] = canon_state.get("epochs", [])
    snapshots: List[Any] = canon_state.get("snapshots", [])
    balances: Dict[str, float] = canon_state.get("balances", {})

    # Validate types minimally to ensure schema compliance
    if not isinstance(epochs, list):
        raise ValueError("Field 'epochs' must be a list")
    if not isinstance(snapshots, list):
        raise ValueError("Field 'snapshots' must be a list")
    if not isinstance(balances, dict):
        raise ValueError("Field 'balances' must be a dict")

    # Construct Metadata
    meta = {
        "canon_export_version": canon_state.get("canon_export_version"),
        "epoch_count": len(epochs),
        "snapshot_count": len(snapshots),
        "balance_count": len(balances),
    }

    # Construct Payload
    payload = {
        "canon_export_format": "v0.1",
        "canon_hash": canon_state.get("canon_hash"),
        "computed_hash": canon_state.get("computed_hash"),
        "exported_at": exported_at,
        "meta": meta,
        "epochs": epochs,
        "snapshots": snapshots,
        "kpis": {
            "epoch_count": meta["epoch_count"],
            "snapshot_count": meta["snapshot_count"],
            "balance_count": meta["balance_count"],
        },
    }
    
    # Filter out None values that are not required (computed_hash)
    # Actually schema allows computed_hash to be missing? No, schema says optional propery, so we can omit or pass null?
    # Spec table says "No" for required on computed_hash. 
    # Python code above includes it with .get(), so it might be None.
    # We'll leave it in. If it's None, it serializes to null, which is valid JSON.

    return payload
