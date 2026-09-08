from __future__ import annotations

import hashlib
import json
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from ilc_core.release.install_sh_manifest_sync import verify_install_sh_manifest_sync
from ilc_core.release.installable_release_manifest import validate_installable_release_manifest
from ilc_core.release.installable_release_signature import validate_envelope_set
from ilc_core.release.update_signature_verifier import verify_artifact_signature


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = (
    ROOT
    / "docs/specs/ilc_installable_release_manifest_ilc_core_0418_GAP_PUBLIC_RC_INVITE_PACKAGE_0418_00b_v0.1.json"
)
ENVELOPE_PATH = (
    ROOT
    / "docs/specs/ilc_core_0418_release_envelopes_GAP_PUBLIC_RC_INVITE_PACKAGE_0418_00b_v0.1.json"
)
UPLOAD_RECEIPT_PATH = (
    ROOT / "docs/specs/ilc_pypi_upload_receipt_GAP_PUBLIC_RC_INVITE_PACKAGE_0418_00b_v0.1.json"
)
INSTALL_SH = ROOT / "tools/install.sh"
EXPECTED_SIGNER_PUBLIC_KEY_HEX = (
    "5bf71c1e0ac93f2d7414b0dc315161fc4a57462c198ba1618e2890ec89a5b15a"
)
EXPECTED_ENVELOPE_SHA256 = (
    "133361b5a9ad23876fede9671f4d9843786b494e4a935f5f2e362e7c5f292dd9"
)
EXPECTED_SIGNED_ARTIFACT_IDS = {
    "ilc-artifact:ilc-core-python-wheel-0418@phase-1628",
    "ilc-artifact:ilc-core-python-sdist-0418@phase-1628",
}


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_0418_manifest_and_envelope_set_validate() -> None:
    manifest = _load_json(MANIFEST_PATH)
    envelope_set = _load_json(ENVELOPE_PATH)

    validate_installable_release_manifest(manifest)
    validate_envelope_set(envelope_set, manifest=manifest)

    assert manifest["release_id"] == "ilc-core-0.4.18"
    assert envelope_set["version"] == "0.4.18"


def test_0418_envelope_set_covers_only_signed_python_artifacts() -> None:
    manifest = _load_json(MANIFEST_PATH)
    envelope_set = _load_json(ENVELOPE_PATH)
    signed_artifacts = {
        artifact["artifact_id"]
        for artifact in manifest["artifacts"]  # type: ignore[index]
        if artifact["signing_status"] == "signed"
    }

    assert signed_artifacts == EXPECTED_SIGNED_ARTIFACT_IDS
    assert set(envelope_set["envelopes"]) == EXPECTED_SIGNED_ARTIFACT_IDS  # type: ignore[arg-type]


def test_0418_release_signatures_verify_with_committed_release_key() -> None:
    manifest = _load_json(MANIFEST_PATH)
    envelope_set = _load_json(ENVELOPE_PATH)
    public_key = Ed25519PublicKey.from_public_bytes(
        bytes.fromhex(EXPECTED_SIGNER_PUBLIC_KEY_HEX)
    )

    for artifact in manifest["artifacts"]:  # type: ignore[index]
        if artifact["signing_status"] != "signed":
            continue
        envelope = envelope_set["envelopes"][artifact["artifact_id"]]  # type: ignore[index]
        assert envelope["signer_public_key_hex"] == EXPECTED_SIGNER_PUBLIC_KEY_HEX
        public_key.verify(
            bytes.fromhex(envelope["signature_hex"]),
            bytes.fromhex(envelope["signed_preimage_sha256"]),
        )
        verify_artifact_signature(
            artifact["artifact_id"],
            artifact["canonical_hash"],
            envelope_set,
            release_id=manifest["release_id"],
            expected_signer_public_key_hex=EXPECTED_SIGNER_PUBLIC_KEY_HEX,
        )


def test_0418_upload_receipt_matches_manifest_and_pypi_urls() -> None:
    manifest = _load_json(MANIFEST_PATH)
    receipt = _load_json(UPLOAD_RECEIPT_PATH)
    artifacts_by_type = {
        artifact["artifact_type"]: artifact for artifact in manifest["artifacts"]  # type: ignore[index]
    }

    assert receipt["version"] == "0.4.18"
    assert receipt["fetchback_verification"] == "pass"
    assert receipt["release_signing"]["signature_verification"] == "pass"  # type: ignore[index]
    assert artifacts_by_type["python_wheel"]["download_url"] == receipt["artifacts"]["wheel"]["canonical_pypi_url"]  # type: ignore[index]
    assert artifacts_by_type["python_sdist"]["download_url"] == receipt["artifacts"]["sdist"]["canonical_pypi_url"]  # type: ignore[index]


def test_install_sh_is_synced_to_0418_manifest() -> None:
    verify_install_sh_manifest_sync(INSTALL_SH, MANIFEST_PATH)


def test_0418_envelope_set_sha256_pinned() -> None:
    assert hashlib.sha256(ENVELOPE_PATH.read_bytes()).hexdigest() == EXPECTED_ENVELOPE_SHA256
