# SPDX-License-Identifier: AGPL-3.0-only
"""Detached release signature envelope schema helpers."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping


class InstallableReleaseSignatureError(ValueError):
    """Raised when a release signature envelope is malformed."""


SCHEMA_VERSION = "GAP_RELEASE_SIGN_00b_v0.1"
SIGNED_PREIMAGE_DOMAIN = "ILC_RELEASE_ARTIFACT_SIGNATURE_V1"
SIGNING_ALGORITHM = "Ed25519"
SIGNED_AT_EPOCH_ZERO = "1970-01-01T00:00:00Z"
SIGNED_PREIMAGE_ALGORITHM = "sha256_of_canonical_json"

_HEX_32_RE = re.compile(r"^[0-9a-f]{64}$")
_HEX_64_RE = re.compile(r"^[0-9a-f]{128}$")
_ARTIFACT_ID_RE = re.compile(r"^ilc-artifact:[a-z0-9][a-z0-9-]*@phase-[1-9][0-9]*$")
_RELEASE_ID_RE = re.compile(r"^ilc-core-[0-9]+\.[0-9]+\.[0-9]+$")
_MAX_STRING_CHARS = 512
_MAX_ENVELOPES = 32
_MAX_DEPTH = 8

_ENVELOPE_FIELDS = frozenset(
    {
        "schema_version",
        "release_id",
        "artifact_id",
        "artifact_sha256",
        "signing_algorithm",
        "signer_public_key_hex",
        "signature_hex",
        "signed_at",
        "signed_preimage_algorithm",
        "signed_preimage_domain",
        "signed_preimage_sha256",
    }
)
_ENVELOPE_SET_FIELDS = frozenset({"schema_version", "version", "envelopes"})


def _fail(token: str) -> None:
    raise InstallableReleaseSignatureError(token)


def _reject_floating_numbers(value: Any, *, field_path: str, depth: int = 0) -> None:
    if depth > _MAX_DEPTH:
        _fail(f"release_envelope_nesting_too_deep:{field_path}")
    if type(value) is type(0.0):
        _fail(f"release_envelope_number_rejected:{field_path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_floating_numbers(child, field_path=f"{field_path}.{key}", depth=depth + 1)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_floating_numbers(child, field_path=f"{field_path}[{index}]", depth=depth + 1)


def _require_exact_keys(
    payload: Mapping[str, Any],
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


def _require_string(value: Any, *, field: str, max_chars: int = _MAX_STRING_CHARS) -> str:
    if not isinstance(value, str) or not value:
        _fail(f"release_envelope_invalid_string:{field}")
    if len(value) > max_chars:
        _fail(f"release_envelope_string_too_long:{field}")
    return value


def _require_literal(value: Any, *, field: str, expected: str, token: str) -> str:
    text = _require_string(value, field=field)
    if text != expected:
        _fail(token)
    return text


def _require_hex(
    value: Any,
    *,
    field: str,
    pattern: re.Pattern[str],
    token: str,
    allow_empty: bool = False,
) -> str:
    if allow_empty and value == "":
        return ""
    if value == "":
        _fail(token)
    text = _require_string(value, field=field)
    if pattern.fullmatch(text) is None:
        _fail(token)
    return text


def _normalize_artifact_sha256(artifact_sha256: str) -> str:
    if artifact_sha256.startswith("sha256:"):
        artifact_sha256 = artifact_sha256.removeprefix("sha256:")
    if _HEX_32_RE.fullmatch(artifact_sha256) is None:
        _fail("release_envelope_artifact_sha256_invalid")
    return artifact_sha256


def canonical_envelope_json(envelope: Mapping[str, Any]) -> str:
    """Return canonical JSON for release signature envelope material."""

    return json.dumps(
        envelope,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def signed_preimage_payload(
    *,
    release_id: str,
    artifact_id: str,
    artifact_sha256: str,
) -> dict[str, str]:
    """Build the canonical payload whose SHA-256 digest is signed in 00c."""

    release_id = _require_string(release_id, field="release_id", max_chars=160)
    if _RELEASE_ID_RE.fullmatch(release_id) is None:
        _fail("release_envelope_release_id_invalid")
    artifact_id = _require_string(artifact_id, field="artifact_id", max_chars=160)
    if _ARTIFACT_ID_RE.fullmatch(artifact_id) is None:
        _fail("release_envelope_artifact_id_invalid")
    artifact_sha256 = _normalize_artifact_sha256(artifact_sha256)
    return {
        "artifact_id": artifact_id,
        "artifact_sha256": artifact_sha256,
        "release_id": release_id,
        "schema_version": SCHEMA_VERSION,
        "signed_at": SIGNED_AT_EPOCH_ZERO,
        "signed_preimage_domain": SIGNED_PREIMAGE_DOMAIN,
        "signing_algorithm": SIGNING_ALGORITHM,
    }


def compute_signed_preimage_sha256(
    *,
    release_id: str,
    artifact_id: str,
    artifact_sha256: str,
) -> str:
    """Return SHA-256 of the canonical signed-preimage payload."""

    payload = signed_preimage_payload(
        release_id=release_id,
        artifact_id=artifact_id,
        artifact_sha256=artifact_sha256,
    )
    return hashlib.sha256(canonical_envelope_json(payload).encode("utf-8")).hexdigest()


def build_envelope_skeleton(
    *,
    release_id: str,
    artifact_id: str,
    artifact_sha256: str,
) -> dict[str, str]:
    """Return an unsigned envelope skeleton for GAP-RELEASE-SIGN-00c ceremony input."""

    artifact_sha256 = _normalize_artifact_sha256(artifact_sha256)
    preimage_sha256 = compute_signed_preimage_sha256(
        release_id=release_id,
        artifact_id=artifact_id,
        artifact_sha256=artifact_sha256,
    )
    return {
        "artifact_id": artifact_id,
        "artifact_sha256": artifact_sha256,
        "release_id": release_id,
        "schema_version": SCHEMA_VERSION,
        "signature_hex": "",
        "signed_at": SIGNED_AT_EPOCH_ZERO,
        "signed_preimage_algorithm": SIGNED_PREIMAGE_ALGORITHM,
        "signed_preimage_domain": SIGNED_PREIMAGE_DOMAIN,
        "signed_preimage_sha256": preimage_sha256,
        "signer_public_key_hex": "",
        "signing_algorithm": SIGNING_ALGORITHM,
    }


def validate_envelope(
    envelope: Mapping[str, Any],
    *,
    allow_unsigned_placeholders: bool = False,
) -> None:
    """Validate one detached release signature envelope structurally."""

    if not isinstance(envelope, Mapping):
        _fail("release_envelope_not_object")
    _reject_floating_numbers(envelope, field_path="envelope")
    _require_exact_keys(
        envelope,
        expected_keys=_ENVELOPE_FIELDS,
        token_prefix="release_envelope",
    )
    _require_literal(
        envelope["schema_version"],
        field="schema_version",
        expected=SCHEMA_VERSION,
        token="release_envelope_schema_version_invalid",
    )
    release_id = _require_string(envelope["release_id"], field="release_id", max_chars=160)
    if _RELEASE_ID_RE.fullmatch(release_id) is None:
        _fail("release_envelope_release_id_invalid")
    artifact_id = _require_string(envelope["artifact_id"], field="artifact_id", max_chars=160)
    if _ARTIFACT_ID_RE.fullmatch(artifact_id) is None:
        _fail("release_envelope_artifact_id_invalid")
    artifact_sha256 = _require_hex(
        envelope["artifact_sha256"],
        field="artifact_sha256",
        pattern=_HEX_32_RE,
        token="release_envelope_artifact_sha256_invalid",
    )
    _require_literal(
        envelope["signing_algorithm"],
        field="signing_algorithm",
        expected=SIGNING_ALGORITHM,
        token="release_envelope_signing_algorithm_invalid",
    )
    _require_hex(
        envelope["signer_public_key_hex"],
        field="signer_public_key_hex",
        pattern=_HEX_32_RE,
        token="release_envelope_public_key_invalid",
        allow_empty=allow_unsigned_placeholders,
    )
    _require_hex(
        envelope["signature_hex"],
        field="signature_hex",
        pattern=_HEX_64_RE,
        token="release_envelope_signature_hex_invalid",
        allow_empty=allow_unsigned_placeholders,
    )
    _require_literal(
        envelope["signed_at"],
        field="signed_at",
        expected=SIGNED_AT_EPOCH_ZERO,
        token="release_envelope_signed_at_invalid",
    )
    _require_literal(
        envelope["signed_preimage_algorithm"],
        field="signed_preimage_algorithm",
        expected=SIGNED_PREIMAGE_ALGORITHM,
        token="release_envelope_preimage_algorithm_invalid",
    )
    _require_literal(
        envelope["signed_preimage_domain"],
        field="signed_preimage_domain",
        expected=SIGNED_PREIMAGE_DOMAIN,
        token="release_envelope_preimage_domain_invalid",
    )
    expected_preimage_sha256 = compute_signed_preimage_sha256(
        release_id=release_id,
        artifact_id=artifact_id,
        artifact_sha256=artifact_sha256,
    )
    signed_preimage_sha256 = _require_hex(
        envelope["signed_preimage_sha256"],
        field="signed_preimage_sha256",
        pattern=_HEX_32_RE,
        token="release_envelope_preimage_sha256_invalid",
    )
    if signed_preimage_sha256 != expected_preimage_sha256:
        _fail("release_envelope_preimage_sha256_mismatch")


def validate_envelope_for_artifact(
    envelope: Mapping[str, Any],
    artifact: Mapping[str, Any],
    *,
    release_id: str,
    allow_unsigned_placeholders: bool = False,
) -> None:
    """Validate that an envelope is bound to one manifest artifact record."""

    validate_envelope(envelope, allow_unsigned_placeholders=allow_unsigned_placeholders)
    if envelope["release_id"] != release_id:
        _fail("release_envelope_release_id_mismatch")
    if envelope["artifact_id"] != artifact.get("artifact_id"):
        _fail("release_envelope_artifact_id_mismatch")
    canonical_hash = artifact.get("canonical_hash")
    if not isinstance(canonical_hash, str) or not canonical_hash.startswith("sha256:"):
        _fail("release_envelope_manifest_hash_invalid")
    if envelope["artifact_sha256"] != _normalize_artifact_sha256(canonical_hash):
        _fail("release_envelope_artifact_sha256_mismatch")


def validate_envelope_set(
    envelope_set: Mapping[str, Any],
    *,
    manifest: Mapping[str, Any] | None = None,
    allow_unsigned_placeholders: bool = False,
) -> None:
    """Validate a detached envelope set, optionally against a manifest."""

    if not isinstance(envelope_set, Mapping):
        _fail("release_envelope_set_not_object")
    _reject_floating_numbers(envelope_set, field_path="envelope_set")
    _require_exact_keys(
        envelope_set,
        expected_keys=_ENVELOPE_SET_FIELDS,
        token_prefix="release_envelope_set",
    )
    _require_literal(
        envelope_set["schema_version"],
        field="schema_version",
        expected=SCHEMA_VERSION,
        token="release_envelope_set_schema_version_invalid",
    )
    version = _require_string(envelope_set["version"], field="version", max_chars=80)
    release_id = f"ilc-core-{version}"
    envelopes = envelope_set["envelopes"]
    if not isinstance(envelopes, Mapping) or not envelopes:
        _fail("release_envelope_set_envelopes_invalid")
    if len(envelopes) > _MAX_ENVELOPES:
        _fail("release_envelope_set_too_many_envelopes")

    artifacts_by_id: dict[str, Mapping[str, Any]] | None = None
    if manifest is not None:
        if not isinstance(manifest, Mapping):
            _fail("release_envelope_manifest_not_object")
        if manifest.get("release_id") != release_id:
            _fail("release_envelope_manifest_release_id_mismatch")
        artifacts = manifest.get("artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            _fail("release_envelope_manifest_artifacts_invalid")
        artifacts_by_id = {}
        for artifact in artifacts:
            if not isinstance(artifact, Mapping):
                _fail("release_envelope_manifest_artifact_not_object")
            artifact_id = artifact.get("artifact_id")
            if not isinstance(artifact_id, str):
                _fail("release_envelope_manifest_artifact_id_invalid")
            artifacts_by_id[artifact_id] = artifact
        if set(envelopes) != set(artifacts_by_id):
            _fail("release_envelope_set_artifact_coverage_mismatch")

    for artifact_id, envelope in envelopes.items():
        if not isinstance(artifact_id, str):
            _fail("release_envelope_set_artifact_key_invalid")
        if not isinstance(envelope, Mapping):
            _fail("release_envelope_set_envelope_not_object")
        if envelope.get("artifact_id") != artifact_id:
            _fail("release_envelope_set_key_mismatch")
        if artifacts_by_id is None:
            validate_envelope(envelope, allow_unsigned_placeholders=allow_unsigned_placeholders)
        else:
            validate_envelope_for_artifact(
                envelope,
                artifacts_by_id[artifact_id],
                release_id=release_id,
                allow_unsigned_placeholders=allow_unsigned_placeholders,
            )


__all__ = [
    "InstallableReleaseSignatureError",
    "SCHEMA_VERSION",
    "SIGNED_AT_EPOCH_ZERO",
    "SIGNED_PREIMAGE_ALGORITHM",
    "SIGNED_PREIMAGE_DOMAIN",
    "SIGNING_ALGORITHM",
    "build_envelope_skeleton",
    "canonical_envelope_json",
    "compute_signed_preimage_sha256",
    "signed_preimage_payload",
    "validate_envelope",
    "validate_envelope_for_artifact",
    "validate_envelope_set",
]
