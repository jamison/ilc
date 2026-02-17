"""
Canon Consumer Integration Helper.

Provides utilities for downstream tools to safely ingest and summarize
canon_state.json artifacts without mutating them.
"""

import json
import sys
import argparse
import logging
from typing import TypedDict, TypeAlias, cast
from os import PathLike

from ilc_core.ledger.canon_loader import verify_canon_state

CanonMeta: TypeAlias = dict[str, int | str | None]
logger = logging.getLogger(__name__)


class CanonSummary(TypedDict, total=False):
    ok: bool
    canon_hash: str | None
    computed_hash: str | None
    errors: list[str]
    meta: CanonMeta
    canon_export_version: str
    epoch_count: int
    snapshot_count: int
    balance_count: int


def _default_meta() -> CanonMeta:
    return {
        "canon_export_version": None,
        "epoch_count": None,
        "snapshot_count": None,
        "balance_count": None,
        "kpi_epoch_count": None,
        "kpi_snapshot_count": None,
        "kpi_balance_count": None,
    }


def _as_object_map(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        return cast(dict[str, object], value)
    return {}


def _coerce_optional_str(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _coerce_errors(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _coerce_meta(value: object) -> CanonMeta:
    meta = _default_meta()
    if not isinstance(value, dict):
        return meta

    value_map = cast(dict[str, object], value)
    for key in meta:
        candidate = value_map.get(key)
        if isinstance(candidate, (int, str)) or candidate is None:
            meta[key] = candidate
    return meta


def summarize_canon_state(path: str | PathLike[str]) -> CanonSummary:
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
    report = _as_object_map(verify_canon_state(path))
    report_ok = bool(report.get("ok", False))
    
    # Base response shape
    result: CanonSummary = {
        "ok": report_ok,
        "canon_hash": _coerce_optional_str(report.get("canon_hash")),
        "computed_hash": _coerce_optional_str(report.get("computed_hash")),
        "errors": _coerce_errors(report.get("errors")),
        "meta": _coerce_meta(report.get("meta")),
    }
    
    if not report_ok:
        return result
    
    # Reload to extract counts (verify_canon_state verifies but doesn't return full payload)
    try:
        with open(path, "r") as f:
            payload = _as_object_map(json.load(f))

        result.update({
            "canon_export_version": (
                payload.get("canon_export_version")
                if isinstance(payload.get("canon_export_version"), str)
                else "unknown"
            ),
            "epoch_count": len(_as_object_map(payload.get("epoch_records"))),
            "snapshot_count": len(_as_object_map(payload.get("stake_snapshots"))),
            "balance_count": len(_as_object_map(payload.get("balances"))),
        })
        return result
    except Exception as e:
        result["ok"] = False
        result["errors"].append(f"Failed to parse payload for summary: {str(e)}")
        return result

def _get_error_code(errors: list[str]) -> str:
    """Map error messages to stable error codes."""
    if not errors:
        return "E_UNKNOWN"
    
    error_msg = "; ".join(errors)
    if "File not found" in error_msg:
        return "E_FILE_NOT_FOUND"
    elif "Invalid JSON" in error_msg:
        return "E_INVALID_JSON"
    elif "Hash mismatch" in error_msg:
        return "E_HASH_MISMATCH"
    elif "Unsupported version" in error_msg:
        return "E_UNSUPPORTED_VERSION"
    return "E_UNKNOWN"

def main() -> int:
    """CLI entrypoint for ilc-canon-summary."""
    parser = argparse.ArgumentParser(description="Summarize a canon_state.json file.")
    parser.add_argument("--path", help="Path to canon_state.json (required unless --validate-export is used)")
    parser.add_argument("--print-hash", action="store_true", help="Include hashes in output")
    parser.add_argument("--quiet", action="store_true", help="Suppress stdout")
    parser.add_argument("--report", action="store_true", help="Emit full verification report as single-line JSON")
    parser.add_argument("--kpis", action="store_true", help="Emit single-line KPI summary")
    parser.add_argument("--diagnostics", action="store_true", help="Emit verbose error diagnostics to stderr (silent on success)")
    parser.add_argument("--audit-log", help="Append usage record to specified JSONL file")
    parser.add_argument("--validate-export", help="Validate a canon export JSON file")
    
    args = parser.parse_args()
    
    if args.validate_export:
        try:
            from ilc_core.ledger.canon_export_validate import validate_canon_export_v0_1
            
            with open(args.validate_export, "r") as f:
                doc = json.load(f)
                
            report = validate_canon_export_v0_1(doc)
            print(json.dumps(report, separators=(",", ":")))
            return 0 if report["ok"] else 1
            
        except FileNotFoundError:
            print(json.dumps({"ok": False, "errors": [f"File not found: {args.validate_export}"], "warnings": []}))
            return 1
        except json.JSONDecodeError:
            print(json.dumps({"ok": False, "errors": [f"Invalid JSON in file: {args.validate_export}"], "warnings": []}))
            return 1
        except Exception as e:
            print(json.dumps({"ok": False, "errors": [str(e)], "warnings": []}))
            return 1
    
    if not args.path:
        parser.error("the following arguments are required: --path")

    summary = summarize_canon_state(args.path)

    # Calculate error code if needed
    errors = summary.get("errors", [])
    error_code = _get_error_code(errors) if not summary.get("ok") else None

    # Diagnostics logic (stderr only)
    if args.diagnostics and not summary.get("ok"):
        error_msg = "; ".join(errors) if errors else "Unknown error"
        print(
            f"diagnostics=on canon_path={args.path} code={error_code} error_message={error_msg}",
            file=sys.stderr,
        )

    # Audit logging logic (append to file)
    if args.audit_log:
        try:
            from datetime import datetime, timezone
            from pathlib import Path
            
            # Prepare record
            record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "canon_path": args.path,
                "ok": summary.get("ok", False),
                "canon_hash": summary.get("canon_hash"),
                "error_code": error_code
            }
            
            # Write to file
            log_path = Path(args.audit_log)
            if not log_path.parent.exists():
                log_path.parent.mkdir(parents=True, exist_ok=True)
                
            with open(log_path, "a", encoding="utf-8") as f:
                json.dump(record, f, separators=(",", ":"))
                f.write("\n")
        except Exception as exc:
            # Audit logging failures should not break main execution flow
            logger.debug("canon_consumer_audit_log_write_skipped error=%s", exc)

    if args.report:
        # Report mode: emit single-line JSON with stable key order
        report = _as_object_map(verify_canon_state(args.path))
        meta = _coerce_meta(report.get("meta"))
        ordered_report = {
            "ok": bool(report.get("ok", False)),
            "canon_hash": _coerce_optional_str(report.get("canon_hash")),
            "computed_hash": _coerce_optional_str(report.get("computed_hash")),
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
