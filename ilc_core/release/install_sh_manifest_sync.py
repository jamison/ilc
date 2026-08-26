"""Sync checks between tools/install.sh and the committed installable manifest."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ilc_core.release.installable_release_manifest import load_installable_release_manifest


_ASSIGNMENT_RE = re.compile(r'^(?P<name>[A-Z0-9_]+)="(?P<value>[^"]*)"$', re.MULTILINE)
_SYNCED_ASSIGNMENT_NAMES = frozenset(
    {
        "RC_WHEEL_URL",
        "RC_WHEEL_SHA256",
        "RC_WHEEL_SIZE",
        "RC_MIN_PYTHON_MINOR",
        "TMP_WHEEL",
    }
)
_ILC_CORE_PY3_ANY_WHEEL_RE = re.compile(
    r"^ilc_core-[0-9]+(?:\.[0-9]+){1,2}-py3-none-any\.whl$"
)
_MAX_INSTALL_SH_BYTES = 1_048_576


def _load_shell_assignments(path: Path) -> dict[str, str]:
    if path.stat().st_size > _MAX_INSTALL_SH_BYTES:
        raise ValueError("install_sh_manifest_sync_failed:install_sh_too_large")
    text = path.read_text(encoding="utf-8")
    assignments: dict[str, str] = {}
    for match in _ASSIGNMENT_RE.finditer(text):
        name = match.group("name")
        value = match.group("value")
        previous = assignments.get(name)
        if name in _SYNCED_ASSIGNMENT_NAMES and previous is not None:
            if not (previous == "" and value != ""):
                raise ValueError(
                    f"install_sh_manifest_sync_failed:duplicate_assignment:{name}"
                )
        assignments[name] = value
    return assignments


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


def _require_tmp_wheel_sync(assignments: dict[str, str], expected_basename: str) -> None:
    if _ILC_CORE_PY3_ANY_WHEEL_RE.fullmatch(expected_basename) is None:
        raise ValueError(
            f"install_sh_manifest_sync_failed:wheel_filename_invalid:{expected_basename}"
        )
    actual = assignments.get("TMP_WHEEL")
    expected = "${TMP_DIR}/" + expected_basename
    dynamic_expected = "${TMP_DIR}/${WHEEL_BASENAME}"
    if actual == dynamic_expected:
        if assignments.get("WHEEL_BASENAME") != "${RC_WHEEL_URL##*/}":
            raise ValueError(
                "install_sh_manifest_sync_failed:WHEEL_BASENAME:${RC_WHEEL_URL##*/}:"
                f"{assignments.get('WHEEL_BASENAME')}"
            )
        return
    if actual != expected:
        raise ValueError(
            f"install_sh_manifest_sync_failed:TMP_WHEEL:{expected}:{actual}"
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
    wheel_basename = str(record["download_url"]).rsplit("/", maxsplit=1)[-1]
    _require_tmp_wheel_sync(assignments, wheel_basename)
