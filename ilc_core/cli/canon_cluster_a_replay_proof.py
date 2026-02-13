"""
ILC Constitution Cluster A - Replay Proof Package CLI.
Phase 144.

Provides command-line interface for building and verifying
canonical replay proof packages.
"""

import sys
import json
import argparse
from typing import Dict, Optional, TypedDict, TypeAlias

from ilc_core.protocol.ilc_cluster_a_replay_proof_package import (
    build_cluster_a_replay_proof_package,
    verify_cluster_a_replay_proof_package
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

CliJsonObject: TypeAlias = Dict[str, object]


class OpsContract(TypedDict):
    ops_contract_version: str
    ok: bool
    batch_report_path: str | None
    compare_report_path: str | None
    batch_ok: bool
    compare_ok: bool
    exit_code: int
    error_token: str | None


def _read_json_file(path: str) -> CliJsonObject:
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

def _write_json_output(data: object, path: Optional[str], pretty: bool, quiet: bool) -> None:
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
        
    except Exception:
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

from pathlib import Path
from ilc_core.protocol.ilc_cluster_a_replay_proof_batch import (
    verify_cluster_a_replay_proof_batch,
    load_manifest_paths
)

def handle_verify_batch(args):
    """Handle verify-batch subcommand."""
    package_items = []
    source_ids = []
    
    # Deterministic source selection
    paths = []
    if args.manifest:
        try:
            manifest_path = Path(args.manifest)
            rel_paths = load_manifest_paths(manifest_path)
            base_dir = manifest_path.parent
            for p_str in rel_paths:
                # Resolve package files relative to the manifest directory,
                # while preserving normalized manifest entry as source_id.
                paths.append((base_dir / p_str, p_str))
        except FileNotFoundError:
            print(json.dumps({"error": "manifest_not_found", "file": str(Path(args.manifest))}))
            sys.exit(EXIT_ERROR)
        except ValueError as e:
            print(json.dumps({"error": "manifest_parse_error", "detail": str(e)}))
            sys.exit(EXIT_ERROR)
        except Exception:
            print(json.dumps({"error": "manifest_parse_error", "detail": "manifest_read_error"}))
            sys.exit(EXIT_ERROR)
    elif args.input_dir:
        input_dir = Path(args.input_dir)
        if not input_dir.is_dir():
             print(json.dumps({"error": "input_dir_not_found"}))
             sys.exit(EXIT_ERROR)
        
        # sorted lexicographically by normalized path
        # glob pattern
        pattern = args.glob if args.glob else "*.json"
        
        # We need deterministic sort of resolved paths
        # "normalized relative path from --input-dir"
        
        # Gather all files
        all_files = sorted(input_dir.rglob(pattern), key=lambda p: p.as_posix())
        paths = all_files
    else:
        print(json.dumps({"error": "usage_error:missing_input_source"}))
        sys.exit(EXIT_ERROR)

    # Process files
    for item in paths:
        # Source ID definition:
        # - form manifest: normalized relative path as written (trimmed)
        # - from directory scan: normalized relative path from --input-dir
        
        if args.manifest:
            p, source_id = item
            error_file = source_id
        else:
            p = item
            # Relative to input_dir
            source_id = p.relative_to(args.input_dir).as_posix()
            error_file = str(p)
            
        try:
            if not p.exists():
                 # Fail fast per spec for manifest?
                 # "For missing file in manifest, fail with exit code 2 and stable JSON token"
                 # Directory scan won't have missing files unless race condition.
                 if args.manifest:
                     print(json.dumps({"error": "manifest_file_not_found", "file": error_file}))
                     sys.exit(EXIT_ERROR)
                 continue # Should not happen for dir scan
                 
            with open(p, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    # "continue batch verification only if file was readable and parseable to object; 
                    # otherwise treat as input error with exit 2"
                    # wait, "invalid JSON in one package... continue ... only if parseable to object"
                    # logic:
                    # - Not readable/parseable -> Exit 2
                    # - Parseable but not object? -> The prompt says "invalid JSON ... continue ... only if ... parseable to object"
                    #   Implying if it IS parseable but NOT object, maybe we should treat it as invalid package?
                    #   Let's see: "Never raises on invalid package shape; represent failures in report."
                    #   So if it is valid JSON but not a dict, we can pass it to verifier (which expects dict).
                    #   Verifier implementation in batch module expects dict.
                    #   So if not dict, we fail hard? Or wrap?
                    #   Re-reading: "For invalid JSON in one package... continue ... only if ... parseable to object"
                    #   So if it is NOT parseable (JSONDecodeError), we treat as input error (Exit 2).
                    #   If it IS parseable, we proceed.
                    #   If it is parseable but not a dict, verifier calls would violate
                    #   the expected object contract for package entries.
                    #   We should probably treat non-dict as immediate fail or wrap it?
                    #   Let's strictly fail if not dict for now to be safe, or just pass to verifier?
                    #   Actually, let's treat non-dict as "invalid package" which causes verification fail (Exit 1), not input error (Exit 2).
                    #   But `package_items` is typed List[Dict]. So we must ensure dict.
                    #   If not dict, we can't pass to batch verifier as is.
                    #   We will just print error and exit 2 per "treat as input error with exit 2" interpretation if "otherwise" covers "not parseable to object".
                   print(json.dumps({"error": E_NOT_OBJECT, "file": str(p)}))
                   sys.exit(EXIT_ERROR)
                
                package_items.append(data)
                source_ids.append(source_id)

        except json.JSONDecodeError:
            print(json.dumps({"error": E_INVALID_JSON, "file": error_file}))
            sys.exit(EXIT_ERROR)
        except OSError:
            print(json.dumps({"error": E_IO_ERROR, "file": error_file}))
            sys.exit(EXIT_ERROR)

    # Run batch verification
    report = verify_cluster_a_replay_proof_batch(package_items, source_ids)
    
    # Write output
    output_path = args.out # Optional
    _write_json_output(report, output_path, args.pretty, args.quiet) # Works for stdout too
    
    # Exit code
    if report["ok"]:
        sys.exit(EXIT_OK)
    else:
         sys.exit(EXIT_VERIFICATION_FAILED)

from ilc_core.protocol.ilc_cluster_a_replay_proof_batch_compare import compare_cluster_a_replay_proof_batch_reports

def handle_compare_reports(args):
    """Handle compare-reports subcommand."""
    left = _read_json_file(args.left)
    right = _read_json_file(args.right)
    
    # Run comparison
    report = compare_cluster_a_replay_proof_batch_reports(left, right)
    
    # Write output
    output_path = args.out # Optional
    _write_json_output(report, output_path, args.pretty, args.quiet)
    
    # Exit code
    if report["ok"]:
        sys.exit(EXIT_OK)
    # Schema-invalid compare results are input/schema errors.
    reasons = {m.get("reason") for m in report.get("mismatches", []) if isinstance(m, dict)}
    if "schema_invalid_left" in reasons or "schema_invalid_right" in reasons:
        sys.exit(EXIT_ERROR)
    else:
        sys.exit(EXIT_VERIFICATION_FAILED)

from ilc_core.protocol.ilc_cluster_a_replay_proof_batch_ops import (
    run_batch_verify_and_compare,
    ManifestParseError,
    ManifestEntryNotFoundError,
)

OPS_CONTRACT_VERSION = "v0.1"
OPS_TOKEN_MANIFEST_NOT_FOUND = "manifest_not_found"
OPS_TOKEN_MANIFEST_PARSE_ERROR = "manifest_parse_error"
OPS_TOKEN_MANIFEST_FILE_NOT_FOUND = "manifest_file_not_found"
OPS_TOKEN_EXPECTED_INVALID_JSON = "expected_invalid_json"
OPS_TOKEN_EXPECTED_NOT_OBJECT = "expected_not_object"
OPS_TOKEN_EXPECTED_SCHEMA_INVALID = "expected_schema_invalid"
OPS_TOKEN_IO_ERROR = "io_error"
OPS_TOKEN_IO_WRITE_ERROR = "io_write_error"
OPS_TOKEN_RUNTIME_ERROR = "ops_runtime_error"
OPS_TOKEN_NO_OUTPUT_SINK = "usage_error:no_output_sink"


def _json_dumps(data: object, pretty: bool) -> str:
    """Serialize JSON with deterministic key ordering."""
    if pretty:
        return json.dumps(data, indent=2, sort_keys=True)
    return json.dumps(data, separators=(",", ":"), sort_keys=True)


def _write_json_file(path: str, data: object, pretty: bool) -> None:
    """Write deterministic JSON content to file."""
    content = _json_dumps(data, pretty)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _build_ops_contract(
    *,
    batch_ok: bool,
    compare_ok: bool,
    batch_report_path: Optional[str],
    compare_report_path: Optional[str],
    exit_code: int,
    error_token: Optional[str],
) -> OpsContract:
    return {
        "ops_contract_version": OPS_CONTRACT_VERSION,
        "ok": bool(batch_ok and compare_ok and exit_code == EXIT_OK),
        "batch_report_path": batch_report_path,
        "compare_report_path": compare_report_path,
        "batch_ok": bool(batch_ok),
        "compare_ok": bool(compare_ok),
        "exit_code": exit_code,
        "error_token": error_token,
    }


def _emit_ops_contract(
    contract: OpsContract, pretty: bool, quiet: bool, force_stdout: bool = False
) -> None:
    if not quiet or force_stdout:
        print(_json_dumps(contract, pretty))


def _emit_ops_error(token: str, pretty: bool, quiet: bool) -> None:
    contract = _build_ops_contract(
        batch_ok=False,
        compare_ok=False,
        batch_report_path=None,
        compare_report_path=None,
        exit_code=EXIT_ERROR,
        error_token=token,
    )
    _emit_ops_contract(contract, pretty=pretty, quiet=quiet, force_stdout=True)
    sys.exit(EXIT_ERROR)

def handle_verify_and_compare(args):
    """Handle verify-and-compare subcommand."""
    if args.quiet and not args.out_compare:
        _emit_ops_error(OPS_TOKEN_NO_OUTPUT_SINK, pretty=args.pretty, quiet=args.quiet)

    try:
        with open(args.expected, "r", encoding="utf-8") as f:
            expected_report = json.load(f)
    except json.JSONDecodeError:
        _emit_ops_error(OPS_TOKEN_EXPECTED_INVALID_JSON, pretty=args.pretty, quiet=args.quiet)
    except OSError:
        _emit_ops_error(OPS_TOKEN_IO_ERROR, pretty=args.pretty, quiet=args.quiet)

    if not isinstance(expected_report, dict):
        _emit_ops_error(OPS_TOKEN_EXPECTED_NOT_OBJECT, pretty=args.pretty, quiet=args.quiet)

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        _emit_ops_error(OPS_TOKEN_MANIFEST_NOT_FOUND, pretty=args.pretty, quiet=args.quiet)

    try:
        result_map = run_batch_verify_and_compare(manifest_path, expected_report)
        batch_report = result_map["batch_report"]
        compare_report = result_map["compare_report"]
    except ManifestEntryNotFoundError:
        _emit_ops_error(OPS_TOKEN_MANIFEST_FILE_NOT_FOUND, pretty=args.pretty, quiet=args.quiet)
    except ManifestParseError:
        _emit_ops_error(OPS_TOKEN_MANIFEST_PARSE_ERROR, pretty=args.pretty, quiet=args.quiet)
    except OSError:
        _emit_ops_error(OPS_TOKEN_IO_ERROR, pretty=args.pretty, quiet=args.quiet)
    except Exception:
        _emit_ops_error(OPS_TOKEN_RUNTIME_ERROR, pretty=args.pretty, quiet=args.quiet)

    batch_report_path = None
    compare_report_path = None

    if args.out_report:
        try:
            _write_json_file(args.out_report, batch_report, args.pretty)
            batch_report_path = str(Path(args.out_report).resolve())
        except OSError:
            _emit_ops_error(OPS_TOKEN_IO_WRITE_ERROR, pretty=args.pretty, quiet=args.quiet)

    if args.out_compare:
        try:
            _write_json_file(args.out_compare, compare_report, args.pretty)
            compare_report_path = str(Path(args.out_compare).resolve())
        except OSError:
            _emit_ops_error(OPS_TOKEN_IO_WRITE_ERROR, pretty=args.pretty, quiet=args.quiet)

    batch_ok = bool(batch_report.get("ok", False))
    compare_ok = bool(compare_report.get("ok", False))
    reasons = {m.get("reason") for m in compare_report.get("mismatches", []) if isinstance(m, dict)}

    if compare_ok:
        exit_code = EXIT_OK
        error_token = None
    elif "schema_invalid_left" in reasons or "schema_invalid_right" in reasons:
        exit_code = EXIT_ERROR
        error_token = OPS_TOKEN_EXPECTED_SCHEMA_INVALID if "schema_invalid_right" in reasons else OPS_TOKEN_RUNTIME_ERROR
    else:
        exit_code = EXIT_VERIFICATION_FAILED
        error_token = None

    contract = _build_ops_contract(
        batch_ok=batch_ok,
        compare_ok=compare_ok,
        batch_report_path=batch_report_path,
        compare_report_path=compare_report_path,
        exit_code=exit_code,
        error_token=error_token,
    )
    _emit_ops_contract(contract, pretty=args.pretty, quiet=args.quiet)
    sys.exit(exit_code)

from ilc_core.protocol.ilc_cluster_a_replay_proof_ci_gate import (
    run_cluster_a_replay_proof_ci_gate,
    load_ci_gate_baseline,
    compare_ci_gate_report_to_baseline,
)

def handle_ci_gate(args):
    """Handle ci-gate subcommand."""
    fixtures_root = Path(args.fixtures_root).absolute()
    
    # Output handling
    pretty = args.pretty
    quiet = args.quiet
    out_path = args.out
    
    # Guard: quiet and no output sink
    if quiet and not out_path:
        err_report = {
            "gate_version": "v0.1",
            "profile": args.profile,
            "ok": False,
            "pass_count": 0,
            "fail_count": 0,
            "checks": [],
            "error_token_counts": {"usage_error:no_output_sink": 1},
            "exit_code": EXIT_ERROR,
            "error_token": "usage_error:no_output_sink",
            "baseline_compare": None,
        }
        print(_json_dumps(err_report, pretty))
        sys.exit(EXIT_ERROR)

    # Gate logic
    report = run_cluster_a_replay_proof_ci_gate(fixtures_root, args.profile)

    # Baseline enforcement
    baseline_path = getattr(args, 'baseline', None)
    enforce_baseline = getattr(args, 'enforce_baseline', False)

    if baseline_path:
        try:
            baseline = load_ci_gate_baseline(Path(baseline_path))
        except FileNotFoundError:
            err_report = {
                "gate_version": "v0.1",
                "profile": args.profile,
                "ok": False,
                "pass_count": 0,
                "fail_count": 0,
                "checks": [],
                "error_token_counts": {"baseline_not_found": 1},
                "exit_code": EXIT_ERROR,
                "error_token": "baseline_not_found",
                "baseline_compare": None,
            }
            print(_json_dumps(err_report, pretty))
            sys.exit(EXIT_ERROR)
        except json.JSONDecodeError:
            err_report = {
                "gate_version": "v0.1",
                "profile": args.profile,
                "ok": False,
                "pass_count": 0,
                "fail_count": 0,
                "checks": [],
                "error_token_counts": {"baseline_invalid_json": 1},
                "exit_code": EXIT_ERROR,
                "error_token": "baseline_invalid_json",
                "baseline_compare": None,
            }
            print(_json_dumps(err_report, pretty))
            sys.exit(EXIT_ERROR)
        except ValueError:
            err_report = {
                "gate_version": "v0.1",
                "profile": args.profile,
                "ok": False,
                "pass_count": 0,
                "fail_count": 0,
                "checks": [],
                "error_token_counts": {"baseline_schema_invalid": 1},
                "exit_code": EXIT_ERROR,
                "error_token": "baseline_schema_invalid",
                "baseline_compare": None,
            }
            print(_json_dumps(err_report, pretty))
            sys.exit(EXIT_ERROR)
        except Exception:
            err_report = {
                "gate_version": "v0.1",
                "profile": args.profile,
                "ok": False,
                "pass_count": 0,
                "fail_count": 0,
                "checks": [],
                "error_token_counts": {"baseline_compare_runtime_error": 1},
                "exit_code": EXIT_ERROR,
                "error_token": "baseline_compare_runtime_error",
                "baseline_compare": None,
            }
            print(_json_dumps(err_report, pretty))
            sys.exit(EXIT_ERROR)

        try:
            cmp_report = compare_ci_gate_report_to_baseline(report, baseline)
        except Exception:
            err_report = {
                "gate_version": "v0.1",
                "profile": args.profile,
                "ok": False,
                "pass_count": 0,
                "fail_count": 0,
                "checks": [],
                "error_token_counts": {"baseline_compare_runtime_error": 1},
                "exit_code": EXIT_ERROR,
                "error_token": "baseline_compare_runtime_error",
                "baseline_compare": None,
            }
            print(_json_dumps(err_report, pretty))
            sys.exit(EXIT_ERROR)

        report["baseline_compare"] = cmp_report

        if enforce_baseline and not cmp_report["ok"]:
            report["ok"] = False
            report["exit_code"] = EXIT_VERIFICATION_FAILED
            report["error_token"] = "baseline_drift_detected"

    # Serialize report
    output_str = _json_dumps(report, pretty)
    
    # Write to file if requested
    if out_path:
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(output_str)
        except OSError:
             err_report = {
                "gate_version": "v0.1",
                "profile": args.profile,
                "ok": False,
                "pass_count": 0,
                "fail_count": 0,
                "checks": [],
                "error_token_counts": {E_IO_WRITE_ERROR: 1},
                "exit_code": EXIT_ERROR,
                "error_token": E_IO_WRITE_ERROR,
                "baseline_compare": None,
             }
             print(_json_dumps(err_report, pretty))
             sys.exit(EXIT_ERROR)

    # Print to stdout unless quiet
    if not quiet:
        print(output_str)
        
    # Exit code
    sys.exit(report["exit_code"])

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
    
    # Verify Batch
    batch_parser = subparsers.add_parser("verify-batch", parents=[parent_parser], help="Verify batch of replay proof packages")
    group = batch_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input-dir", help="Directory to scan for packages")
    group.add_argument("--manifest", help="Path to manifest file listing packages")
    
    batch_parser.add_argument("--glob", help="Glob pattern for directory scan (default: *.json)")
    batch_parser.add_argument("--out", help="Output path for batch report (default: stdout)")
    batch_parser.set_defaults(func=handle_verify_batch)
    
    # Compare Reports
    compare_parser = subparsers.add_parser("compare-reports", parents=[parent_parser], help="Compare two batch reports")
    compare_parser.add_argument("--left", required=True, help="Path to left batch report")
    compare_parser.add_argument("--right", required=True, help="Path to right batch report")
    compare_parser.add_argument("--out", help="Output path for compare report (default: stdout)")
    compare_parser.set_defaults(func=handle_compare_reports)
    
    # Verify and Compare (Ops)
    ops_parser = subparsers.add_parser("verify-and-compare", parents=[parent_parser], help="Run batch verification and compare against expected report")
    ops_parser.add_argument("--manifest", required=True, help="Path to input manifest")
    ops_parser.add_argument("--expected", required=True, help="Path to expected batch report")
    ops_parser.add_argument("--out-report", help="Output path for generated batch report")
    ops_parser.add_argument("--out-compare", help="Output path for comparison report (default: stdout)")
    ops_parser.set_defaults(func=handle_verify_and_compare)
    
    # CI Gate
    gate_parser = subparsers.add_parser("ci-gate", parents=[parent_parser], help="Run deterministic CI gate checks")
    gate_parser.add_argument("--fixtures-root", required=True, help="Root path for test fixtures")
    gate_parser.add_argument("--profile", default="release_v0_1", help="CI profile name (default: release_v0_1)")
    gate_parser.add_argument("--out", help="Output JSON report path")
    gate_parser.add_argument("--baseline", help="Path to baseline report for drift comparison")
    gate_parser.add_argument("--enforce-baseline", action="store_true", help="Fail (exit 1) if baseline drift detected")
    gate_parser.set_defaults(func=handle_ci_gate)
    
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
