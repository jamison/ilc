# SPDX-License-Identifier: AGPL-3.0-only
"""Opt-in Ed25519 release envelope verification for installers and updates."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlparse

from ilc_core.release.installable_release_signature import (
    InstallableReleaseSignatureError,
    compute_signed_preimage_sha256,
    validate_envelope,
    validate_envelope_set,
)


MAX_ENVELOPE_SET_BYTES = 65536
HTTP_TIMEOUT_SECONDS = 30
HTTP_CHUNK_BYTES = 8192
PUBLIC_RC_RELEASE_SIGNER_PUBLIC_KEY_HEX = (
    "5bf71c1e0ac93f2d7414b0dc315161fc4a57462c198ba1618e2890ec89a5b15a"
)

_HEX_32_BYTES_RE = re.compile(r"^[0-9a-f]{64}$")


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"release_envelope_set_non_finite_json_constant:{value}")


def _require_sha256_hex(value: Any, *, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"release_envelope_invalid_sha256:{field}")
    if value.startswith("sha256:"):
        value = value.removeprefix("sha256:")
    if _HEX_32_BYTES_RE.fullmatch(value) is None:
        raise ValueError(f"release_envelope_invalid_sha256:{field}")
    return value


def _read_local_envelope_set(path_text: str) -> bytes:
    path = Path(path_text).expanduser()
    if not path.is_file():
        raise ValueError("release_envelope_set_path_not_found")
    with path.open("rb") as handle:
        payload = handle.read(MAX_ENVELOPE_SET_BYTES + 1)
    if len(payload) > MAX_ENVELOPE_SET_BYTES:
        raise ValueError("release_envelope_set_too_large")
    return payload


def _resolve_local_envelope_ref(path_text: str, *, base_dir: Path | None = None) -> str:
    path = Path(path_text).expanduser()
    if path.is_absolute() or base_dir is None:
        return str(path)
    return str((base_dir / path).resolve())


def _fetch_https_envelope_set(url: str) -> bytes:
    try:
        import requests
    except ImportError as exc:
        raise ValueError("release_envelope_fetch_requests_not_available") from exc
    try:
        response = requests.get(
            url,
            stream=True,
            timeout=HTTP_TIMEOUT_SECONDS,
            verify=True,
            allow_redirects=False,
        )
    except requests.RequestException as exc:
        raise ValueError("release_envelope_fetch_failed:network") from exc
    if response.status_code in {301, 302, 303, 307, 308}:
        raise ValueError("release_envelope_fetch_redirect_forbidden")
    if response.status_code != 200:
        raise ValueError(f"release_envelope_fetch_failed:{response.status_code}")
    declared = response.headers.get("Content-Length")
    if declared is not None:
        try:
            declared_size = int(declared)
        except ValueError as exc:
            raise ValueError("release_envelope_content_length_invalid") from exc
        if declared_size > MAX_ENVELOPE_SET_BYTES:
            raise ValueError("release_envelope_set_too_large")
    chunks: list[bytes] = []
    total = 0
    for chunk in response.iter_content(chunk_size=HTTP_CHUNK_BYTES):
        if not chunk:
            continue
        total += len(chunk)
        if total > MAX_ENVELOPE_SET_BYTES:
            raise ValueError("release_envelope_set_too_large")
        chunks.append(chunk)
    return b"".join(chunks)


def fetch_and_validate_envelope_set(
    envelope_ref_url_or_path: str,
    *,
    manifest: dict[str, Any] | None = None,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    """Fetch or read a release envelope set and validate its schema."""

    if not isinstance(envelope_ref_url_or_path, str) or not envelope_ref_url_or_path:
        raise ValueError("release_envelope_ref_invalid")
    parsed = urlparse(envelope_ref_url_or_path)
    if parsed.scheme:
        if parsed.scheme != "https":
            raise ValueError("release_envelope_fetch_insecure_url")
        payload = _fetch_https_envelope_set(envelope_ref_url_or_path)
    else:
        payload = _read_local_envelope_set(
            _resolve_local_envelope_ref(envelope_ref_url_or_path, base_dir=base_dir)
        )
    try:
        envelope_set = json.loads(
            payload.decode("utf-8"),
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError("release_envelope_set_invalid_json") from exc
    if not isinstance(envelope_set, dict):
        raise ValueError("release_envelope_set_not_object")
    try:
        validate_envelope_set(envelope_set, manifest=manifest)
    except InstallableReleaseSignatureError as exc:
        raise ValueError(str(exc)) from exc
    return envelope_set


def verify_artifact_signature(
    artifact_id: str,
    artifact_sha256: str,
    envelope_set: Mapping[str, Any],
    *,
    release_id: str,
    expected_signer_public_key_hex: str,
) -> None:
    """Verify one artifact hash against a detached Ed25519 release envelope."""

    envelopes = envelope_set.get("envelopes")
    if not isinstance(envelopes, Mapping):
        raise ValueError("release_envelope_set_envelopes_invalid")
    envelope = envelopes.get(artifact_id)
    if not isinstance(envelope, Mapping):
        raise ValueError("release_envelope_missing_artifact")
    try:
        validate_envelope(envelope)
    except InstallableReleaseSignatureError as exc:
        raise ValueError(str(exc)) from exc
    if envelope.get("release_id") != release_id:
        raise ValueError("release_envelope_release_id_mismatch")
    if envelope.get("signer_public_key_hex") != expected_signer_public_key_hex:
        raise ValueError("release_envelope_signer_public_key_mismatch")

    artifact_sha256_hex = _require_sha256_hex(artifact_sha256, field="artifact_sha256")
    preimage_sha256 = compute_signed_preimage_sha256(
        release_id=release_id,
        artifact_id=artifact_id,
        artifact_sha256=artifact_sha256_hex,
        release_key_registration_ref=str(envelope.get("release_key_registration_ref")),
        genesis_lineage_ref=str(envelope.get("genesis_lineage_ref")),
        prior_release_envelope_ref=str(envelope.get("prior_release_envelope_ref")),
    )
    if envelope.get("signed_preimage_sha256") != preimage_sha256:
        raise ValueError("release_envelope_preimage_mismatch")
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except ImportError as exc:
        raise ValueError("release_envelope_verify_cryptography_not_available") from exc

    try:
        public_key_bytes = bytes.fromhex(expected_signer_public_key_hex)
        signature_bytes = bytes.fromhex(str(envelope.get("signature_hex")))
        preimage_bytes = bytes.fromhex(preimage_sha256)
        public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)
        public_key.verify(signature_bytes, preimage_bytes)
    except InvalidSignature as exc:
        raise ValueError("release_envelope_signature_invalid") from exc
    except ValueError as exc:
        raise ValueError("release_envelope_signature_invalid") from exc


__all__ = [
    "HTTP_TIMEOUT_SECONDS",
    "MAX_ENVELOPE_SET_BYTES",
    "PUBLIC_RC_RELEASE_SIGNER_PUBLIC_KEY_HEX",
    "fetch_and_validate_envelope_set",
    "verify_artifact_signature",
]
