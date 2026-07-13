from pathlib import Path

from ilc_core.rc.signing_ceremony_status import (
    PHASE_1446_EPOCH_TRANSITION_AUTHORIZED,
    PHASE_1446_PUBLIC_RC_PUBLISHED,
    PHASE_1446_RELEASE_ARTIFACT_SIGNING_PERFORMED,
    PHASE_1446_ROOT_ENVELOPE_HASH,
    PHASE_1446_RUNTIME_FLAG_ACTIVATION_AUTHORIZED,
    PHASE_1446_SIGNED_ARTIFACT_HASHES,
    PHASE_1446_SIGNING_RECORD_PATH,
    PHASE_1446_SIGNING_TOKENS,
    PUBLIC_RC_NOT_PUBLISHED_PHASE_1446_TOKEN,
    phase_1446_status,
)

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_SECRET_PATTERNS = (
    "BEGIN PRIVATE KEY",
    "END PRIVATE KEY",
    "PRIVATE KEY",
    "mnemonic",
    "recovery_seed",
)
REQUIRED_TOKENS = (
    "signing_ceremony_pre_conditions_verified_phase_1446",
    "v0_3_genesis_root_envelope_signed_phase_1446",
    "v0_3_signing_ceremony_complete_phase_1446",
    "public_rc_not_published_phase_1446",
)


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1446_sidecar_exports_tokens_and_non_authorizations() -> None:
    assert PHASE_1446_ROOT_ENVELOPE_HASH.startswith("sha256:")
    assert set(REQUIRED_TOKENS).issubset(set(PHASE_1446_SIGNING_TOKENS))
    assert PUBLIC_RC_NOT_PUBLISHED_PHASE_1446_TOKEN in PHASE_1446_SIGNING_TOKENS
    assert PHASE_1446_PUBLIC_RC_PUBLISHED is False
    assert PHASE_1446_EPOCH_TRANSITION_AUTHORIZED is False
    assert PHASE_1446_RUNTIME_FLAG_ACTIVATION_AUTHORIZED is False
    assert PHASE_1446_RELEASE_ARTIFACT_SIGNING_PERFORMED is False
    assert PHASE_1446_SIGNED_ARTIFACT_HASHES[
        "out/genesis_core_star_map_v0.3_candidate.json"
    ]
    assert PHASE_1446_SIGNED_ARTIFACT_HASHES[
        "out/genesis_compile_coverage_diagnostic_v0.3_candidate.json"
    ]
    assert phase_1446_status()["public_rc_" + "published"] is False


def test_phase_1446_signing_record_contains_tokens_and_no_secret_material() -> None:
    record = _read(PHASE_1446_SIGNING_RECORD_PATH)
    for token in REQUIRED_TOKENS:
        assert token in record
    for pattern in FORBIDDEN_SECRET_PATTERNS:
        assert pattern not in record
    assert "Root envelope payload hash: `sha256:" in record
    assert "public_rc_not_published_phase_1446" in record


def test_phase_1446_sidecar_has_public_rc_exclude_and_public_boundary() -> None:
    sidecar = _read("ilc_core/rc/signing_ceremony_status.py")
    assert sidecar.startswith(
        "# PUBLIC_RC_EXCLUDE: "
        "internal_signing_ceremony_status_not_public_rc_launch_surface\n"
    )
    assert "# PUBLIC_RC_EXCLUDE_REASON: Phase 1446/1447 signing ceremony token record; internal only." in sidecar
    assert "PUBLIC_RC_NOT_PUBLISHED_PHASE_1446_TOKEN" in sidecar
    for pattern in FORBIDDEN_SECRET_PATTERNS:
        assert pattern not in sidecar


def test_phase_1446_status_and_sequence_lock_are_backfilled() -> None:
    status = _read("docs/phases/STATUS.md")
    sequence_lock = _read("docs/specs/ilc_phase_1429_1458_sequence_lock_v0.1.md")
    assert "Phase 1446 / v0.3 Genesis Root Envelope Signing Ceremony" in status
    assert "v0_3_genesis_root_envelope_signed_phase_1446" in status
    assert "public_rc_not_published_phase_1446" in status
    assert "Phase 1446 addendum" in sequence_lock
    assert "v0_3_signing_ceremony_complete_phase_1446" in sequence_lock
