
from typing import Dict, Any, List
from pathlib import Path
from os import PathLike
import json
import hashlib
import datetime
from dataclasses import asdict

from ilc_core.ledger.backend import LedgerBackend

def compute_canon_hash(payload: Dict[str, Any]) -> str:
    """
    Compute a deterministic SHA-256 hash of the canon payload.
    The payload MUST NOT contain the 'canon_hash' field (or it should be empty).
    """
    # Sort keys for determinism.
    # We use sort_keys=True. ensuring stable ordering of dictionary keys.
    canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

def export_canon_state_json(
    ledger: LedgerBackend, 
    path: PathLike, 
    *, 
    canon_version: str = "v0.1"
) -> Dict[str, Any]:
    """
    Export canonical, deterministic ledger state to a JSON file.
    
    Returns the final canon payload dict (including the computed canon_hash).
    
    Determinism Guarantee:
    - All dictionary keys are sorted in the JSON output.
    - Lists of records (if any) should be sorted by stable IDs.
    - No runtime-dependent values (like UUIDs unless they are part of the state) are generated.
    """
    # 1. Extract state (read-only copy)
    # Convert data classes to dicts if needed
    
    # Sort stake snapshots by epoch_id (or some stable key)
    # The ledger stores them as a dict, so json dump verify sort_keys=True handles the map keys.
    # We just need to ensure the values inside are also stable.
    stake_snapshots_data = {
        k: asdict(v) for k, v in ledger.stake_snapshots.items()
    }
    
    # Sort epoch records
    epoch_records_data = {
        k: v for k, v in ledger.epoch_records.items()
    }
    
    # Balances are a simple dict, sort_keys=True handles it.
    balances_data = ledger.balances.copy()
    
    # 2. Build payload structure
    payload = {
        "canon_export_version": canon_version,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        # canon_hash will be inserted after computation
        
        "epoch_records": epoch_records_data,
        "stake_snapshots": stake_snapshots_data,
        "balances": balances_data,
    }
    
    # 3. Compute Hash
    # Fix: Exclude generated_at from the hash to ensure determinism across runs.
    # We copy the payload and remove mutable fields.
    payload_for_hashing = payload.copy()
    if "generated_at" in payload_for_hashing:
        del payload_for_hashing["generated_at"]
    
    # We compute hash of the payload WITHOUT generated_at and WITHOUT canon_hash key.
    payload_hash = compute_canon_hash(payload_for_hashing)
    
    # 4. Insert Hash
    payload["canon_hash"] = payload_hash
    
    # 5. Write to disk
    # Use sort_keys=True to ensure file determinism as well
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        
    return payload
