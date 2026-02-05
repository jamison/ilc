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
        "errors": report.get("errors", [])
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
    
    args = parser.parse_args()
    
    summary = summarize_canon_state(args.path)

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
