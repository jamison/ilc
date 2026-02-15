import logging
from typing import Dict, List, Optional, TypedDict, TypeAlias
from pathlib import Path
import json

from jsonschema import Draft7Validator

from ilc_core.protocol.ilc_cluster_a_replay_proof_package import (
    verify_cluster_a_replay_proof_package,
)
from ilc_core.protocol.ilc_cluster_a_replay_proof_batch_ops import (
    run_batch_verify_and_compare,
)
from ilc_core.protocol.ilc_cluster_a_replay_proof_schemas import (
    load_replay_proof_schema,
)

logger = logging.getLogger(__name__)

GATE_VERSION = "v0.1"
COMPARE_VERSION = "v0.1"

GateSchemaMap: TypeAlias = Dict[str, object]


class GateCheckResult(TypedDict):
    check_id: str
    ok: bool
    expected: object
    actual: object
    error_token: str | None


class GateBaselineMismatch(TypedDict, total=False):
    path: str
    reason: str
    left: object | None
    right: object | None
    detail: str | None


class GateBaselineCompareReport(TypedDict):
    compare_version: str
    ok: bool
    mismatch_count: int
    mismatches: List[GateBaselineMismatch]


class GateReport(TypedDict):
    gate_version: str
    profile: str
    ok: bool
    pass_count: int
    fail_count: int
    checks: List[GateCheckResult]
    error_token_counts: Dict[str, int]
    exit_code: int
    error_token: str | None
    baseline_compare: GateBaselineCompareReport | None


def _load_gate_report_schema() -> GateSchemaMap:
    """Load CI-gate schema from packaged resources."""
    return load_replay_proof_schema("ilc_cluster_a_replay_proof_ci_gate_report_v0.1.json")


_GATE_REPORT_SCHEMA = _load_gate_report_schema()

_GATE_REPORT_VALIDATOR = Draft7Validator(_GATE_REPORT_SCHEMA) if _GATE_REPORT_SCHEMA else None


def _build_check_result(
    check_id: str,
    ok: bool,
    expected: object,
    actual: object,
    error_token: Optional[str] = None,
) -> GateCheckResult:
    return {
        "check_id": check_id,
        "ok": ok,
        "expected": expected,
        "actual": actual,
        "error_token": error_token,
    }


def _check_package_verify_valid(fixtures_root: Path) -> GateCheckResult:
    # Target: tests/fixtures/cluster_a_replay_proof_v0_1/package_valid.json
    target = fixtures_root / "cluster_a_replay_proof_v0_1" / "package_valid.json"
    if not target.exists():
        return _build_check_result(
            "check_package_verify_valid",
            False,
            "ok=true",
            "file_not_found",
            "fixture_missing",
        )

    try:
        with open(target, "r", encoding="utf-8") as f:
            pkg = json.load(f)
        report = verify_cluster_a_replay_proof_package(pkg)
        ok = report.get("ok", False)
        return _build_check_result(
            "check_package_verify_valid",
            ok,
            "ok=true",
            f"ok={str(ok).lower()}",
            None if ok else "verify_failed",
        )
    except Exception as exc:
        logger.debug("ci_gate_check_package_verify_valid_exception: %s", exc, exc_info=True)
        return _build_check_result(
            "check_package_verify_valid",
            False,
            "ok=true",
            "exception",
            "runtime_error",
        )


def _check_package_verify_tampered_hash(fixtures_root: Path) -> GateCheckResult:
    # Target: tests/fixtures/cluster_a_replay_proof_v0_1/package_tampered_hash.json
    target = fixtures_root / "cluster_a_replay_proof_v0_1" / "package_tampered_hash.json"
    if not target.exists():
        return _build_check_result(
            "check_package_verify_tampered_hash",
            False,
            "ok=false",
            "file_not_found",
            "fixture_missing",
        )

    try:
        with open(target, "r", encoding="utf-8") as f:
            pkg = json.load(f)
        report = verify_cluster_a_replay_proof_package(pkg)
        ok = report.get("ok", False)
        # Expected: ok=False
        check_ok = not ok
        return _build_check_result(
            "check_package_verify_tampered_hash",
            check_ok,
            "ok=false",
            f"ok={str(ok).lower()}",
            None if check_ok else "verify_succeeded_unexpectedly",
        )
    except Exception as exc:
        logger.debug("ci_gate_check_tampered_hash_exception: %s", exc, exc_info=True)
        return _build_check_result(
            "check_package_verify_tampered_hash",
            False,
            "ok=false",
            "exception",
            "runtime_error",
        )


def _check_batch_verify_manifest(fixtures_root: Path) -> GateCheckResult:
    # Target: tests/fixtures/cluster_a_replay_proof_batch_v0_1/manifest_mixed.json
    # Note: Phase 148 discovered load_manifest_paths expects TXT path list, NOT JSON dict.
    # We should look for tests/fixtures/cluster_a_replay_proof_batch_ops_v0_1/manifest.txt
    target = fixtures_root / "cluster_a_replay_proof_batch_ops_v0_1" / "manifest.txt"
    if not target.exists():
        return _build_check_result(
            "check_batch_verify_manifest",
            False,
            "batch_ok=true",
            "file_not_found",
            "fixture_missing",
        )

    try:
        # We need to manually construct package list because verify_cluster_a_replay_proof_batch
        # takes (packages, source_ids).
        # But wait, `run_batch_verify_from_manifest` does this.
        # Let's import that instead to avoid duplication logic.
        from ilc_core.protocol.ilc_cluster_a_replay_proof_batch_ops import run_batch_verify_from_manifest
        
        report = run_batch_verify_from_manifest(target)
        ok = report.get("ok", False)
        return _build_check_result(
            "check_batch_verify_manifest",
            ok,
            "batch_ok=true",
            f"batch_ok={str(ok).lower()}",
            None if ok else "batch_verify_failed",
        )
    except Exception as exc:
        logger.debug("ci_gate_check_batch_verify_manifest_exception: %s", exc, exc_info=True)
        return _build_check_result(
            "check_batch_verify_manifest",
            False,
            "batch_ok=true",
            "exception",
            "runtime_error",
        )


def _check_compare_reports_mismatch(fixtures_root: Path) -> GateCheckResult:
    # Target: verify-and-compare fixtures for mismatch scenario
    # manifest: tests/fixtures/cluster_a_replay_proof_batch_ops_v0_1/manifest.txt
    # expected: tests/fixtures/cluster_a_replay_proof_batch_ops_v0_1/report_mismatch.json
    
    # We expect mismatch count > 0 -> OK=False from protocol
    # BUT for this CI check, "success" means we successfully detetected the mismatch.
    # So if protocol returns ok=False, check passes.
    
    manifest = fixtures_root / "cluster_a_replay_proof_batch_ops_v0_1" / "manifest.txt"
    expected_path = fixtures_root / "cluster_a_replay_proof_batch_ops_v0_1" / "report_mismatch.json"
    
    if not manifest.exists() or not expected_path.exists():
        return _build_check_result(
            "check_compare_reports_mismatch",
            False,
            "compare_ok=false",
            "file_not_found",
            "fixture_missing",
        )

    try:
        with open(expected_path, "r", encoding="utf-8") as f:
            expected_report = json.load(f)
            
        reports = run_batch_verify_and_compare(manifest, expected_report)
        compare = reports["compare_report"]
        
        compare_ok = compare.get("ok", False)
        mismatch_count = compare.get("mismatch_count", 0)
        
        # We expect compare_ok=False and mismatch_count > 0
        success = (not compare_ok) and (mismatch_count > 0)
        
        return _build_check_result(
            "check_compare_reports_mismatch",
            success,
            "compare_ok=false",
            f"compare_ok={str(compare_ok).lower()},mismatch={mismatch_count}",
            None if success else "mismatch_detection_failed",
        )
            
    except Exception as exc:
        logger.debug("ci_gate_check_compare_mismatch_exception: %s", exc, exc_info=True)
        return _build_check_result(
            "check_compare_reports_mismatch",
            False,
            "compare_ok=false",
            "exception",
            "runtime_error",
        )


def _check_verify_and_compare_contract(fixtures_root: Path) -> GateCheckResult:
    # Target: verify-and-compare success scenario
    # manifest: tests/fixtures/cluster_a_replay_proof_batch_ops_v0_1/manifest.txt
    # expected: tests/fixtures/cluster_a_replay_proof_batch_ops_v0_1/report_match.json
    
    manifest = fixtures_root / "cluster_a_replay_proof_batch_ops_v0_1" / "manifest.txt"
    expected_path = fixtures_root / "cluster_a_replay_proof_batch_ops_v0_1" / "report_match.json"
    
    if not manifest.exists() or not expected_path.exists():
        return _build_check_result(
            "check_verify_and_compare_contract",
            False,
            "compare_ok=true",
            "file_not_found",
            "fixture_missing",
        )

    try:
        with open(expected_path, "r", encoding="utf-8") as f:
            expected_report = json.load(f)
            
        reports = run_batch_verify_and_compare(manifest, expected_report)
        compare = reports["compare_report"]
        
        compare_ok = compare.get("ok", False)
        
        return _build_check_result(
            "check_verify_and_compare_contract",
            compare_ok,
            "compare_ok=true",
            f"compare_ok={str(compare_ok).lower()}",
            None if compare_ok else "contract_verification_failed",
        )
            
    except Exception as exc:
        logger.debug("ci_gate_check_verify_compare_contract_exception: %s", exc, exc_info=True)
        return _build_check_result(
            "check_verify_and_compare_contract",
            False,
            "compare_ok=true",
            "exception",
            "runtime_error",
        )


def _count_error_tokens(checks: List[GateCheckResult]) -> Dict[str, int]:
    counts = {}
    for c in checks:
        if not c["ok"] and c["error_token"]:
            token = c["error_token"]
            counts[token] = counts.get(token, 0) + 1
    # Sort deterministically
    return dict(sorted(counts.items()))


def run_cluster_a_replay_proof_ci_gate(
    fixtures_root: Path | str, profile: str = "release_v0_1"
) -> GateReport:
    """
    Executes a deterministic sequence of replay-proof checks.
    """
    fixtures_root = Path(fixtures_root)

    if profile != "release_v0_1":
        return {
            "gate_version": GATE_VERSION,
            "profile": profile,
            "ok": False,
            "pass_count": 0,
            "fail_count": 0,
            "checks": [],
            "error_token_counts": {"profile_invalid": 1},
            "exit_code": 2,
            "error_token": "profile_invalid",
            "baseline_compare": None,
        }

    checks = []
    
    # release_v0_1 checks sequence
    checks.append(_check_package_verify_valid(fixtures_root))
    checks.append(_check_package_verify_tampered_hash(fixtures_root))
    checks.append(_check_batch_verify_manifest(fixtures_root))
    checks.append(_check_compare_reports_mismatch(fixtures_root))
    checks.append(_check_verify_and_compare_contract(fixtures_root))
    
    pass_count = sum(1 for c in checks if c["ok"])
    fail_count = len(checks) - pass_count
    
    ok = (fail_count == 0)
    exit_code = 0 if ok else 1
    
    return {
        "gate_version": GATE_VERSION,
        "profile": profile,
        "ok": ok,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "checks": checks,
        "error_token_counts": _count_error_tokens(checks),
        "exit_code": exit_code,
        "error_token": None,
        "baseline_compare": None,
    }


# --- Baseline Load and Drift Compare ---


def _validate_gate_report_schema(data: object) -> Optional[str]:
    """Validate data against CI gate report schema. Returns error string if invalid, None if valid."""
    if _GATE_REPORT_VALIDATOR is None:
        return "internal_error:schema_not_loaded"
    errors = list(_GATE_REPORT_VALIDATOR.iter_errors(data))
    if not errors:
        return None
    errors.sort(key=lambda e: (list(e.absolute_path), e.message))
    return f"schema_validation_failed: {errors[0].message}"


def load_ci_gate_baseline(path: Path | str) -> GateReport:
    """
    Load and validate a CI gate baseline file.
    Raises FileNotFoundError, json.JSONDecodeError, or ValueError (schema invalid).
    """
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("baseline is not a JSON object")
    err = _validate_gate_report_schema(data)
    if err:
        raise ValueError(err)
    return data


def _escape_path_token(token: str) -> str:
    """Escape path token per JSON Pointer (RFC 6901)."""
    return token.replace("~", "~0").replace("/", "~1")


def _path_join(parent: str, key: str) -> str:
    """Append key to parent path."""
    token = _escape_path_token(str(key))
    if parent in ("", "/"):
        return f"/{token}"
    return f"{parent}/{token}"


def _compare_recursive(
    path: str, left: object, right: object, mismatches: List[GateBaselineMismatch]
) -> None:
    """Recursively compare left and right structures. Populates mismatches list."""
    if type(left) != type(right):
        mismatches.append({
            "path": path,
            "reason": "value_mismatch",
            "left": left,
            "right": right,
            "detail": None,
        })
        return

    if isinstance(left, dict):
        all_keys = sorted(set(left.keys()) | set(right.keys()))
        for k in all_keys:
            new_path = _path_join(path, k)
            if k not in left:
                mismatches.append({"path": new_path, "reason": "missing_left", "left": None, "right": right[k], "detail": None})
            elif k not in right:
                mismatches.append({"path": new_path, "reason": "missing_right", "left": left[k], "right": None, "detail": None})
            else:
                _compare_recursive(new_path, left[k], right[k], mismatches)
        return

    if isinstance(left, list):
        max_len = max(len(left), len(right))
        for i in range(max_len):
            new_path = _path_join(path, str(i))
            if i >= len(left):
                mismatches.append({"path": new_path, "reason": "missing_left", "left": None, "right": right[i], "detail": None})
            elif i >= len(right):
                mismatches.append({"path": new_path, "reason": "missing_right", "left": left[i], "right": None, "detail": None})
            else:
                _compare_recursive(new_path, left[i], right[i], mismatches)
        return

    if left != right:
        mismatches.append({
            "path": path,
            "reason": "value_mismatch",
            "left": left,
            "right": right,
            "detail": None,
        })


def compare_ci_gate_report_to_baseline(
    current: object, baseline: object
) -> GateBaselineCompareReport:
    """
    Compare a current CI gate report to a baseline report.
    Returns a deterministic compare report with stable reason tokens.
    """
    # Schema validation
    current_err = _validate_gate_report_schema(current)
    if current_err:
        return {
            "compare_version": COMPARE_VERSION,
            "ok": False,
            "mismatch_count": 1,
            "mismatches": [{
                "path": "/",
                "reason": "schema_invalid_current",
                "left": None,
                "right": None,
                "detail": current_err,
            }],
        }

    baseline_err = _validate_gate_report_schema(baseline)
    if baseline_err:
        return {
            "compare_version": COMPARE_VERSION,
            "ok": False,
            "mismatch_count": 1,
            "mismatches": [{
                "path": "/",
                "reason": "schema_invalid_baseline",
                "left": None,
                "right": None,
                "detail": baseline_err,
            }],
        }

    # Deep compare (current=left, baseline=right)
    mismatches: List[GateBaselineMismatch] = []
    _compare_recursive("/", current, baseline, mismatches)

    # Deterministic sort
    mismatches.sort(key=lambda m: (m["path"], m["reason"]))

    return {
        "compare_version": COMPARE_VERSION,
        "ok": len(mismatches) == 0,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
    }
