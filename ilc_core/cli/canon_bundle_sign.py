
import argparse
import json
import sys
from pathlib import Path
from typing import NoReturn

from ilc_core.ledger.canon_export_bundle_sign import sign_manifest, load_key_from_file

def main() -> int:
    parser = argparse.ArgumentParser(description="Sign a canon export bundle.")
    parser.add_argument("--bundle", required=True, help="Path to the bundle directory")
    parser.add_argument("--key-file", required=True, help="Path to base64 key file")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing signature")
    
    args = parser.parse_args()
    
    # JSON report structure
    report = {"ok": True, "errors": [], "warnings": []}
    
    try:
        bundle_path = Path(args.bundle).resolve()
        if not bundle_path.exists() or not bundle_path.is_dir():
            report["ok"] = False
            report["errors"].append("bundle_missing")
        else:
            # Pre-check manifest to strictly match error codes
            if not (bundle_path / "manifest.json").exists():
                 report["ok"] = False
                 report["errors"].append("manifest_missing")
            else:
                 key_path = Path(args.key_file)
                 if not key_path.exists():
                      report["ok"] = False
                      report["errors"].append("key_missing")
                 else:
                      try:
                           key = load_key_from_file(key_path)
                           sign_manifest(bundle_path, key, overwrite=args.overwrite)
                      except ValueError as e:
                           report["ok"] = False
                           if str(e) == "invalid_key_file" or "invalid_key_file" in str(e):
                                report["errors"].append("invalid_key_file")
                           elif "empty" in str(e): # Handle "Key file is empty"
                                report["errors"].append("invalid_key_file")
                           else:
                                report["errors"].append("invalid_key_file") # Catch-all for base64 errors
                      except FileExistsError:
                           report["ok"] = False
                           report["errors"].append("signature_exists")

    except Exception as e:
        report["ok"] = False
        report["errors"].append("unexpected_error")
        # In a real unexpected error we might want to log to stderr, 
        # but per prompt "No stderr output on expected errors. Only unexpected internal exceptions may use stderr."
        # The prompt says: "unexpected_error (optional fallback for non-expected exceptions)"
        # and "No stderr output on expected errors."
        print(f"Internal error: {e}", file=sys.stderr)

    print(json.dumps(report, separators=(",", ":"), sort_keys=True))
    return 0 if report["ok"] else 1

if __name__ == "__main__":
    sys.exit(main())
