# SPDX-License-Identifier: AGPL-3.0-or-later

import argparse
import json
import sys
from pathlib import Path

from ilc_core.ledger.canon_bundle_replay_verify import replay_verify
from ilc_core.ledger.canon_bundle_replay_report import render_replay_report

def _write_report(bundle_path: Path, audit_path: Path, result: dict, report_arg: str) -> list:
    """Write replay report if --report is set. Returns list of warnings."""
    warnings = []
    try:
        report_path = Path(report_arg)
        if report_path.is_dir():
            report_path = report_path / "bundle_replay_report.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        md_content = render_replay_report(
            bundle_path=str(bundle_path),
            audit_path=str(audit_path),
            export_root=None,
            replay_json=result,
            mismatches=result.get("mismatch", {}),
            warnings=result.get("warnings", []),
            errors=result.get("errors", []),
        )
        report_path.write_text(md_content, encoding="utf-8")
    except Exception:
        warnings.append("report_write_failed")
    return warnings

def main() -> int:
    parser = argparse.ArgumentParser(description="Replay-verify a bundle against an audit artifact.")
    parser.add_argument("--bundle", required=True, help="Path to the bundle directory")
    parser.add_argument("--audit", required=True, help="Path to audit JSON file")
    parser.add_argument("--report", help="Path to write Markdown replay report")
    
    args = parser.parse_args()
    
    bundle_path = Path(args.bundle).resolve()
    audit_path = Path(args.audit)
    
    # Load audit JSON
    if not audit_path.exists():
        result = {
            "ok": False,
            "errors": ["audit_file_missing"],
            "warnings": [],
            "replay_matches": False,
            "mismatch": {}
        }
        if args.report:
            extra_warnings = _write_report(bundle_path, audit_path, result, args.report)
            if extra_warnings:
                result["warnings"].extend(extra_warnings)
        json_output = json.dumps(
            result,
            separators=(",", ":"),
            sort_keys=True,
            allow_nan=False,
        )
        print(json_output)
        return 1
    
    try:
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        result = {
            "ok": False,
            "errors": ["audit_parse_error"],
            "warnings": [],
            "replay_matches": False,
            "mismatch": {}
        }
        if args.report:
            extra_warnings = _write_report(bundle_path, audit_path, result, args.report)
            if extra_warnings:
                result["warnings"].extend(extra_warnings)
        json_output = json.dumps(
            result,
            separators=(",", ":"),
            sort_keys=True,
            allow_nan=False,
        )
        print(json_output)
        return 1
    
    # Run replay verification
    result = replay_verify(bundle_path, audit)
    
    # Write report if requested
    if args.report:
        extra_warnings = _write_report(bundle_path, audit_path, result, args.report)
        if extra_warnings:
            result["warnings"].extend(extra_warnings)
    
    json_output = json.dumps(
        result,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    )
    print(json_output)
    
    return 0 if result.get("replay_matches", False) else 1

if __name__ == "__main__":
    sys.exit(main())
