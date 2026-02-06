
import argparse
import json
import sys
from pathlib import Path

from ilc_core.ledger.canon_bundle_replay_verify import replay_verify

def main() -> int:
    parser = argparse.ArgumentParser(description="Replay-verify a bundle against an audit artifact.")
    parser.add_argument("--bundle", required=True, help="Path to the bundle directory")
    parser.add_argument("--audit", required=True, help="Path to audit JSON file")
    
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
        print(json.dumps(result, separators=(",", ":"), sort_keys=False))
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
        print(json.dumps(result, separators=(",", ":"), sort_keys=False))
        return 1
    
    # Run replay verification
    result = replay_verify(bundle_path, audit)
    
    print(json.dumps(result, separators=(",", ":"), sort_keys=False))
    return 0 if result.get("replay_matches", False) else 1

if __name__ == "__main__":
    sys.exit(main())
