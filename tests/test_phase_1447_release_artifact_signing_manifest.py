import hashlib
import json
import re
from pathlib import Path

from ilc_core.rc.signing_ceremony_status import (
    PHASE_1446_ROOT_ENVELOPE_HASH,
    PHASE_1446_SIGNED_ARTIFACT_HASHES,
    PHASE_1446_SIGNING_TOKENS,
    PHASE_1447_DETERMINISTIC_TIMESTAMP_FALLBACK,
    PHASE_1447_EPOCH_TRANSITION_AUTHORIZED,
    PHASE_1447_LAUNCH_READINESS_MANIFEST_CONTENT_HASH,
    PHASE_1447_MANIFEST_SIGNATURE,
    PHASE_1447_PUBLIC_REPOSITORY_PUBLISHED,
    PHASE_1447_RELEASE_ARTIFACT_SIGNING_MANIFEST_PATH,
    PHASE_1447_SIGNING_TOKENS,
    PUBLIC_RC_LAUNCH_READINESS_MANIFEST_V1_FINALIZED_PHASE_1447_TOKEN,
    PUBLIC_REPOSITORY_NOT_PUBLISHED_PHASE_1447_TOKEN,
    RELEASE_ARTIFACTS_SIGNED_PHASE_1447_TOKEN,
    phase_1447_status,
)

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_SECRET_PATTERNS = (
    "BEGIN PRIVATE KEY",
    "END PRIVATE KEY",
    "PRIVATE KEY",
    "mnemonic",
    "recovery_seed",
)
PHASE_1446_REQUIRED_TOKENS = (
    "signing_ceremony_pre_conditions_verified_phase_1446",
    "v0_3_genesis_root_envelope_signed_phase_1446",
    "v0_3_signing_ceremony_complete_phase_1446",
    "public_rc_not_published_phase_1446",
)
PHASE_1447_REQUIRED_TOKENS = (
    "release_artifacts_signed_phase_1447",
    "public_rc_launch_readiness_manifest_v1_finalized_phase_1447",
    "public_repository_not_published_phase_1447",
)


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _canonical_hash(payload: object) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _first_json_block(text: str) -> dict[str, object]:
    match = re.search(r"```json\n(.*?)\n```", text, flags=re.S)
    assert match is not None
    return json.loads(match.group(1))


def test_phase_1447_sidecar_exports_tokens_and_non_authorizations() -> None:
    assert RELEASE_ARTIFACTS_SIGNED_PHASE_1447_TOKEN in PHASE_1447_SIGNING_TOKENS
    assert (
        PUBLIC_RC_LAUNCH_READINESS_MANIFEST_V1_FINALIZED_PHASE_1447_TOKEN
        in PHASE_1447_SIGNING_TOKENS
    )
    assert PUBLIC_REPOSITORY_NOT_PUBLISHED_PHASE_1447_TOKEN in PHASE_1447_SIGNING_TOKENS
    assert set(PHASE_1446_REQUIRED_TOKENS).issubset(set(PHASE_1446_SIGNING_TOKENS))
    assert PHASE_1447_PUBLIC_REPOSITORY_PUBLISHED is False
    assert PHASE_1447_EPOCH_TRANSITION_AUTHORIZED is False
    assert PHASE_1447_MANIFEST_SIGNATURE is None
    assert PHASE_1447_DETERMINISTIC_TIMESTAMP_FALLBACK == "1970-01-01T00:00:00Z"
    assert phase_1447_status()["manifest_signature"] is None


def test_phase_1447_manifest_document_contains_tokens_and_boundaries() -> None:
    text = _read(PHASE_1447_RELEASE_ARTIFACT_SIGNING_MANIFEST_PATH)
    for token in PHASE_1447_REQUIRED_TOKENS:
        assert token in text
    for pattern in FORBIDDEN_SECRET_PATTERNS:
        assert pattern not in text
    assert "Phase 1446 root envelope recomputation: `PASS`" in text
    assert "Phase 1446 artifact path/hash set exact match: `PASS`" in text
    assert PHASE_1446_ROOT_ENVELOPE_HASH in text
    assert "1970-01-01T00:00:00Z" in text
    assert "wall-clock generated" not in text
    assert '"manifest_signature": null' in text
    assert '"epoch_0_to_1_transition_authorized": false' in text
    assert not re.search(r"epoch_0_to_1_transition_authorized.*true", text)


def test_phase_1447_launch_manifest_content_hash_recomputes() -> None:
    manifest = _first_json_block(_read(PHASE_1447_RELEASE_ARTIFACT_SIGNING_MANIFEST_PATH))
    assert manifest["manifest_version"] == "public_rc_launch_readiness_manifest_v1"
    assert manifest["epoch_0_to_1_transition_authorized"] is False
    assert manifest["manifest_signature"] is None
    assert manifest["manifest_content_hash"] == PHASE_1447_LAUNCH_READINESS_MANIFEST_CONTENT_HASH
    clone = json.loads(json.dumps(manifest, sort_keys=True, allow_nan=False))
    clone["manifest_content_hash"] = None
    clone["manifest_signature"] = None
    assert _canonical_hash(clone) == PHASE_1447_LAUNCH_READINESS_MANIFEST_CONTENT_HASH


def test_phase_1446_root_hash_and_artifact_set_recompute() -> None:
    phase_1446_payload = _first_json_block(
        _read("docs/specs/ilc_v03_genesis_root_envelope_signing_record_1446_v0.1.md")
    )
    assert _canonical_hash(phase_1446_payload) == PHASE_1446_ROOT_ENVELOPE_HASH
    artifact_set = {
        item["path"]: item["sha256"]
        for item in phase_1446_payload["artifact_hashes"]
    }
    assert artifact_set == PHASE_1446_SIGNED_ARTIFACT_HASHES


def test_phase_1447_status_and_sequence_lock_are_backfilled() -> None:
    status = _read("docs/phases/STATUS.md")
    sequence_lock = _read("docs/specs/ilc_phase_1429_1458_sequence_lock_v0.1.md")
    assert "Phase 1447 / Release Artifact Signing + Manifest Finalization" in status
    assert "release_artifacts_signed_phase_1447" in status
    assert "public_repository_not_published_phase_1447" in status
    assert "Phase 1447 addendum" in sequence_lock
    assert "public_rc_launch_readiness_manifest_v1_finalized_phase_1447" in sequence_lock
