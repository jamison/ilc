from __future__ import annotations

import hashlib
import json
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from ilc_core.release.installable_release_manifest import load_installable_release_manifest
from ilc_core.release.installable_release_signature import (
    SIGNED_AT_EPOCH_ZERO,
    validate_envelope_set,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = (
    ROOT
    / "docs/specs/ilc_installable_release_manifest_ilc_core_0417_GAP_CONSENSUS_BINARY_DEPLOY_FIX2_00_v0.1.json"
)
ENVELOPE_PATH = (
    ROOT / "docs/specs/ilc_core_0417_release_envelopes_GAP_RELEASE_SIGN_00c_v0.1.json"
)
STATUS_PATH = ROOT / "docs/phases/STATUS.md"
EXPECTED_ENVELOPE_SHA256 = (
    "60a1bc4c404560e0fb211fec4788a87bf8c9bacff224b1f74d9647a6d1dd27b9"
)
EXPECTED_SIGNER_PUBLIC_KEY_HEX = (
    "5bf71c1e0ac93f2d7414b0dc315161fc4a57462c198ba1618e2890ec89a5b15a"
)
EXPECTED_SIGNED_ARTIFACT_IDS = {
    "ilc-artifact:ilc-core-python-wheel-0417@phase-1628",
    "ilc-artifact:ilc-core-python-sdist-0417@phase-1628",
}


def _manifest() -> dict[str, object]:
    return load_installable_release_manifest(MANIFEST_PATH)


def _envelope_set() -> dict[str, object]:
    return json.loads(ENVELOPE_PATH.read_text(encoding="utf-8"))


def _artifacts_by_id() -> dict[str, dict[str, object]]:
    manifest = _manifest()
    return {
        artifact["artifact_id"]: artifact
        for artifact in manifest["artifacts"]  # type: ignore[index]
    }


def test_envelope_set_is_present_and_validates() -> None:
    envelope_set = _envelope_set()
    validate_envelope_set(envelope_set, manifest=_manifest())


def test_envelope_set_has_signed_python_artifacts_only() -> None:
    envelopes = _envelope_set()["envelopes"]
    assert set(envelopes) == EXPECTED_SIGNED_ARTIFACT_IDS


def test_envelope_set_signed_at_is_epoch_zero() -> None:
    envelopes = _envelope_set()["envelopes"]
    for envelope in envelopes.values():  # type: ignore[union-attr]
        assert envelope["signed_at"] == SIGNED_AT_EPOCH_ZERO


def test_manifest_signing_status_marks_only_signed_artifacts() -> None:
    manifest = _manifest()
    statuses = {
        artifact["artifact_id"]: artifact["signing_status"]
        for artifact in manifest["artifacts"]  # type: ignore[index]
    }
    assert statuses == {
        "ilc-artifact:ilc-core-python-wheel-0417@phase-1628": "signed",
        "ilc-artifact:ilc-core-python-sdist-0417@phase-1628": "signed",
        "ilc-artifact:ilc-consensus-linux-x86-64-tarball-0416@phase-1628": "unsigned",
    }


def test_manifest_has_public_https_envelope_ref_after_00d() -> None:
    assert (
        _manifest()["release_envelope_ref"]
        == "https://raw.githubusercontent.com/jamison/ilc/main/docs/specs/ilc_core_0417_release_envelopes_GAP_RELEASE_SIGN_00c_v0.1.json"
    )


def test_manifest_records_release_signer_public_key() -> None:
    assert _manifest()["signer_public_key_hex"] == EXPECTED_SIGNER_PUBLIC_KEY_HEX


def test_manifest_no_longer_claims_no_release_signing() -> None:
    non_claims = _manifest()["non_claims"]
    assert "no_release_signing" not in non_claims  # type: ignore[operator]
    assert "release_signature_verification_for_0417_not_claimed" not in non_claims  # type: ignore[operator]


def test_envelope_artifacts_match_signed_manifest_artifacts_exactly() -> None:
    artifacts = _artifacts_by_id()
    envelopes = _envelope_set()["envelopes"]
    signed_artifacts = {
        artifact_id
        for artifact_id, artifact in artifacts.items()
        if artifact["signing_status"] == "signed"
    }
    assert set(envelopes) == signed_artifacts
    for artifact_id, envelope in envelopes.items():  # type: ignore[union-attr]
        manifest_hash = artifacts[artifact_id]["canonical_hash"]
        assert envelope["artifact_id"] == artifact_id
        assert envelope["artifact_sha256"] == str(manifest_hash).removeprefix("sha256:")


def test_envelope_signatures_verify_against_release_key() -> None:
    public_key = Ed25519PublicKey.from_public_bytes(
        bytes.fromhex(EXPECTED_SIGNER_PUBLIC_KEY_HEX)
    )
    envelopes = _envelope_set()["envelopes"]
    for envelope in envelopes.values():  # type: ignore[union-attr]
        assert envelope["signer_public_key_hex"] == EXPECTED_SIGNER_PUBLIC_KEY_HEX
        public_key.verify(
            bytes.fromhex(envelope["signature_hex"]),
            bytes.fromhex(envelope["signed_preimage_sha256"]),
        )


def test_envelope_set_sha256_recorded() -> None:
    envelope_bytes = ENVELOPE_PATH.read_text(encoding="utf-8").encode("utf-8")
    assert hashlib.sha256(envelope_bytes).hexdigest() == EXPECTED_ENVELOPE_SHA256
    assert EXPECTED_ENVELOPE_SHA256 in STATUS_PATH.read_text(encoding="utf-8")


def test_no_private_key_in_envelope() -> None:
    envelope_text = ENVELOPE_PATH.read_text(encoding="utf-8").lower()
    assert "private" not in envelope_text
    assert "secret" not in envelope_text
    assert "-----begin" not in envelope_text
