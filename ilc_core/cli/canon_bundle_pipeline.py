
import argparse
import json
import sys
from pathlib import Path

from ilc_core.ledger.canon_export_bundle_validate import validate_canon_export_bundle
from ilc_core.ledger.canon_export_bundle_sign import sign_manifest, load_key_from_file
from ilc_core.ledger.canon_export_bundle_verify_sig import verify_manifest_signature
from ilc_core.ledger.canon_export_bundle_report import render_bundle_report

def main() -> int:
    parser = argparse.ArgumentParser(description="Run the canon bundle pipeline.")
    parser.add_argument("--bundle", required=True, help="Path to the bundle directory")
    parser.add_argument("--key-file", help="Path to base64 key file for signing/verification")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing signature")
    parser.add_argument("--report", help="Path to write Markdown validation report")
    
    args = parser.parse_args()
    
    steps = {"validate": False, "sign": False, "verify": False, "report": False}
    report = {
        "ok": True,
        "errors": [],
        "warnings": [],
        "steps": steps,
        "bundle_path": "",
    }
    
    try:
        bundle_path = Path(args.bundle).resolve()
        report["bundle_path"] = str(bundle_path)
        
        # Step 1: Check bundle exists and is a directory
        if not bundle_path.exists() or not bundle_path.is_dir():
            report["ok"] = False
            report["errors"].append("bundle_missing")
            print(json.dumps(report, separators=(",", ":"), sort_keys=False))
            return 1
        
        # Step 2: Validate bundle
        validation_result = validate_canon_export_bundle(bundle_path)
        steps["validate"] = True
        if not validation_result.get("ok", False):
            report["ok"] = False
            report["errors"].extend(validation_result.get("errors", []))
            report["warnings"].extend(validation_result.get("warnings", []))
            print(json.dumps(report, separators=(",", ":"), sort_keys=False))
            return 1
        
        # Step 3: Signing (optional)
        if args.key_file:
            key_path = Path(args.key_file)
            if not key_path.exists():
                report["ok"] = False
                report["errors"].append("key_missing")
                print(json.dumps(report, separators=(",", ":"), sort_keys=False))
                return 1
            try:
                key = load_key_from_file(key_path)
            except ValueError:
                report["ok"] = False
                report["errors"].append("invalid_key_file")
                print(json.dumps(report, separators=(",", ":"), sort_keys=False))
                return 1
            
            # Sign
            try:
                sign_manifest(bundle_path, key, overwrite=args.overwrite)
                steps["sign"] = True
            except FileExistsError:
                report["ok"] = False
                report["errors"].append("signature_exists")
                print(json.dumps(report, separators=(",", ":"), sort_keys=False))
                return 1
            
            # Verify
            try:
                if not verify_manifest_signature(bundle_path, key):
                    report["ok"] = False
                    report["errors"].append("signature_mismatch")
                    print(json.dumps(report, separators=(",", ":"), sort_keys=False))
                    return 1
                steps["verify"] = True
            except FileNotFoundError:
                report["ok"] = False
                report["errors"].append("signature_missing")
                print(json.dumps(report, separators=(",", ":"), sort_keys=False))
                return 1
        else:
            report["warnings"].append("signature_verification_skipped")
        
        # Step 4: Report (optional)
        if args.report:
            report_path = Path(args.report)
            report_path.parent.mkdir(parents=True, exist_ok=True)
            md_content = render_bundle_report(str(bundle_path), validation_result)
            report_path.write_text(md_content, encoding="utf-8")
            steps["report"] = True
            
    except Exception as e:
        report["ok"] = False
        report["errors"].append("pipeline_failed")
        print(f"Internal error: {e}", file=sys.stderr)

    print(json.dumps(report, separators=(",", ":"), sort_keys=False))
    return 0 if report["ok"] else 1

if __name__ == "__main__":
    sys.exit(main())
