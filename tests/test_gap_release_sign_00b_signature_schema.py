from __future__ import annotations

import json

import pytest

from ilc_core.release.installable_release_signature import (
    SCHEMA_VERSION,
    SIGNED_AT_EPOCH_ZERO,
    SIGNED_PREIMAGE_DOMAIN,
    SIGNING_ALGORITHM,
    InstallableReleaseSignatureError,
    build_envelope_skeleton,
    canonical_envelope_json,
    compute_signed_preimage_sha256,
    signed_preimage_payload,
    validate_envelope,
    validate_envelope_set,
)


ARTIFACT_ID = "ilc-artifact:ilc-core-python-wheel-0415@phase-1627"
ARTIFACT_SHA256 = "058e2deec5656d25cc92de3d16acd8db01778f26c18e6405e06db48569ce7524"
RELEASE_ID = "ilc-core-0.4.15"
PUBLIC_KEY = "a" * 64
SIGNATURE = "b" * 128


def _signed_envelope() -> dict[str, str]:
    envelope = build_envelope_skeleton(
        release_id=RELEASE_ID,
        artifact_id=ARTIFACT_ID,
        artifact_sha256=ARTIFACT_SHA256,
    )
    envelope["signer_public_key_hex"] = PUBLIC_KEY
    envelope["signature_hex"] = SIGNATURE
    return envelope


def _manifest() -> dict[str, object]:
    return {
        "manifest_schema_version": "GAP_PUBLIC_INSTALL_01.v0.1",
        "release_id": RELEASE_ID,
        "channel": "rc",
        "manifest_produced_phase": 1627,
        "non_claims": ["no_release_signing"],
        "artifacts": [
            {
                "artifact_id": ARTIFACT_ID,
                "artifact_type": "python_wheel",
                "canonical_hash": f"sha256:{ARTIFACT_SHA256}",
                "lineage_reference": "genesis:v0.1",
                "produced_phase": 1627,
                "ratification_token": "cdl_086_ratified_phase_1220",
                "signing_status": "unsigned",
                "platform": "any",
                "arch": "any",
                "channel": "rc",
                "size_bytes": 1451016,
                "download_url": "https://files.pythonhosted.org/example/ilc_core-0.4.15-py3-none-any.whl",
                "min_python_version": "3.10",
            }
        ],
    }


def test_build_skeleton_has_required_fields() -> None:
    envelope = build_envelope_skeleton(
        release_id=RELEASE_ID,
        artifact_id=ARTIFACT_ID,
        artifact_sha256=ARTIFACT_SHA256,
    )
    assert set(envelope) == {
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


def test_build_skeleton_signed_at_is_epoch_zero() -> None:
    envelope = build_envelope_skeleton(
        release_id=RELEASE_ID,
        artifact_id=ARTIFACT_ID,
        artifact_sha256=ARTIFACT_SHA256,
    )
    assert envelope["signed_at"] == SIGNED_AT_EPOCH_ZERO


def test_build_skeleton_validates_only_with_unsigned_placeholder_mode() -> None:
    envelope = build_envelope_skeleton(
        release_id=RELEASE_ID,
        artifact_id=ARTIFACT_ID,
        artifact_sha256=ARTIFACT_SHA256,
    )
    validate_envelope(envelope, allow_unsigned_placeholders=True)
    with pytest.raises(InstallableReleaseSignatureError, match="release_envelope_public_key_invalid"):
        validate_envelope(envelope)


def test_compute_preimage_sha256_is_deterministic() -> None:
    first = compute_signed_preimage_sha256(
        release_id=RELEASE_ID,
        artifact_id=ARTIFACT_ID,
        artifact_sha256=ARTIFACT_SHA256,
    )
    second = compute_signed_preimage_sha256(
        release_id=RELEASE_ID,
        artifact_id=ARTIFACT_ID,
        artifact_sha256=ARTIFACT_SHA256,
    )
    assert first == second
    assert len(first) == 64


def test_compute_preimage_sha256_canonical_json_used() -> None:
    payload = signed_preimage_payload(
        release_id=RELEASE_ID,
        artifact_id=ARTIFACT_ID,
        artifact_sha256=ARTIFACT_SHA256,
    )
    expected = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )
    assert canonical_envelope_json(payload) == expected


def test_preimage_includes_domain_and_release_id() -> None:
    payload = signed_preimage_payload(
        release_id=RELEASE_ID,
        artifact_id=ARTIFACT_ID,
        artifact_sha256=ARTIFACT_SHA256,
    )
    assert payload["signed_preimage_domain"] == SIGNED_PREIMAGE_DOMAIN
    assert payload["release_id"] == RELEASE_ID


def test_validate_envelope_accepts_signed_shape() -> None:
    validate_envelope(_signed_envelope())


def test_validate_envelope_rejects_wrong_schema_version() -> None:
    envelope = _signed_envelope()
    envelope["schema_version"] = "wrong"
    with pytest.raises(InstallableReleaseSignatureError, match="release_envelope_schema_version_invalid"):
        validate_envelope(envelope)


def test_validate_envelope_rejects_non_hex_public_key() -> None:
    envelope = _signed_envelope()
    envelope["signer_public_key_hex"] = "z" * 64
    with pytest.raises(InstallableReleaseSignatureError, match="release_envelope_public_key_invalid"):
        validate_envelope(envelope)


def test_validate_envelope_rejects_non_hex_signature() -> None:
    envelope = _signed_envelope()
    envelope["signature_hex"] = "z" * 128
    with pytest.raises(InstallableReleaseSignatureError, match="release_envelope_signature_hex_invalid"):
        validate_envelope(envelope)


def test_validate_envelope_rejects_wrong_signed_at() -> None:
    envelope = _signed_envelope()
    envelope["signed_at"] = "2026-09-04T00:00:00Z"
    with pytest.raises(InstallableReleaseSignatureError, match="release_envelope_signed_at_invalid"):
        validate_envelope(envelope)


def test_validate_envelope_rejects_extra_fields() -> None:
    envelope = _signed_envelope()
    envelope["extra"] = "field"
    with pytest.raises(InstallableReleaseSignatureError, match="release_envelope_extra_field:extra"):
        validate_envelope(envelope)


def test_validate_envelope_rejects_float_values() -> None:
    envelope = _signed_envelope()
    envelope["release_id"] = 1.25  # type: ignore[assignment]
    with pytest.raises(InstallableReleaseSignatureError, match="release_envelope_number_rejected"):
        validate_envelope(envelope)


def test_validate_envelope_rejects_preimage_mismatch() -> None:
    envelope = _signed_envelope()
    envelope["signed_preimage_sha256"] = "0" * 64
    with pytest.raises(InstallableReleaseSignatureError, match="release_envelope_preimage_sha256_mismatch"):
        validate_envelope(envelope)


def test_validate_envelope_rejects_wrong_domain() -> None:
    envelope = _signed_envelope()
    envelope["signed_preimage_domain"] = "WRONG_DOMAIN"
    with pytest.raises(InstallableReleaseSignatureError, match="release_envelope_preimage_domain_invalid"):
        validate_envelope(envelope)


def test_validate_envelope_set_rejects_empty_envelopes() -> None:
    with pytest.raises(InstallableReleaseSignatureError, match="release_envelope_set_envelopes_invalid"):
        validate_envelope_set({"schema_version": SCHEMA_VERSION, "version": "0.4.15", "envelopes": {}})


def test_validate_envelope_set_checks_manifest_coverage() -> None:
    envelope = _signed_envelope()
    validate_envelope_set(
        {
            "schema_version": SCHEMA_VERSION,
            "version": "0.4.15",
            "envelopes": {ARTIFACT_ID: envelope},
        },
        manifest=_manifest(),
    )


def test_validate_envelope_set_rejects_manifest_hash_mismatch() -> None:
    envelope = _signed_envelope()
    manifest = _manifest()
    manifest["artifacts"][0]["canonical_hash"] = "sha256:" + ("1" * 64)  # type: ignore[index]
    with pytest.raises(InstallableReleaseSignatureError, match="release_envelope_artifact_sha256_mismatch"):
        validate_envelope_set(
            {
                "schema_version": SCHEMA_VERSION,
                "version": "0.4.15",
                "envelopes": {ARTIFACT_ID: envelope},
            },
            manifest=manifest,
        )


def test_canonical_envelope_json_sort_keys() -> None:
    assert canonical_envelope_json({"b": "2", "a": "1"}) == '{"a":"1","b":"2"}'


def test_constants_are_public_rc_release_schema_values() -> None:
    assert SCHEMA_VERSION == "GAP_RELEASE_SIGN_00b_v0.1"
    assert SIGNING_ALGORITHM == "Ed25519"
