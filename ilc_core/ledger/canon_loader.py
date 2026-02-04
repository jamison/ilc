
from typing import Dict, Any, Optional
from os import PathLike
from pathlib import Path
import json
from dataclasses import dataclass

from ilc_core.ledger.canon_export import compute_canon_hash

class CanonVerificationError(ValueError):
    """Raised when canon verification fails."""
    pass

@dataclass(frozen=True)
class CanonState:
    canon_export_version: str
    canon_hash: str
    generated_at: str
    epoch_records: Dict[str, Any]
    stake_snapshots: Dict[str, Any]
    balances: Dict[str, Any]

def verify_canon_hash(payload: Dict[str, Any]) -> bool:
    """
    Verify the integrity of a canon payload.
    
    Returns:
        True if the computed hash matches payload['canon_hash'].
        
    Raises:
        CanonVerificationError if 'canon_hash' is missing or verification fails.
    """
    if "canon_hash" not in payload:
        raise CanonVerificationError("Missing 'canon_hash' field in payload.")
    
    expected_hash = payload["canon_hash"]
    
    # Replicate export logic:
    # 1. Copy payload
    # 2. Remove non-hashed fields (canon_hash, generated_at)
    verify_payload = payload.copy()
    
    # Must remove the hash itself
    del verify_payload["canon_hash"]
    
    # Must remove generated_at (as per export fix)
    if "generated_at" in verify_payload:
        del verify_payload["generated_at"]
        
    computed_hash = compute_canon_hash(verify_payload)
    
    if computed_hash != expected_hash:
        raise CanonVerificationError(
            f"Hash mismatch! Expected {expected_hash}, computed {computed_hash}"
        )
        
    return True

def load_canon_state(path: PathLike) -> Dict[str, Any]:
    """
    Load canon state from JSON file and verify integrity.
    
    Args:
        path: Path to canon_state.json
        
    Returns:
        Verified payload dict.
        
    Raises:
        CanonVerificationError: If verification fails.
        KeyError/ValueError: If schema is invalid.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Canon file not found: {p}")
        
    with p.open("r", encoding="utf-8") as f:
        try:
            payload = json.load(f)
        except json.JSONDecodeError as e:
            raise CanonVerificationError(f"Invalid JSON: {e}")
            
    # Basic Schema Sanity
    required_keys = {
        "canon_export_version": str,
        "canon_hash": str,
        "generated_at": str,
        "epoch_records": dict,
        "stake_snapshots": dict,
        "balances": dict
    }
    
    for key, expected_type in required_keys.items():
        if key not in payload:
            raise CanonVerificationError(f"Missing required key: {key}")
        if not isinstance(payload[key], expected_type):
            raise CanonVerificationError(
                f"Invalid type for '{key}': expected {expected_type.__name__}, got {type(payload[key]).__name__}"
            )
            
    if payload["canon_export_version"] != "v0.1":
        raise CanonVerificationError(f"Unsupported version: {payload.get('canon_export_version')}")

    # Verify Hash
    verify_canon_hash(payload)
    
    return payload

def verify_canon_state(path: PathLike) -> Dict[str, Any]:
    """
    Verify canon state file and return a verification report.
    Does NOT raise exceptions for verification failures (returns ok=False).
    
    Returns:
        Dict with keys:
            - ok (bool): True if verified
            - canon_hash (str): The hash found in the file
            - computed_hash (str): The hash re-computed (if possible)
            - error (str, optional): Error message if failed
    """
    try:
        # We can reuse load_canon_state, but we need to catch the specific errors
        # However, load_canon_state returns the payload, we want report.
        # Let's do a custom flow to capture computed hash even on mismatch.
        
        p = Path(path)
        if not p.exists():
            return {"ok": False, "error": f"File not found: {path}"}
            
        with p.open("r", encoding="utf-8") as f:
            try:
                payload = json.load(f)
            except json.JSONDecodeError as e:
                return {"ok": False, "error": f"Invalid JSON: {e}"}
        
        # We won't replicate full schema check here, just enough to get hash
        if "canon_hash" not in payload:
            return {"ok": False, "error": "Missing 'canon_hash' field"}
            
        expected_hash = payload["canon_hash"]
        
        # Compute
        verify_payload = payload.copy()
        del verify_payload["canon_hash"]
        if "generated_at" in verify_payload:
            del verify_payload["generated_at"]
            
        computed_hash = compute_canon_hash(verify_payload)
        
        if computed_hash == expected_hash:
            return {
                "ok": True, 
                "canon_hash": expected_hash, 
                "computed_hash": computed_hash
            }
        else:
            return {
                "ok": False, 
                "canon_hash": expected_hash, 
                "computed_hash": computed_hash,
                "error": "Hash mismatch"
            }
            
    except Exception as e:
        return {"ok": False, "error": str(e)}

def load_canon_state_obj(path: PathLike) -> CanonState:
    """
    Load canon state and return typed wrapper.
    """
    data = load_canon_state(path)
    return CanonState(
        canon_export_version=data["canon_export_version"],
        canon_hash=data["canon_hash"],
        generated_at=data["generated_at"],
        epoch_records=data["epoch_records"],
        stake_snapshots=data["stake_snapshots"],
        balances=data["balances"]
    )
