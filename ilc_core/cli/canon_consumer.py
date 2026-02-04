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
    
    if not report["ok"]:
        return {
            "ok": False,
            "error": report.get("error", "Verification failed")
        }
    
    # Reload to extract counts (verify_canon_state verifies but doesn't return full payload)
    # We can trust the file now since verify passed
    try:
        with open(path, "r") as f:
            payload = json.load(f)
            
        return {
            "ok": True,
            "canon_hash": report["canon_hash"],
            "computed_hash": report["computed_hash"],
            "canon_export_version": payload.get("canon_export_version", "unknown"),
            "epoch_count": len(payload.get("epoch_records", {})),
            "snapshot_count": len(payload.get("stake_snapshots", {})),
            "balance_count": len(payload.get("balances", {})),
        }
    except Exception as e:
        return {
            "ok": False,
            "error": f"Failed to parse payload for summary: {str(e)}"
        }

def main() -> int:
    """CLI entrypoint for ilc-canon-summary."""
    parser = argparse.ArgumentParser(description="Summarize a canon_state.json file.")
    parser.add_argument("--path", required=True, help="Path to canon_state.json")
    
    args = parser.parse_args()
    
    summary = summarize_canon_state(args.path)
    
    # Strict deterministic JSON output
    print(json.dumps(summary, sort_keys=True))
    
    return 0 if summary["ok"] else 1

if __name__ == "__main__":
    sys.exit(main())
