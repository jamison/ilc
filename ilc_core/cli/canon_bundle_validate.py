# SPDX-License-Identifier: AGPL-3.0-only

import argparse
import json
import os
import sys
from pathlib import Path
from typing import NoReturn

from ilc_core.ledger.canon_export_bundle_validate import validate_canon_export_bundle
from ilc_core.ledger.canon_export_bundle_sign import load_key_from_file
from ilc_core.ledger.canon_export_bundle_verify_sig import verify_manifest_signature


def _apply_signature_verification(report: dict, bundle_path: Path, args: argparse.Namespace) -> None:
    if not args.verify_signature:
        report.setdefault("warnings", []).append("Signature verification skipped")
        _allow_empty_key_registry(report)
        return
    if not args.key_file:
        report["ok"] = False
        report["errors"].append("key_missing")
        return
    try:
        key = load_key_from_file(Path(args.key_file))
        if not verify_manifest_signature(bundle_path, key):
            report["ok"] = False
            report["errors"].append("signature_mismatch")
            return
        _allow_empty_key_registry(report)
    except FileNotFoundError as exc:
        report["ok"] = False
        if "manifest.json" in str(exc):
            report["errors"].append("manifest_missing")
        else:
            report["errors"].append("signature_missing")
    except ValueError as exc:
        report["ok"] = False
        if str(exc) == "invalid_key_file":
            report["errors"].append("invalid_key_file")
        else:
            report["errors"].append(f"signature_verification_error:{exc}")
    except Exception as exc:
        report["ok"] = False
        report["errors"].append(f"signature_verification_error:{exc}")


def _allow_empty_key_registry(report: dict) -> None:
    if os.environ.get("ILC_ALLOW_EMPTY_KEY_REGISTRY") != "1":
        return
    report["errors"] = [
        error for error in report.get("errors", []) if error != "unknown_key_id"
    ]
    report["ok"] = not report["errors"]


def _write_optional_report(report: dict, bundle_path: Path, report_arg: str | None) -> None:
    if not report_arg:
        return
    try:
        from ilc_core.ledger.canon_export_bundle_report import render_bundle_report

        report_path = Path(report_arg)
        if report_path.is_dir():
            report_path = report_path / "bundle_validation_report.md"
        if not report_path.parent.exists():
            report_path.parent.mkdir(parents=True, exist_ok=True)
        md_content = render_bundle_report(str(bundle_path), report)
        report_path.write_text(md_content, encoding="utf-8")
    except Exception as e:
        # Report generation failure should not affect exit code or JSON output.
        print(f"Warning: Failed to write report: {e}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a canon export bundle.")
    parser.add_argument("--bundle", required=True, help="Path to the bundle directory")
    parser.add_argument("--report", help="Path to write Markdown validation report")
    parser.add_argument("--verify-signature", action="store_true", help="Verify manifest.sig HMAC")
    parser.add_argument("--key-file", help="Path to base64 key file (required for signature verification)")

    args = parser.parse_args()
    bundle_path = Path(args.bundle).resolve()
    
    try:
        report = validate_canon_export_bundle(bundle_path)
    except Exception as e:
        # Fallback for unexpected crashes in validator
        report = {
            "ok": False,
            "errors": [f"Validator crashed: {e}"],
            "warnings": []
        }

    # Signature Verification Logic
    _apply_signature_verification(report, bundle_path, args)

    # Single-line JSON output
    print(json.dumps(report, separators=(",", ":"), sort_keys=True, allow_nan=False))

    # Optional Report Generation
    _write_optional_report(report, bundle_path, args.report)
    
    return 0 if report["ok"] else 1

if __name__ == "__main__":
    sys.exit(main())
