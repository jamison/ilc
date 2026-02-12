from typing import Dict, Any
from pathlib import Path
import json
import posixpath

from ilc_core.protocol.ilc_cluster_a_replay_proof_batch import (
    verify_cluster_a_replay_proof_batch,
    load_manifest_paths,
)
from ilc_core.protocol.ilc_cluster_a_replay_proof_batch_compare import (
    compare_cluster_a_replay_proof_batch_reports,
)


class ManifestParseError(ValueError):
    """Manifest or package content is malformed for batch ops."""


class ManifestEntryNotFoundError(FileNotFoundError):
    """A manifest-referenced package file does not exist."""


def _normalize_source_id(raw_path: str) -> str:
    """Normalize manifest entry IDs to deterministic POSIX-like relative IDs."""
    normalized = raw_path.replace("\\", "/")
    normalized = posixpath.normpath(normalized)
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def run_batch_verify_from_manifest(manifest_path: Path) -> Dict[str, Any]:
    """
    Run batch verification from a manifest file.

    Raises:
        ManifestParseError: On invalid manifest content or invalid package payload.
        ManifestEntryNotFoundError: If a referenced package file is missing.
        OSError: On IO errors reading manifest or package files.
    """
    try:
        rel_paths = load_manifest_paths(manifest_path)
    except ValueError as exc:
        raise ManifestParseError(str(exc)) from exc

    base_dir = manifest_path.parent
    package_items = []
    source_ids = []

    for rp in rel_paths:
        source_id = _normalize_source_id(rp)
        pkg_path = base_dir / rp
        if not pkg_path.exists():
            raise ManifestEntryNotFoundError(source_id)

        try:
            with open(pkg_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            raise ManifestParseError(f"invalid_json:{source_id}") from exc
        except OSError:
            raise

        if not isinstance(data, dict):
            raise ManifestParseError(f"package_not_object:{source_id}")

        package_items.append(data)
        source_ids.append(source_id)

    return verify_cluster_a_replay_proof_batch(package_items, source_ids)


def run_batch_verify_and_compare(manifest_path: Path, expected_report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run batch verification and compare against expected report.
    Returns both reports for higher-level command composition.
    """
    batch_report = run_batch_verify_from_manifest(manifest_path)
    compare_report = compare_cluster_a_replay_proof_batch_reports(batch_report, expected_report)
    return {"batch_report": batch_report, "compare_report": compare_report}
