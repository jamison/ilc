
import argparse
import json
import sys
from pathlib import Path

from ilc_core.ledger.canon_export_bundle_validate import validate_canon_export_bundle
from ilc_core.ledger.canon_export_bundle_sign import sign_manifest, load_key_from_file
from ilc_core.ledger.canon_export_bundle_verify_sig import verify_manifest_signature
from ilc_core.ledger.canon_bundle_pipeline_report import render_pipeline_report
from ilc_core.ledger.canon_bundle_audit_artifact import create_audit_artifact, write_audit_artifact

def _set_error(report, code: str) -> None:
    report["ok"] = False
    report["errors"].append(code)

def _resolve_report_paths(report_arg: Path) -> tuple[Path, Path]:
    """Resolve report and audit paths from the --report argument."""
    if report_arg.is_dir():
        report_path = report_arg / "bundle_pipeline_report.md"
        audit_path = report_arg / "bundle_pipeline_audit.json"
    else:
        report_path = report_arg
        audit_path = report_arg.with_name("bundle_pipeline_audit.json")
    return report_path, audit_path

def _extract_key_metadata(bundle_path: Path) -> dict | None:
    manifest_path = bundle_path / "manifest.json"
    if not manifest_path.exists():
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not (manifest.get("key_id") or manifest.get("sig_alg") or manifest.get("signed_at")):
        return None
    key_id = manifest.get("key_id")
    key_status = None
    if key_id:
        from ilc_core.ledger.canon_bundle_key_registry import get_registry
        registry = get_registry()
        key_status = registry.status(key_id)
    return {
        "key_id": key_id,
        "sig_alg": manifest.get("sig_alg"),
        "signed_at": manifest.get("signed_at"),
        "key_status": key_status,
    }

def _write_report(bundle_path: Path, report, report_path: Path, json_output: str) -> tuple[bool, str | None]:
    """Write report file and return (success, content)."""
    try:
        report_path.parent.mkdir(parents=True, exist_ok=True)

        key_metadata = _extract_key_metadata(bundle_path)
        md_content = render_pipeline_report(
            str(bundle_path),
            report,
            json_output=json_output,
            key_metadata=key_metadata,
        )
        report_path.write_text(md_content, encoding="utf-8")
        return True, md_content
    except Exception:
        return False, None


def _write_audit(bundle_path: Path, report, audit_path: Path, json_output: str, report_path: Path | None, report_content: str | None) -> None:
    """Write audit artifact file; append warning on failure."""
    try:
        audit = create_audit_artifact(
            bundle_path=bundle_path,
            report=report,
            report_path=report_path,
            audit_path=audit_path,
            json_output=json_output,
            report_content=report_content,
        )
        if not write_audit_artifact(audit, audit_path):
            report.setdefault("warnings", []).append("audit_write_failed")
    except Exception:
        report.setdefault("warnings", []).append("audit_write_failed")

def _prepare_bundle(args, report) -> tuple[Path | None, bool]:
    bundle_path = Path(args.bundle).resolve()
    report["bundle_path"] = str(bundle_path)
    if not bundle_path.exists() or not bundle_path.is_dir():
        _set_error(report, "bundle_missing")
        return None, False
    manifest_path = bundle_path / "manifest.json"
    if not manifest_path.exists():
        _set_error(report, "manifest_missing")
        return None, False
    return bundle_path, True

def _run_validation(bundle_path: Path, report, steps) -> bool:
    validation_result = validate_canon_export_bundle(bundle_path)
    steps["validate"] = True
    if validation_result.get("ok", False):
        return True
    report["ok"] = False
    report["errors"].extend(validation_result.get("errors", []))
    report["warnings"].extend(validation_result.get("warnings", []))
    return False

def _load_key(args, report):
    key_path = Path(args.key_file)
    if not key_path.exists():
        _set_error(report, "key_missing")
        return None
    try:
        return load_key_from_file(key_path)
    except ValueError:
        _set_error(report, "invalid_key_file")
        return None

def _handle_existing_signature(bundle_path: Path, key, report, steps) -> bool:
    try:
        if verify_manifest_signature(bundle_path, key):
            steps["verify"] = True
            report["warnings"].append("signature_exists")
            return False
        _set_error(report, "signature_mismatch")
        return False
    except FileNotFoundError:
        _set_error(report, "signature_missing")
        return False

def _sign_bundle(bundle_path: Path, key, report, steps, overwrite: bool) -> bool:
    try:
        sign_manifest(bundle_path, key, overwrite=overwrite)
        steps["sign"] = True
        return True
    except FileExistsError:
        _set_error(report, "signature_exists")
        return False

def _verify_signature(bundle_path: Path, key, report, steps) -> bool:
    try:
        if not verify_manifest_signature(bundle_path, key):
            _set_error(report, "signature_mismatch")
            return False
        steps["verify"] = True
        return True
    except FileNotFoundError:
        _set_error(report, "signature_missing")
        return False

def _handle_signing(args, bundle_path: Path, report, steps) -> bool:
    if not args.key_file:
        report["warnings"].append("signature_verification_skipped")
        return True
    key = _load_key(args, report)
    if key is None:
        return False
    sig_path = bundle_path / "manifest.sig"
    if sig_path.exists() and not args.overwrite:
        return _handle_existing_signature(bundle_path, key, report, steps)
    if not _sign_bundle(bundle_path, key, report, steps, args.overwrite):
        return False
    return _verify_signature(bundle_path, key, report, steps)

def _finalize(args, report) -> int:
    """Write report/audit (if requested), print JSON, and return exit code."""
    bundle_path = Path(report.get("bundle_path", ""))
    json_output = json.dumps(report, separators=(",", ":"), sort_keys=False)

    if args.report:
        report_arg_path = Path(args.report)
        report_path, audit_path = _resolve_report_paths(report_arg_path)

        # Optimistically mark report as true for JSON/report alignment.
        report["steps"]["report"] = True
        json_output = json.dumps(report, separators=(",", ":"), sort_keys=False)
        report_ok, report_content = _write_report(bundle_path, report, report_path, json_output)
        if not report_ok:
            report["steps"]["report"] = False
            report.setdefault("warnings", []).append("report_write_failed")
            json_output = json.dumps(report, separators=(",", ":"), sort_keys=False)
            report_content = None
            report_path = None

        _write_audit(bundle_path, report, audit_path, json_output, report_path, report_content)

    print(json_output)
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
        bundle_path, ok = _prepare_bundle(args, report)
        if not ok:
            return _finalize(args, report)
        if not _run_validation(bundle_path, report, steps):
            return _finalize(args, report)
        if not _handle_signing(args, bundle_path, report, steps):
            return _finalize(args, report)
            
    except Exception as e:
        report["ok"] = False
        report["errors"].append("pipeline_failed")
        report.setdefault("warnings", []).append(f"pipeline_internal_error:{e}")

    return _finalize(args, report)

if __name__ == "__main__":
    sys.exit(main())
