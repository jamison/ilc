"""
ILC Constitution Cluster A - Replay Proof Package CLI.
Phase 144.

Provides command-line interface for building and verifying
canonical replay proof packages.
"""

import sys
import json
import argparse
from typing import Dict, Any, Optional

from ilc_core.protocol.ilc_cluster_a_replay_proof_package import (
    build_cluster_a_replay_proof_package,
    verify_cluster_a_replay_proof_package,
    E_SCHEMA_INVALID_PACKAGE
)

# Exit Codes
EXIT_OK = 0
EXIT_VERIFICATION_FAILED = 1
EXIT_ERROR = 2

# Failure Tokens
E_FILE_NOT_FOUND = "file_not_found"
E_INVALID_JSON = "invalid_json"
E_NOT_OBJECT = "schema_violation:not_object"
E_IO_ERROR = "io_error"
E_IO_WRITE_ERROR = "io_write_error"
E_BUILD_ERROR = "build_error"

def _read_json_file(path: str) -> Dict[str, Any]:
    """Read a JSON file strictly."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, dict):
                print(json.dumps({"error": E_NOT_OBJECT, "file": path}))
                sys.exit(EXIT_ERROR)
            return data
    except FileNotFoundError:
        print(json.dumps({"error": E_FILE_NOT_FOUND, "file": path}))
        sys.exit(EXIT_ERROR)
    except json.JSONDecodeError:
        print(json.dumps({"error": E_INVALID_JSON, "file": path}))
        sys.exit(EXIT_ERROR)
    except Exception:
        # Fallback for perm errors etc
        print(json.dumps({"error": E_IO_ERROR, "file": path}))
        sys.exit(EXIT_ERROR)

def _write_json_output(data: Any, path: Optional[str], pretty: bool, quiet: bool):
    """Write JSON output to file or stdout."""
    # Strict determinism: sort_keys=True, no whitespace default
    
    if pretty:
        content = json.dumps(data, indent=2, sort_keys=True)
    else:
        content = json.dumps(data, separators=(',', ':'), sort_keys=True)
        
    if path:
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception:
            print(json.dumps({"error": E_IO_WRITE_ERROR, "file": path}))
            sys.exit(EXIT_ERROR)
    elif not quiet:
        print(content)

def handle_build(args):
    """Handle build subcommand."""
    evidence = _read_json_file(args.evidence)
    contract = _read_json_file(args.contract)
    
    try:
        # The builder raises ValueError on critical failures
        # or we might want to catch it to emit JSON error
        package = build_cluster_a_replay_proof_package(
            evidence=evidence,
            governance_record=contract.get("governance_record", {}),
            apply_result=contract.get("apply_result", {}),
            conformance_result=contract.get("conformance_result", {})
        )
        
        _write_json_output(package, args.out, args.pretty, args.quiet)
        sys.exit(EXIT_OK)
        
    except Exception as e:
        # Protocol level error
        # We should print JSON error
        # Ideally protocol raises known exceptions, but here we trap generic
        print(json.dumps({"error": E_BUILD_ERROR}))
        sys.exit(EXIT_ERROR)

def handle_verify(args):
    """Handle verify subcommand."""
    package = _read_json_file(args.package)
    
    # Verifier never raises, always returns dict
    result = verify_cluster_a_replay_proof_package(package)
    
    _write_json_output(result, None, args.pretty, args.quiet)
    
    if result["ok"]:
        sys.exit(EXIT_OK)
    else:
        sys.exit(EXIT_VERIFICATION_FAILED)

def main():
    parser = argparse.ArgumentParser(
        description="ILC Cluster A Replay Proof CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Common args
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--pretty", action="store_true", help="Pretty print JSON")
    parent_parser.add_argument("--quiet", action="store_true", help="Suppress stdout")

    # Build
    build_parser = subparsers.add_parser("build", parents=[parent_parser], help="Build replay proof package")
    build_parser.add_argument("--evidence", required=True, help="Path to evidence JSON")
    build_parser.add_argument("--contract", required=True, help="Path to replay contract JSON")
    build_parser.add_argument("--out", help="Output path (default: stdout)")
    build_parser.set_defaults(func=handle_build)
    
    # Verify
    verify_parser = subparsers.add_parser("verify", parents=[parent_parser], help="Verify replay proof package")
    verify_parser.add_argument("package", help="Path to package JSON")
    verify_parser.set_defaults(func=handle_verify)
    
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
