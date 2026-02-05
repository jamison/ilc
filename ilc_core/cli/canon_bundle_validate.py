
import argparse
import json
import sys
from pathlib import Path
from typing import NoReturn

from ilc_core.ledger.canon_export_bundle_validate import validate_canon_export_bundle

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a canon export bundle.")
    parser.add_argument("--bundle", required=True, help="Path to the bundle directory")
    
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
    
    # Single-line JSON output
    print(json.dumps(report, separators=(",", ":"), sort_keys=False))
    
    return 0 if report["ok"] else 1

if __name__ == "__main__":
    sys.exit(main())
