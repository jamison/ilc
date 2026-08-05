"""Sync checks between tools/install.sh and the committed installable manifest."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ilc_core.release.installable_release_manifest import load_installable_release_manifest


_ASSIGNMENT_RE = re.compile(r'^(?P<name>[A-Z0-9_]+)="(?P<value>[^"]*)"$', re.MULTILINE)
_MAX_INSTALL_SH_BYTES = 1_048_576


def _load_shell_assignments(path: Path) -> dict[str, str]:
    if path.stat().st_size > _MAX_INSTALL_SH_BYTES:
        raise ValueError("install_sh_manifest_sync_failed:install_sh_too_large")
    text = path.read_text(encoding="utf-8")
    return {match.group("name"): match.group("value") for match in _ASSIGNMENT_RE.finditer(text)}


def _wheel_record(manifest: dict[str, Any]) -> dict[str, Any]:
    for record in manifest.get("artifacts", []):
        if record.get("channel") == "rc" and record.get("artifact_type") == "python_wheel":
            return record
    raise ValueError("install_sh_manifest_sync_failed:python_wheel_record_missing")


def _require_sync(
    assignments: dict[str, str],
    *,
    shell_field: str,
    expected: str,
) -> None:
    actual = assignments.get(shell_field)
    if actual != expected:
        raise ValueError(
            f"install_sh_manifest_sync_failed:{shell_field}:{expected}:{actual}"
        )


def verify_install_sh_manifest_sync(
    install_sh_path: str | Path,
    manifest_path: str | Path,
) -> None:
    """Raise ``ValueError`` if embedded installer values drift from the manifest."""

    manifest = load_installable_release_manifest(manifest_path)
    record = _wheel_record(manifest)
    canonical_hash = record["canonical_hash"]
    if not canonical_hash.startswith("sha256:"):
        raise ValueError("install_sh_manifest_sync_failed:canonical_hash_prefix")
    assignments = _load_shell_assignments(Path(install_sh_path))
    _require_sync(
        assignments,
        shell_field="RC_WHEEL_URL",
        expected=str(record["download_url"]),
    )
    _require_sync(
        assignments,
        shell_field="RC_WHEEL_SHA256",
        expected=canonical_hash.removeprefix("sha256:"),
    )
    _require_sync(
        assignments,
        shell_field="RC_WHEEL_SIZE",
        expected=str(record["size_bytes"]),
    )
    min_python_version = str(record["min_python_version"])
    _require_sync(
        assignments,
        shell_field="RC_MIN_PYTHON_MINOR",
        expected=min_python_version.split(".", maxsplit=1)[1],
    )
