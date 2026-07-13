# SPDX-License-Identifier: AGPL-3.0-only
"""Local StarMap installer MVP for bounded AtlasSliceManifest fixtures."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable, Mapping


STARMAP_INSTALLER_VERSION = "starmap_installer_1575b_fix4.v0.1"
MAX_MANIFEST_BYTES = 10 * 1024 * 1024
PUBLIC_MARKER = "PUBLIC_RC_" + "EXCLUDE"
ALLOWED_EXPORT_CATEGORIES = frozenset({"public"})
REQUIRED_ENVELOPE_KEYS = frozenset(
    {
        "content_entries",
        "cross_section_ref_count",
        "exclusion_policy",
        "included_node_merkle_root",
        "installer_profile",
        "privacy_budget",
        "projection_filter",
        "public_rc_exclude",
        "receipt_sha256",
        "root_pointers",
        "runtime_version",
        "section_label",
        "semantic_loss_annotations",
        "slice_id",
        "slice_version",
        "source_lmdb_root_sha256",
    }
)


class StarMapInstallerError(ValueError):
    """Raised when the local installer rejects a manifest or materialization."""


def load_manifest_payload(path: str | Path) -> dict[str, Any]:
    """Load a manifest JSON object with the MVP byte limit."""

    manifest_path = Path(path)
    try:
        size = manifest_path.stat().st_size
    except OSError as exc:
        raise StarMapInstallerError("starmap_manifest_unreadable") from exc
    if size > MAX_MANIFEST_BYTES:
        raise StarMapInstallerError("starmap_manifest_too_large")
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise StarMapInstallerError("starmap_manifest_json_invalid") from exc
    if not isinstance(payload, dict):
        raise StarMapInstallerError("starmap_manifest_json_not_object")
    return payload


def canonical_json_bytes(payload: object) -> bytes:
    """Return deterministic JSON bytes after rejecting floats."""

    _reject_float(payload)
    try:
        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise StarMapInstallerError("starmap_canonical_json_invalid") from exc
    return encoded.encode("utf-8")


def canonical_sha256(payload: object) -> str:
    """Return the SHA-256 digest of the canonical JSON representation."""

    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def verify_starmap_manifest(payload: Mapping[str, object]) -> dict[str, object]:
    """Verify an unsigned local AtlasSliceManifest fixture and public boundaries."""

    _validate_fixture_passthrough_fields(payload)
    envelope = _manifest_envelope(payload)
    entries = _content_entries(envelope)
    for entry in entries:
        _validate_public_entry(entry)
        _entry_materialization_bytes(entry)
    _verify_merkle_root(envelope, entries)
    return {
        "content_entry_count": len(entries),
        "installer_version": STARMAP_INSTALLER_VERSION,
        "manifest_hash": canonical_sha256(dict(payload)),
        "projection_filter": _require_str(envelope, "projection_filter"),
        "slice_id": _require_str(envelope, "slice_id"),
        "slice_version": _require_str(envelope, "slice_version"),
        "verification": "passed",
    }


def materialize_starmap_manifest(
    payload: Mapping[str, object],
    *,
    target: str | Path | None = None,
    dry_run: bool = False,
) -> dict[str, object]:
    """Materialize deterministic node-record files under a safe target directory."""

    verification = verify_starmap_manifest(payload)
    envelope = _manifest_envelope(payload)
    entries = _content_entries(envelope)
    plan = [_materialization_plan(entry) for entry in entries]
    _assert_no_path_conflicts(plan)
    materialized_hashes: dict[str, str] = {}
    for relative_path, content in plan:
        digest = hashlib.sha256(content).hexdigest()
        materialized_hashes[relative_path.as_posix()] = digest
    if not dry_run:
        if target is None:
            raise StarMapInstallerError("starmap_materialization_target_required")
        target_path = _validate_target_dir(Path(target))
        for relative_path, content in plan:
            _write_atomic(target_path / relative_path, content)
    return {
        **verification,
        "dry_run": dry_run,
        "materialized_file_count": len(plan),
        "materialized_hashes": materialized_hashes,
        "materialization": "planned" if dry_run else "written",
    }


def build_install_receipt(
    payload: Mapping[str, object],
    *,
    created_at_policy: str = "deterministic_test_fixture",
) -> dict[str, object]:
    """Build a deterministic local install receipt for a verified manifest."""

    result = materialize_starmap_manifest(payload, dry_run=True)
    envelope = _manifest_envelope(payload)
    receipt = {
        "content_hashes": result["materialized_hashes"],
        "created_at_policy": created_at_policy,
        "installer_version": STARMAP_INSTALLER_VERSION,
        "manifest_hash": result["manifest_hash"],
        "materialized_file_count": result["materialized_file_count"],
        "slice_id": _require_str(envelope, "slice_id"),
        "slice_version": _require_str(envelope, "slice_version"),
        "test_commands_declared": _test_commands_declared(
            _require_str(envelope, "projection_filter")
        ),
    }
    return {
        **receipt,
        "receipt_sha256": canonical_sha256(receipt),
    }


def merge_manifest_entries(
    payloads: Iterable[Mapping[str, object]],
) -> dict[str, object]:
    """Return deduped node/hash pairs or fail on conflicting overlaps."""

    seen: dict[str, str] = {}
    for payload in payloads:
        verify_starmap_manifest(payload)
        envelope = _manifest_envelope(payload)
        for entry in _content_entries(envelope):
            node_id = _require_str(entry, "node_id")
            record_sha256 = _require_str(entry, "record_sha256")
            prior = seen.get(node_id)
            if prior is not None and prior != record_sha256:
                raise StarMapInstallerError("starmap_overlap_hash_conflict")
            seen[node_id] = record_sha256
    return {
        "deduped_node_count": len(seen),
        "node_hashes": dict(sorted(seen.items())),
    }


def _manifest_envelope(payload: Mapping[str, object]) -> dict[str, object]:
    canonical_json = _require_str(payload, "canonical_json")
    try:
        envelope = json.loads(canonical_json)
    except json.JSONDecodeError as exc:
        raise StarMapInstallerError("starmap_manifest_canonical_json_invalid") from exc
    if not isinstance(envelope, dict):
        raise StarMapInstallerError("starmap_manifest_envelope_invalid")
    if set(envelope) != REQUIRED_ENVELOPE_KEYS:
        raise StarMapInstallerError("starmap_manifest_envelope_keys_invalid")
    if canonical_json_bytes(envelope).decode("utf-8") != canonical_json:
        raise StarMapInstallerError("starmap_manifest_canonical_json_not_canonical")
    for key in (
        "content_entries",
        "cross_section_ref_count",
        "exclusion_policy",
        "included_node_merkle_root",
        "installer_profile",
        "privacy_budget",
        "projection_filter",
        "public_rc_exclude",
        "receipt_sha256",
        "root_pointers",
        "runtime_version",
        "section_label",
        "semantic_loss_annotations",
        "slice_id",
        "slice_version",
        "source_lmdb_root_sha256",
    ):
        if payload.get(key) != envelope.get(key):
            raise StarMapInstallerError("starmap_manifest_envelope_mismatch")
    if envelope.get("public_rc_exclude") is not True:
        raise StarMapInstallerError("starmap_manifest_public_rc_exclude_invalid")
    if (
        isinstance(envelope.get("cross_section_ref_count"), bool)
        or not isinstance(envelope.get("cross_section_ref_count"), int)
        or int(envelope["cross_section_ref_count"]) < 0
    ):
        raise StarMapInstallerError("starmap_cross_section_ref_count_invalid")
    _require_sha256(_require_str(envelope, "source_lmdb_root_sha256"))
    _require_sha256(_require_str(envelope, "included_node_merkle_root"))
    return envelope


def _validate_fixture_passthrough_fields(payload: Mapping[str, object]) -> None:
    _require_str(payload, "cidv1")
    _require_str(payload, "dag_cbor_b64")
    _require_sha256(_require_str(payload, "sha256"))
    cose_value = payload.get("cose_sign1_b64")
    if cose_value != "":
        raise StarMapInstallerError("starmap_signed_fixture_not_supported")
    if payload.get("dev_signed") is not False:
        raise StarMapInstallerError("starmap_dev_signed_fixture_not_supported")


def _content_entries(envelope: Mapping[str, object]) -> list[dict[str, object]]:
    entries = envelope.get("content_entries")
    if not isinstance(entries, list) or not all(isinstance(entry, dict) for entry in entries):
        raise StarMapInstallerError("starmap_content_entries_invalid")
    seen: set[str] = set()
    normalized: list[dict[str, object]] = []
    for entry in entries:
        node_id = _require_str(entry, "node_id")
        if node_id in seen:
            raise StarMapInstallerError("starmap_duplicate_content_entry")
        seen.add(node_id)
        _require_sha256(_require_str(entry, "record_sha256"))
        normalized.append(dict(entry))
    if not normalized:
        raise StarMapInstallerError("starmap_content_entries_empty")
    root_pointers = envelope.get("root_pointers")
    if not isinstance(root_pointers, list) or not all(
        isinstance(item, str) and item for item in root_pointers
    ):
        raise StarMapInstallerError("starmap_root_pointers_invalid")
    annotations = envelope.get("semantic_loss_annotations")
    if not isinstance(annotations, list) or not all(
        isinstance(item, str) for item in annotations
    ):
        raise StarMapInstallerError("starmap_semantic_loss_invalid")
    return normalized


def _validate_public_entry(entry: Mapping[str, object]) -> None:
    if _require_str(entry, "export_category") not in ALLOWED_EXPORT_CATEGORIES:
        raise StarMapInstallerError("starmap_non_public_export_category")
    if _require_str(entry, "graph_projection") == "excluded_private_material":
        raise StarMapInstallerError("starmap_private_projection_rejected")
    if PUBLIC_MARKER in json.dumps(entry, sort_keys=True, separators=(",", ":")):
        raise StarMapInstallerError("starmap_public_rc_exclude_content_rejected")


def _verify_merkle_root(
    envelope: Mapping[str, object],
    entries: list[dict[str, object]],
) -> None:
    leaves = sorted(_require_str(entry, "record_sha256") for entry in entries)
    expected = hashlib.sha256("\n".join(leaves).encode("utf-8")).hexdigest()
    if _require_str(envelope, "included_node_merkle_root") != expected:
        raise StarMapInstallerError("starmap_manifest_merkle_root_mismatch")


def _entry_materialization_bytes(entry: Mapping[str, object]) -> bytes:
    encoded = canonical_json_bytes(entry) + b"\n"
    if PUBLIC_MARKER.encode("utf-8") in encoded:
        raise StarMapInstallerError("starmap_public_rc_exclude_content_rejected")
    return encoded


def _materialization_plan(entry: Mapping[str, object]) -> tuple[Path, bytes]:
    materialization_path = str(entry.get("materialization_path", ""))
    if materialization_path:
        relative_path = Path(materialization_path)
    else:
        relative_path = Path("nodes") / f"{_safe_filename(_require_str(entry, 'node_id'))}.node.json"
    _validate_relative_path(relative_path)
    return relative_path, _entry_materialization_bytes(entry)


def _assert_no_path_conflicts(plan: Iterable[tuple[Path, bytes]]) -> None:
    seen: dict[str, str] = {}
    for relative_path, content in plan:
        path_key = relative_path.as_posix()
        digest = hashlib.sha256(content).hexdigest()
        prior = seen.get(path_key)
        if prior is not None and prior != digest:
            raise StarMapInstallerError("starmap_materialization_path_conflict")
        seen[path_key] = digest


def _validate_relative_path(path: Path) -> None:
    if path.is_absolute():
        raise StarMapInstallerError("starmap_absolute_path_rejected")
    parts = path.parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise StarMapInstallerError("starmap_path_traversal_rejected")


def _validate_target_dir(target: Path) -> Path:
    resolved = target.expanduser().resolve()
    if resolved == Path(resolved.anchor):
        raise StarMapInstallerError("starmap_target_root_rejected")
    resolved.mkdir(parents=True, exist_ok=True)
    if not resolved.is_dir():
        raise StarMapInstallerError("starmap_target_not_directory")
    return resolved


def _write_atomic(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def _test_commands_declared(projection_filter: str) -> list[str]:
    commands = [
        "ilc-starmap-installer verify <manifest>",
        "ilc-starmap-installer materialize --dry-run <manifest>",
        "ilc-starmap-installer receipt <manifest>",
    ]
    if projection_filter == "economic_soft_rc_slice":
        commands.append("ilc-starmap-installer materialize <manifest> --target <dir>")
    return commands


def _require_str(payload: Mapping[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or value == "":
        raise StarMapInstallerError(f"starmap_{key}_invalid")
    return value


def _safe_filename(value: str) -> str:
    return "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in value)


def _require_sha256(value: str) -> None:
    if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
        raise StarMapInstallerError("starmap_sha256_invalid")


def _reject_float(value: object) -> None:
    if isinstance(value, float):
        raise StarMapInstallerError("starmap_float_not_allowed")
    if isinstance(value, Mapping):
        for key, item in value.items():
            _reject_float(key)
            _reject_float(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _reject_float(item)


__all__ = [
    "MAX_MANIFEST_BYTES",
    "STARMAP_INSTALLER_VERSION",
    "StarMapInstallerError",
    "build_install_receipt",
    "canonical_json_bytes",
    "canonical_sha256",
    "load_manifest_payload",
    "materialize_starmap_manifest",
    "merge_manifest_entries",
    "verify_starmap_manifest",
]
