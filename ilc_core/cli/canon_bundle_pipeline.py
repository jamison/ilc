
import argparse
import json
import sys
from pathlib import Path

from ilc_core.ledger.canon_export_bundle_validate import validate_canon_export_bundle
from ilc_core.ledger.canon_export_bundle_sign import sign_manifest, load_key_from_file
from ilc_core.ledger.canon_export_bundle_verify_sig import verify_manifest_signature
from ilc_core.ledger.canon_bundle_pipeline_report import render_pipeline_report
from ilc_core.ledger.canon_bundle_audit_artifact import create_audit_artifact, write_audit_artifact

def _write_report_and_audit(args, report, json_output):
    """Write report and audit artifact if --report is set. Always called before exit."""
    if not args.report:
        return
    
    bundle_path = Path(report.get("bundle_path", ""))
    report_arg_path = Path(args.report)
    
    # Determine report path
    if report_arg_path.is_dir():
        report_path = report_arg_path / "bundle_pipeline_report.md"
        audit_path = report_arg_path / "bundle_pipeline_audit.json"
    else:
        report_path = report_arg_path
        audit_path = report_arg_path.with_name("bundle_pipeline_audit.json")
    
    # Write report
    md_content = None
    try:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report["steps"]["report"] = True
        md_content = render_pipeline_report(
            str(bundle_path),
            report,
            json_output=json_output,
        )
        report_path.write_text(md_content, encoding="utf-8")
    except Exception:
        report["steps"]["report"] = False
        report.setdefault("warnings", []).append("report_write_failed")
    
    # Write audit artifact
    try:
        audit = create_audit_artifact(
            bundle_path=bundle_path,
            report=report,
            report_path=report_path if report["steps"]["report"] else None,
            audit_path=audit_path,
            json_output=json_output,
            report_content=md_content,
        )
        if not write_audit_artifact(audit, audit_path):
            report.setdefault("warnings", []).append("audit_write_failed")
    except Exception:
        report.setdefault("warnings", []).append("audit_write_failed")

def _finalize(args, report) -> int:
    """Print JSON, write report and audit, and return exit code."""
    json_output = json.dumps(report, separators=(",", ":"), sort_keys=False)
    print(json_output)
    _write_report_and_audit(args, report, json_output)
    return 0 if report["ok"] else 1

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
            return _finalize(args, report)

        manifest_path = bundle_path / "manifest.json"
        if not manifest_path.exists():
            report["ok"] = False
            report["errors"].append("manifest_missing")
            return _finalize(args, report)
        
        # Step 2: Validate bundle
        validation_result = validate_canon_export_bundle(bundle_path)
        steps["validate"] = True
        if not validation_result.get("ok", False):
            report["ok"] = False
            report["errors"].extend(validation_result.get("errors", []))
            report["warnings"].extend(validation_result.get("warnings", []))
            return _finalize(args, report)
        
        # Step 3: Signing (optional)
        if args.key_file:
            key_path = Path(args.key_file)
            if not key_path.exists():
                report["ok"] = False
                report["errors"].append("key_missing")
                return _finalize(args, report)
            try:
                key = load_key_from_file(key_path)
            except ValueError:
                report["ok"] = False
                report["errors"].append("invalid_key_file")
                return _finalize(args, report)
            
            sig_path = bundle_path / "manifest.sig"
            if sig_path.exists() and not args.overwrite:
                try:
                    if verify_manifest_signature(bundle_path, key):
                        report["ok"] = False
                        report["errors"].append("signature_exists")
                    else:
                        report["ok"] = False
                        report["errors"].append("signature_mismatch")
                except FileNotFoundError:
                    report["ok"] = False
                    report["errors"].append("signature_missing")
                return _finalize(args, report)

            # Sign
            try:
                sign_manifest(bundle_path, key, overwrite=args.overwrite)
                steps["sign"] = True
            except FileExistsError:
                report["ok"] = False
                report["errors"].append("signature_exists")
                return _finalize(args, report)
            
            # Verify
            try:
                if not verify_manifest_signature(bundle_path, key):
                    report["ok"] = False
                    report["errors"].append("signature_mismatch")
                    return _finalize(args, report)
                steps["verify"] = True
            except FileNotFoundError:
                report["ok"] = False
                report["errors"].append("signature_missing")
                return _finalize(args, report)
        else:
            report["warnings"].append("signature_verification_skipped")
            
    except Exception as e:
        report["ok"] = False
        report["errors"].append("pipeline_failed")
        print(f"Internal error: {e}", file=sys.stderr)

    return _finalize(args, report)

if __name__ == "__main__":
    sys.exit(main())
