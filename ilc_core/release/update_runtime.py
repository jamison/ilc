# SPDX-License-Identifier: AGPL-3.0-only
"""Pure helpers for the GAP-PUBLIC-INSTALL-03 ``ilc update`` command."""

from __future__ import annotations

import hashlib
import importlib.metadata
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ilc_core.release.installable_release_manifest import ALLOWED_CHANNELS


_CANONICAL_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_WHEEL_VERSION_RE = re.compile(
    r"(?i)(?:^|/)ilc_core-(?P<version>[0-9]+(?:\.[0-9]+){1,2})(?:[-_][^/]*)?\.whl$"
)


def select_update_artifact(manifest: dict[str, Any], channel: str) -> dict[str, Any]:
    """Return the pure-Python wheel artifact for ``channel``.

    The installable manifest validator has already enforced artifact shape; this
    helper keeps the selection policy unit-testable and independent of network
    and process-execution concerns.
    """

    if channel not in ALLOWED_CHANNELS:
        raise ValueError(f"ilc_update_invalid_channel:{channel}")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError("ilc_update_manifest_artifacts_invalid")
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        if (
            artifact.get("artifact_type") == "python_wheel"
            and artifact.get("channel") == channel
            and artifact.get("platform") == "any"
            and artifact.get("arch") == "any"
        ):
            return dict(artifact)
    raise ValueError(f"ilc_update_no_wheel_for_channel:{channel}")


def canonical_hash_hex(expected_canonical_hash: str) -> str:
    """Return the SHA-256 hex portion of a canonical ``sha256:<hex>`` string."""

    if not isinstance(expected_canonical_hash, str):
        raise ValueError("ilc_update_invalid_canonical_hash")
    if not _CANONICAL_SHA256_RE.fullmatch(expected_canonical_hash):
        raise ValueError("ilc_update_invalid_canonical_hash")
    return expected_canonical_hash.removeprefix("sha256:")


def verify_download_hash(path: Path, expected_canonical_hash: str) -> None:
    """Verify a downloaded wheel file against the expected SHA-256."""

    expected_hex = canonical_hash_hex(expected_canonical_hash)
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != expected_hex:
        raise ValueError("ilc_update_hash_mismatch")


def download_size_cap(expected_size_bytes: int) -> int:
    """Return an integer 110% size cap for an expected artifact size."""

    if isinstance(expected_size_bytes, bool) or not isinstance(expected_size_bytes, int):
        raise ValueError("ilc_update_invalid_size_bytes")
    if expected_size_bytes <= 0:
        raise ValueError("ilc_update_invalid_size_bytes")
    return (expected_size_bytes * 11 + 9) // 10


def enforce_download_size(actual_size_bytes: int, expected_size_bytes: int) -> None:
    """Fail if the downloaded payload exceeds the allowed cap."""

    if isinstance(actual_size_bytes, bool) or not isinstance(actual_size_bytes, int):
        raise ValueError("ilc_update_invalid_download_size")
    if actual_size_bytes < 0:
        raise ValueError("ilc_update_invalid_download_size")
    if actual_size_bytes > download_size_cap(expected_size_bytes):
        raise ValueError("ilc_update_size_exceeded")


def artifact_version(artifact: dict[str, Any]) -> str:
    """Extract the package version from an artifact wheel URL."""

    url = artifact.get("download_url")
    if not isinstance(url, str) or not url:
        raise ValueError("ilc_update_artifact_download_url_invalid")
    path = urlparse(url).path
    match = _WHEEL_VERSION_RE.search(path)
    if match is None:
        raise ValueError("ilc_update_artifact_version_unparseable")
    return match.group("version")


def installed_ilc_core_version() -> str | None:
    """Return the installed package version, or ``None`` when not installed."""

    try:
        return importlib.metadata.version("ilc-core")
    except importlib.metadata.PackageNotFoundError:
        return None


def is_already_current(artifact: dict[str, Any]) -> bool:
    """Return advisory version-match status for dry-run visibility.

    This does not prove local wheel hash equality and must not be used as a
    non-dry-run skip condition.
    """

    installed = installed_ilc_core_version()
    if installed is None:
        return False
    return installed == artifact_version(artifact)
