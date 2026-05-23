# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

from typing import TypeAlias
from pathlib import Path
from os import PathLike
import json
import hashlib
import datetime
import os
import tempfile
from dataclasses import asdict

from ilc_core.ledger.backend import LedgerBackend
from ilc_core.ledger.exact_numeric import (
    exact_to_canonical_string,
    normalize_json_scalars,
)

JsonScalar: TypeAlias = str | int | bool | None
JsonValue: TypeAlias = JsonScalar | dict[str, "JsonValue"] | list["JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]


def compute_canon_hash(payload: JsonObject) -> str:
    """
    Compute a deterministic SHA-256 hash of the canon payload.
    The payload MUST NOT contain the 'canon_hash' field (or it should be empty).
    """
    # Sort keys for determinism.
    # We use sort_keys=True. ensuring stable ordering of dictionary keys.
    canonical_json = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

def export_canon_state_json(
    ledger: LedgerBackend, 
    path: PathLike, 
    *, 
    canon_version: str = "v0.1"
) -> JsonObject:
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
    stake_snapshots_data: dict[str, JsonObject] = {
        k: normalize_json_scalars(asdict(v)) for k, v in ledger.stake_snapshots.items()
    }
    
    # Sort epoch records
    epoch_records_data: dict[str, JsonObject] = {
        k: normalize_json_scalars(dict(v)) for k, v in ledger.epoch_records.items()
    }
    
    # Balances are a simple dict, sort_keys=True handles it.
    balances_data: dict[str, str] = {
        agent_id: exact_to_canonical_string(amount, token="canon_export_balance_invalid")
        for agent_id, amount in ledger.balances.items()
    }
    
    # 2. Build payload structure
    payload: JsonObject = {
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
    
    tmp_path: str | None = None
    try:
        fd, tmp_path = tempfile.mkstemp(
            prefix=f".{out_path.name}.",
            suffix=".tmp",
            dir=out_path.parent,
            text=True,
        )
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, allow_nan=False, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp_path, out_path)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                os.unlink(tmp_path)
            except FileNotFoundError:
                pass
        
    return payload
