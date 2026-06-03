# SPDX-License-Identifier: AGPL-3.0-only
import json
import csv
import os
import tempfile
from os import PathLike
from pathlib import Path
from dataclasses import asdict
from typing import TypeAlias, TypedDict

from ilc_core.ledger.backend import EpochRecord, LedgerBackend
from ilc_core.ledger.exact_numeric import (
    exact_to_canonical_string,
    normalize_json_scalars,
)
from ilc_core.ledger.settlement_verification import (
    SettlementVerificationResult,
    verify_stake_distribution,
)


JsonScalar: TypeAlias = str | int | bool | None
JsonValue: TypeAlias = JsonScalar | dict[str, "JsonValue"] | list["JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]


class LedgerStateExport(TypedDict):
    epoch_records: dict[str, EpochRecord]
    stake_snapshots: dict[str, JsonObject]
    balances: dict[str, str]


class LedgerDistributionCheck(TypedDict, total=False):
    epoch_id: str
    ok: bool
    total_delta: str
    expected_total: str
    max_agent_error: str
    top_errors: list[str]
    input_hash: str


VerificationResult: TypeAlias = SettlementVerificationResult | dict[str, object]

def export_ledger_state_json(
    ledger: LedgerBackend, 
    path: PathLike,
    *,
    balances_before: dict[str, object] | None = None,
    target_epoch_id: str | None = None
) -> VerificationResult:
    """
    Export full ledger state to a JSON file.
    
    If balances_before and target_epoch_id are provided, performs distribution check
    on that specific epoch and attaches 'distribution_check' to the record.
    
    Returns the verification result (check dict) if performed, else empty dict.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    # Access internal storage (assuming InMemory/File backend structure)
    epoch_records = getattr(ledger, "epoch_records", {})
    balances = getattr(ledger, "balances", {})
    raw_snapshots = getattr(ledger, "stake_snapshots", {})
    
    # Convert snapshots to dicts
    snapshots_data: dict[str, JsonObject] = {}
    for epoch_id, snap in raw_snapshots.items():
        if hasattr(snap, "to_dict"):
            snapshots_data[epoch_id] = normalize_json_scalars(snap.to_dict())
        else:
            snapshots_data[epoch_id] = normalize_json_scalars(asdict(snap))

    epoch_records_data = {
        epoch_id: normalize_json_scalars(record)
        for epoch_id, record in epoch_records.items()
    }
    balances_data = {
        agent_id: exact_to_canonical_string(amount, token="ledger_export_balance_invalid")
        for agent_id, amount in balances.items()
    }
            
    data: LedgerStateExport = {
        "epoch_records": epoch_records_data,
        "stake_snapshots": snapshots_data,
        "balances": balances_data,
    }
    
    check_result: VerificationResult = {}
    
    # Optional Verification (Task B)
    if balances_before is not None and target_epoch_id:
        record = epoch_records.get(target_epoch_id)
        # We need the snapshot for *this* epoch
        snapshot_raw = raw_snapshots.get(target_epoch_id)
        
        if record:
             check_result = verify_stake_distribution(
                 epoch_record=record,
                 snapshot=snapshot_raw, # verify handles None
                 balances_before=balances_before,
                 balances_after=balances # current balances are 'after'
             )
             # MEDIUM-012 fix: build a new output record rather than mutating the
             # shared epoch_records dict entry in-place, avoiding races on concurrent readers.
             annotated_record = dict(normalize_json_scalars(record))
             annotated_record["distribution_check"] = normalize_json_scalars(check_result)
             data["epoch_records"][target_epoch_id] = annotated_record

    # MEDIUM-012 fix: write atomically (tempfile + os.replace) so a crash mid-write
    # cannot produce a partial/corrupt output file.  allow_nan=False ensures float NaN
    # or Infinity raises ValueError rather than producing invalid JSON.
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=p.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True, allow_nan=False)
        os.replace(tmp_path, p)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    return check_result

def export_ledger_state_csv(ledger: LedgerBackend, path: PathLike) -> None:
    """
    Export ledger epoch records to a CSV file.
    
    Note: Currently only exports flat epoch records. 
    Snapshots and balances are available in the JSON export.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    epoch_records = getattr(ledger, "epoch_records", {})
    
    if not epoch_records:
        # Create empty file
        p.touch()
        return

    # Flatten logic
    rows: list[dict[str, object]] = []
    headers: set[str] = set()
    
    # Pre-scan for headers (optional, or just use hardcoded common ones then dynamic)
    # We want a stable order.
    # Common keys: epoch_id, epoch_index, status, distribution_status, summary.*
    
    for rec in epoch_records.values():
        row = rec.copy()
        
        # Flatten metrics/summary
        summary = row.pop("summary", None) or {}
        for k, v in summary.items():
            row[f"summary_{k}"] = v
            
        # Flatten checksums
        checksums = row.pop("checksums", None) or {}
        for k, v in checksums.items():
            row[f"checksum_{k}"] = v
            
        rows.append(row)
        headers.update(row.keys())
        
    # Sort headers for stability
    header_list = sorted(list(headers))
    # Move epoch_index, epoch_id to front if present
    for k in ["epoch_id", "epoch_index"]:
        if k in header_list:
            header_list.remove(k)
            header_list.insert(0, k)
            
    with p.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header_list)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

def export_ledger_distribution_checks_csv(
    checks: list[LedgerDistributionCheck],
    path: PathLike,
) -> None:
    """
    Export verification results to a CSV file.
    """
    if not checks:
        return
        
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    # Flatten checks for CSV if needed?
    # Prompt says columns: epoch_id, ok, total_delta, expected_total, max_agent_error, top_errors, input_hash
    # The check result doesn't have epoch_id inside it by default, we should probably inject it or 
    # expect the caller to pass it??
    # Wait, the verification helper returns a dict. It doesn't include epoch_id.
    # We should probably pass a list of checks where we added epoch_id.
    
    header = ["epoch_id", "ok", "total_delta", "expected_total", "max_agent_error", "top_errors", "input_hash"]
    
    with p.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for c in checks:
            # Filter to just header keys
            row = {k: c.get(k) for k in header}
            # top_errors is list, stringify
            if isinstance(row["top_errors"], list):
                row["top_errors"] = ";".join(row["top_errors"])
            for numeric_key in ("total_delta", "expected_total", "max_agent_error"):
                if row[numeric_key] is not None:
                    row[numeric_key] = exact_to_canonical_string(
                        row[numeric_key],
                        token=f"ledger_distribution_check_{numeric_key}_invalid",
                    )
            writer.writerow(row)
