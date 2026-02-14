from typing import Dict, List, TypedDict
from pathlib import Path
from collections import Counter
import posixpath
import re
import logging

from ilc_core.protocol.ilc_cluster_a_replay_proof_package import (
    ReplayCheckList,
    ReplayObject,
    verify_cluster_a_replay_proof_package,
)

logger = logging.getLogger(__name__)

_WINDOWS_ABS_PATH_RE = re.compile(r"^[A-Za-z]:/")


class ReplayBatchResultRow(TypedDict):
    input_index: int
    source_id: str
    ok: bool
    errors: List[str]
    warnings: List[str]
    checks: ReplayCheckList


class ReplayBatchReport(TypedDict):
    report_version: str
    total_packages: int
    ok_count: int
    fail_count: int
    ok: bool
    results: List[ReplayBatchResultRow]
    error_token_counts: Dict[str, int]
    batch_errors: List[str]


def _normalize_manifest_path(raw_path: str) -> str:
    """
    Normalize and validate a manifest entry path.

    Returns a portable POSIX-like relative path.
    Raises ValueError on invalid path forms.
    """
    normalized = raw_path.replace("\\", "/")
    normalized = posixpath.normpath(normalized)

    while normalized.startswith("./"):
        normalized = normalized[2:]

    if normalized in ("", "."):
        raise ValueError("schema_violation:invalid_manifest_path")

    # Reject traversal and absolute paths; manifests must stay relative.
    if normalized == ".." or normalized.startswith("../"):
        raise ValueError("schema_violation:manifest_path_escape")
    if normalized.startswith("/") or _WINDOWS_ABS_PATH_RE.match(normalized):
        raise ValueError("schema_violation:manifest_path_not_relative")

    return normalized


def load_manifest_paths(path: Path) -> List[str]:
    """
    Parses a manifest file into a list of normalized relative paths.
    
    Rules:
    - Ignores blank lines.
    - Ignores lines starting with '#'.
    - Preserves first-seen order.
    - Rejects duplicate effective paths with 'schema_violation:duplicate_manifest_path'.
    - Does NOT expand shell globs.
    """
    seen = set()
    out: List[str] = []
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as exc:
        logger.debug("batch_manifest_read_guard: %s", exc, exc_info=True)
        # If we can't read the manifest, let the caller handle the IO error, 
        # but the specific requirement covers malformed content logic.
        # Here we assume file exists and is readable if passed to this function in a valid flow.
        raise
        
    for raw in content.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        normalized = _normalize_manifest_path(line)
        if normalized in seen:
            raise ValueError("schema_violation:duplicate_manifest_path")
        seen.add(normalized)
        out.append(normalized)
    return out

def verify_cluster_a_replay_proof_batch(
    package_items: List[ReplayObject], 
    source_ids: List[str]
) -> ReplayBatchReport:
    """
    Verifies a batch of replay proof packages and produces a deterministic report.
    
    Args:
        package_items: List of package dictionaries (already parsed).
        source_ids: List of source identifiers corresponding 1:1 to package_items.
        
    Returns:
        A dictionary matching the ilc_cluster_a_replay_proof_batch_report_v0.1 schema.
    """
    if len(package_items) != len(source_ids):
        # Deterministic error report for input mismatch
        return {
            "report_version": "v0.1",
            "total_packages": 0,
            "ok_count": 0,
            "fail_count": 0,
            "ok": False,
            "results": [],
            "error_token_counts": {},
            "batch_errors": ["context_violation:batch_input_length_mismatch"]
        }

    results: List[ReplayBatchResultRow] = []
    token_counter = Counter()

    for idx, (package, source_id) in enumerate(zip(package_items, source_ids)):
        # verify_cluster_a_replay_proof_package returns:
        # { "ok": bool, "errors": [...], "warnings": [...], "checks": {...} }
        # plus potentially other fields, but we only need these for the report contract.
        
        # We assume package is a dict. If it's malformed/None, the caller should have 
        # handled it or we treat it as an invalid package here if the verifier supports it.
        # The prompt says: "Never raises on invalid package shape; represent failures in report."
        # verify_cluster_a_replay_proof_package handles basic shape validation.
        
        pkg_result = verify_cluster_a_replay_proof_package(package)
        
        # Construct the result entry per spec
        checks = pkg_result.get("checks", [])
        if not isinstance(checks, list):
            checks = []

        entry: ReplayBatchResultRow = {
            "input_index": idx,
            "source_id": source_id,
            "ok": pkg_result["ok"],
            "errors": pkg_result.get("errors", []),
            "warnings": pkg_result.get("warnings", []),
            "checks": checks
        }
        
        results.append(entry)
        
        # Aggregate error tokens
        for err in entry["errors"]:
            token_counter[err] += 1

    # Sort aggregated error counts by token (key) for determinism
    error_token_counts = {k: token_counter[k] for k in sorted(token_counter)}

    # Aggregate counts
    total_packages = len(results)
    ok_count = sum(1 for r in results if r["ok"])
    fail_count = total_packages - ok_count
    
    report: ReplayBatchReport = {
        "report_version": "v0.1",
        "total_packages": total_packages,
        "ok_count": ok_count,
        "fail_count": fail_count,
        "ok": (fail_count == 0),
        "results": results, # Preserves deterministic input order
        "error_token_counts": error_token_counts,
        "batch_errors": [] # No batch-level errors if we got here
    }
    
    return report
