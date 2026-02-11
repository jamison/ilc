from typing import List, Dict, Any
from pathlib import Path
from collections import Counter

from ilc_core.protocol.ilc_cluster_a_replay_proof_package import verify_cluster_a_replay_proof_package

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
    except Exception:
        # If we can't read the manifest, let the caller handle the IO error, 
        # but the specific requirement covers malformed content logic.
        # Here we assume file exists and is readable if passed to this function in a valid flow.
        raise
        
    for raw in content.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line in seen:
            raise ValueError("schema_violation:duplicate_manifest_path")
        seen.add(line)
        out.append(line)
    return out

def verify_cluster_a_replay_proof_batch(
    package_items: List[Dict[str, Any]], 
    source_ids: List[str]
) -> Dict[str, Any]:
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

    results = []
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

        entry = {
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
    
    report = {
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
