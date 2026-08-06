"""Validator for GAP-PUBLIC-INSTALL-01 installable release manifests."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


class InstallableReleaseManifestError(ValueError):
    """Raised when an installable release manifest is not canonical enough to use."""


PHASE_1213_ARTIFACT_TYPES = frozenset(
    {
        "runtime_module",
        "genesis_bundle",
        "cli_binary",
        "documentation_bundle",
        "source_release_tarball",
        "public_repository_tag",
        "container_image",
        "star_map_release_envelope",
        "operator_bootstrap_bundle",
        "verification_bundle",
    }
)

INSTALLABLE_ARTIFACT_TYPES = frozenset(
    {
        "python_wheel",
        "python_sdist",
        "install_script",
    }
)

ALLOWED_ARTIFACT_TYPES = PHASE_1213_ARTIFACT_TYPES | INSTALLABLE_ARTIFACT_TYPES
ALLOWED_PLATFORMS = frozenset({"linux", "darwin", "windows", "any"})
ALLOWED_ARCHES = frozenset({"amd64", "arm64", "any"})
ALLOWED_CHANNELS = frozenset({"stable", "rc", "dev"})
ALLOWED_SIGNING_STATUSES = frozenset({"signed", "unsigned", "deferred"})

REQUIRED_1213_FIELDS = frozenset(
    {
        "artifact_id",
        "artifact_type",
        "canonical_hash",
        "lineage_reference",
        "produced_phase",
        "ratification_token",
        "signing_status",
    }
)
REQUIRED_INSTALLABLE_FIELDS = frozenset(
    {
        "platform",
        "arch",
        "channel",
        "size_bytes",
        "download_url",
    }
)
OPTIONAL_ARTIFACT_FIELDS = frozenset({"min_python_version"})
ALLOWED_ARTIFACT_FIELDS = (
    REQUIRED_1213_FIELDS | REQUIRED_INSTALLABLE_FIELDS | OPTIONAL_ARTIFACT_FIELDS
)
REQUIRED_TOP_LEVEL_FIELDS = frozenset(
    {
        "manifest_schema_version",
        "release_id",
        "channel",
        "manifest_produced_phase",
        "non_claims",
        "artifacts",
    }
)

_ARTIFACT_ID_RE = re.compile(r"^ilc-artifact:[a-z0-9][a-z0-9-]*@phase-[1-9][0-9]*$")
_CANONICAL_HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_LINEAGE_RE = re.compile(
    r"^(genesis:v[0-9]+(?:\.[0-9]+)*|artifact:ilc-artifact:[a-z0-9][a-z0-9-]*@phase-[1-9][0-9]*@sha256:[0-9a-f]{64})$"
)
_MIN_PYTHON_VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+$")


def _fail(token: str) -> None:
    raise InstallableReleaseManifestError(token)


def _require_exact_keys(
    payload: dict[str, Any],
    *,
    expected_keys: frozenset[str],
    token_prefix: str,
) -> None:
    actual = set(payload)
    missing = expected_keys - actual
    extra = actual - expected_keys
    if missing:
        _fail(f"{token_prefix}_missing_field:{sorted(missing)[0]}")
    if extra:
        _fail(f"{token_prefix}_extra_field:{sorted(extra)[0]}")


def _require_string(value: Any, *, field: str, max_chars: int = 2048) -> str:
    if not isinstance(value, str) or not value:
        _fail(f"installable_manifest_invalid_string:{field}")
    if len(value) > max_chars:
        _fail(f"installable_manifest_string_too_long:{field}")
    return value


def _require_positive_int(value: Any, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        _fail(f"installable_manifest_invalid_integer:{field}")
    if value <= 0:
        _fail(f"installable_manifest_non_positive_integer:{field}")
    return value


def _require_allowed(value: Any, *, field: str, allowed: frozenset[str]) -> str:
    text = _require_string(value, field=field)
    if text not in allowed:
        _fail(f"installable_manifest_invalid_{field}:{text}")
    return text


def _reject_floating_numbers(value: Any, *, field_path: str) -> None:
    if isinstance(value, float):
        _fail(f"installable_manifest_float_rejected:{field_path}")
    if isinstance(value, dict):
        for key, child in value.items():
            _reject_floating_numbers(child, field_path=f"{field_path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_floating_numbers(child, field_path=f"{field_path}[{index}]")


def _validate_artifact(record: Any, *, index: int, manifest_channel: str) -> None:
    if not isinstance(record, dict):
        _fail(f"installable_manifest_artifact_not_object:{index}")
    required = REQUIRED_1213_FIELDS | REQUIRED_INSTALLABLE_FIELDS
    if record.get("artifact_type") in {"python_wheel", "python_sdist"}:
        required = required | frozenset({"min_python_version"})
    _require_exact_keys(
        record,
        expected_keys=required,
        token_prefix=f"installable_manifest_artifact_{index}",
    )

    artifact_id = _require_string(record["artifact_id"], field="artifact_id", max_chars=160)
    if not _ARTIFACT_ID_RE.fullmatch(artifact_id):
        _fail(f"installable_manifest_invalid_artifact_id:{artifact_id}")

    artifact_type = _require_allowed(
        record["artifact_type"],
        field="artifact_type",
        allowed=ALLOWED_ARTIFACT_TYPES,
    )
    canonical_hash = _require_string(
        record["canonical_hash"], field="canonical_hash", max_chars=71
    )
    if not _CANONICAL_HASH_RE.fullmatch(canonical_hash):
        _fail("installable_manifest_invalid_canonical_hash")

    lineage_reference = _require_string(
        record["lineage_reference"], field="lineage_reference", max_chars=260
    )
    if not _LINEAGE_RE.fullmatch(lineage_reference):
        _fail("installable_manifest_invalid_lineage_reference")

    _require_positive_int(record["produced_phase"], field="produced_phase")
    _require_string(record["ratification_token"], field="ratification_token", max_chars=160)
    _require_allowed(
        record["signing_status"],
        field="signing_status",
        allowed=ALLOWED_SIGNING_STATUSES,
    )
    _require_allowed(record["platform"], field="platform", allowed=ALLOWED_PLATFORMS)
    _require_allowed(record["arch"], field="arch", allowed=ALLOWED_ARCHES)
    channel = _require_allowed(record["channel"], field="channel", allowed=ALLOWED_CHANNELS)
    if channel != manifest_channel:
        _fail("installable_manifest_artifact_channel_mismatch")
    _require_positive_int(record["size_bytes"], field="size_bytes")

    download_url = _require_string(record["download_url"], field="download_url", max_chars=2048)
    if not download_url.startswith("https://"):
        _fail("installable_manifest_download_url_not_https")
    if "example." in download_url or "placeholder" in download_url.lower():
        _fail("installable_manifest_placeholder_download_url")

    if artifact_type in {"python_wheel", "python_sdist"}:
        min_python_version = _require_string(
            record["min_python_version"],
            field="min_python_version",
            max_chars=16,
        )
        if not _MIN_PYTHON_VERSION_RE.fullmatch(min_python_version):
            _fail("installable_manifest_invalid_min_python_version")


def validate_installable_release_manifest(manifest: dict[str, Any]) -> None:
    """Validate an installable release manifest.

    Raises ``InstallableReleaseManifestError`` with a stable token string on failure.
    """

    if not isinstance(manifest, dict):
        _fail("installable_manifest_not_object")
    _reject_floating_numbers(manifest, field_path="manifest")
    _require_exact_keys(
        manifest,
        expected_keys=REQUIRED_TOP_LEVEL_FIELDS,
        token_prefix="installable_manifest_top_level",
    )

    _require_string(
        manifest["manifest_schema_version"],
        field="manifest_schema_version",
        max_chars=96,
    )
    _require_string(manifest["release_id"], field="release_id", max_chars=160)
    channel = _require_allowed(manifest["channel"], field="channel", allowed=ALLOWED_CHANNELS)
    _require_positive_int(
        manifest["manifest_produced_phase"],
        field="manifest_produced_phase",
    )

    non_claims = manifest["non_claims"]
    if not isinstance(non_claims, list) or not non_claims:
        _fail("installable_manifest_non_claims_invalid")
    for index, item in enumerate(non_claims):
        _require_string(item, field=f"non_claims[{index}]", max_chars=160)

    artifacts = manifest["artifacts"]
    if not isinstance(artifacts, list) or not artifacts:
        _fail("installable_manifest_artifacts_invalid")
    seen_ids: set[str] = set()
    for index, record in enumerate(artifacts):
        _validate_artifact(record, index=index, manifest_channel=channel)
        artifact_id = record["artifact_id"]
        if artifact_id in seen_ids:
            _fail(f"installable_manifest_duplicate_artifact_id:{artifact_id}")
        seen_ids.add(artifact_id)


def canonical_installable_release_manifest_bytes(manifest: dict[str, Any]) -> bytes:
    """Return canonical JSON bytes for a validated installable release manifest."""

    validate_installable_release_manifest(manifest)
    return json.dumps(
        manifest,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _reject_non_finite_constant(value: str) -> None:
    _fail(f"installable_manifest_non_finite_json_constant:{value}")


def load_installable_release_manifest(path: str | Path) -> dict[str, Any]:
    """Load and validate an installable release manifest from JSON."""

    payload = Path(path).read_text(encoding="utf-8")
    try:
        manifest = json.loads(payload, parse_constant=_reject_non_finite_constant)
    except json.JSONDecodeError as exc:
        raise InstallableReleaseManifestError("installable_manifest_invalid_json") from exc
    if not isinstance(manifest, dict):
        _fail("installable_manifest_not_object")
    validate_installable_release_manifest(manifest)
    return manifest
