"""
Canon Consumer Integration Helper.

Provides utilities for downstream tools to safely ingest and summarize
canon_state.json artifacts without mutating them.
"""

import json
import sys
import argparse
from typing import Dict, Any, Union
from os import PathLike

from ilc_core.ledger.canon_loader import verify_canon_state

def summarize_canon_state(path: Union[str, PathLike]) -> Dict[str, Any]:
    """
    Return a deterministic summary dict for canon_state.json.
    
    Verifies the file integrity first.
    
    Args:
        path: Path to canon_state.json
        
    Returns:
        Dict containing:
        - ok (bool): True if verified
        - canon_hash (str, optional): Hash from file
        - computed_hash (str, optional): Hash computed from content
        - canon_export_version (str, optional): Version string
        - epoch_count (int, optional): Number of epoch records
        - snapshot_count (int, optional): Number of stake snapshots
        - balance_count (int, optional): Number of agent balances
        - error (str, optional): Error message if verification failed
    """
    report = verify_canon_state(path)
    
    # Base response shape
    result = {
        "ok": report["ok"],
        "canon_hash": report.get("canon_hash"),
        "computed_hash": report.get("computed_hash"),
        "errors": report.get("errors", []),
        "meta": report.get("meta", {
            "canon_export_version": None,
            "epoch_count": None,
            "snapshot_count": None,
            "balance_count": None,
            "kpi_epoch_count": None,
            "kpi_snapshot_count": None,
            "kpi_balance_count": None
        })
    }
    
    if not report["ok"]:
        return result
    
    # Reload to extract counts (verify_canon_state verifies but doesn't return full payload)
    try:
        with open(path, "r") as f:
            payload = json.load(f)
            
        result.update({
            "canon_export_version": payload.get("canon_export_version", "unknown"),
            "epoch_count": len(payload.get("epoch_records", {})),
            "snapshot_count": len(payload.get("stake_snapshots", {})),
            "balance_count": len(payload.get("balances", {})),
        })
        return result
    except Exception as e:
        result["ok"] = False
        result["errors"].append(f"Failed to parse payload for summary: {str(e)}")
        return result

def main() -> int:
    """CLI entrypoint for ilc-canon-summary."""
    parser = argparse.ArgumentParser(description="Summarize a canon_state.json file.")
    parser.add_argument("--path", required=True, help="Path to canon_state.json")
    parser.add_argument("--print-hash", action="store_true", help="Include hashes in output")
    parser.add_argument("--quiet", action="store_true", help="Suppress stdout")
    parser.add_argument("--report", action="store_true", help="Emit full verification report as single-line JSON")
    parser.add_argument("--kpis", action="store_true", help="Emit single-line KPI summary")
    parser.add_argument("--diagnostics", action="store_true", help="Emit verbose error diagnostics to stderr (silent on success)")
    
    args = parser.parse_args()
    
    summary = summarize_canon_state(args.path)

    # Diagnostics logic (stderr only)
    if args.diagnostics and not summary.get("ok"):
        errors = summary.get("errors", [])
        error_msg = "; ".join(errors) if errors else "Unknown error"

        # Map to stable error code
        code = "E_UNKNOWN"
        if "File not found" in error_msg:
            code = "E_FILE_NOT_FOUND"
        elif "Invalid JSON" in error_msg:
            code = "E_INVALID_JSON"
        elif "Hash mismatch" in error_msg:
            code = "E_HASH_MISMATCH"
        elif "Unsupported version" in error_msg:
            code = "E_UNSUPPORTED_VERSION"

        print(
            f"diagnostics=on canon_path={args.path} code={code} error_message={error_msg}",
            file=sys.stderr,
        )

    if args.report:
        # Report mode: emit single-line JSON with stable key order
        report = verify_canon_state(args.path)
        meta = report.get(
            "meta",
            {
                "canon_export_version": None,
                "epoch_count": None,
                "snapshot_count": None,
                "balance_count": None,
                "kpi_epoch_count": None,
                "kpi_snapshot_count": None,
                "kpi_balance_count": None,
            },
        )
        errors = report.get("errors", [])
        ordered_report = {
            "ok": report.get("ok", False),
            "canon_hash": report.get("canon_hash"),
            "computed_hash": report.get("computed_hash"),
            "errors": errors,
            "meta": meta,
        }
        print(json.dumps(ordered_report, separators=(",", ":")))
        return 0 if ordered_report["ok"] else 1

    if args.kpis and not args.quiet:
        # KPI mode: emit single-line summary
        # Format: kpis=epochs:3 snapshots:2 balances:4
        meta = summary.get("meta", {})
        epochs = meta.get("kpi_epoch_count")
        snapshots = meta.get("kpi_snapshot_count")
        balances = meta.get("kpi_balance_count")
        
        # Handle None values elegantly for display
        e_str = str(epochs) if epochs is not None else "None"
        s_str = str(snapshots) if snapshots is not None else "None"
        b_str = str(balances) if balances is not None else "None"
        
        print(f"kpis=epochs:{e_str} snapshots:{s_str} balances:{b_str}")
        return 0 if summary.get("ok") else 1

    # Format output as single line: status=ok canon_path=... canon_hash=... errors=[]
    status = "ok" if summary.get("ok") else "fail"
    canon_hash = summary.get("canon_hash") or "unknown"
    # Shorten hash for display
    canon_hash_short = canon_hash[:12] if canon_hash and canon_hash != "unknown" else "unknown"
    
    errors = summary.get("errors", [])
    # Format errors as python list repr for easy parsing
    errors_str = str(errors).replace("'", '"')
    
    output = (
        f"status={status} "
        f"canon_path={args.path} "
        f"canon_hash={canon_hash_short} "
        f"errors={errors_str}"
    )

    if not args.quiet:
        print(output)

    return 0 if summary.get("ok") else 1

if __name__ == "__main__":
    sys.exit(main())
