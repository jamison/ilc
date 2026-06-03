# SPDX-License-Identifier: AGPL-3.0-only
import argparse
import json
import sys
from pathlib import Path
from ilc_core.ledger.canon_loader import verify_canon_state

def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a canon_state.json file.")
    parser.add_argument("--path", required=True, help="Path to canon_state.json")
    parser.add_argument("--print-hash", action="store_true", help="Include hashes in output")
    parser.add_argument("--quiet", action="store_true", help="Suppress stdout")
    
    args = parser.parse_args()
    
    # Run verification (does not throw)
    report = verify_canon_state(args.path)
    
    # Filter output if needed
    if not args.print_hash:
        report.pop("canon_hash", None)
        report.pop("computed_hash", None)
        
    # Output
    if not args.quiet:
        print(json.dumps(report, sort_keys=True))
        
    # Exit Code
    return 0 if report.get("ok") else 1

if __name__ == "__main__":
    sys.exit(main())
