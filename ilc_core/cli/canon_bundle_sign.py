
import argparse
import json
import sys
from pathlib import Path

from ilc_core.ledger.canon_export_bundle_sign import sign_manifest, load_key_from_file


def _emit_report(report: dict) -> int:
    print(json.dumps(report, separators=(",", ":"), sort_keys=False))
    return 0 if report["ok"] else 1


def _fail(code: str) -> dict:
    return {"ok": False, "errors": [code], "warnings": []}

def main() -> int:
    parser = argparse.ArgumentParser(description="Sign a canon export bundle.")
    parser.add_argument("--bundle", required=True, help="Path to the bundle directory")
    parser.add_argument("--key-file", help="Path to base64 key file")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing signature")
    
    args = parser.parse_args()
    
    try:
        bundle_path = Path(args.bundle).resolve()
        if not bundle_path.exists() or not bundle_path.is_dir():
            return _emit_report(_fail("bundle_missing"))

        if not (bundle_path / "manifest.json").exists():
            return _emit_report(_fail("manifest_missing"))

        if not args.key_file:
            return _emit_report(_fail("key_missing"))

        key_path = Path(args.key_file)
        if not key_path.exists():
            return _emit_report(_fail("key_missing"))

        try:
            key = load_key_from_file(key_path)
            sign_manifest(bundle_path, key, overwrite=args.overwrite)
        except ValueError:
            return _emit_report(_fail("invalid_key_file"))
        except FileExistsError:
            return _emit_report(_fail("signature_exists"))

    except Exception as e:
        report = _fail("unexpected_error")
        report["warnings"].append(f"internal_error:{e}")
        return _emit_report(report)

    return _emit_report({"ok": True, "errors": [], "warnings": []})

if __name__ == "__main__":
    sys.exit(main())
