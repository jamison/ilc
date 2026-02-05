
import argparse
import json
import sys
from pathlib import Path
from typing import NoReturn

from ilc_core.ledger.canon_export_bundle_validate import validate_canon_export_bundle
from ilc_core.ledger.canon_export_bundle_sign import load_key_from_file
from ilc_core.ledger.canon_export_bundle_verify_sig import verify_manifest_signature

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
    if args.verify_signature:
        if not args.key_file:
             report["ok"] = False
             report["errors"].append("Missing --key-file for signature verification")
        else:
            try:
                key = load_key_from_file(Path(args.key_file))
                if not verify_manifest_signature(bundle_path, key):
                     report["ok"] = False
                     report["errors"].append("Signature mismatch")
            except FileNotFoundError:
                report["ok"] = False
                report["errors"].append("Signature verification failed: manifest.sig not found")
            except Exception as e:
                report["ok"] = False
                report["errors"].append(f"Signature verification error: {e}")
    else:
        report.setdefault("warnings", []).append("Signature verification skipped")
    
    # Single-line JSON output
    print(json.dumps(report, separators=(",", ":"), sort_keys=False))
    
    # Optional Report Generation
    if args.report:
        try:
            from ilc_core.ledger.canon_export_bundle_report import render_bundle_report
            
            report_path = Path(args.report)
            if report_path.is_dir():
                report_path = report_path / "bundle_validation_report.md"
            
            # Create parent dirs if needed
            if not report_path.parent.exists():
                report_path.parent.mkdir(parents=True, exist_ok=True)
                
            md_content = render_bundle_report(str(bundle_path), report)
            report_path.write_text(md_content, encoding="utf-8")
            
        except Exception as e:
            # Report generation failure should not affect exit code or JSON output
            print(f"Warning: Failed to write report: {e}", file=sys.stderr)
    
    return 0 if report["ok"] else 1

if __name__ == "__main__":
    sys.exit(main())
