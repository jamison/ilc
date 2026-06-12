"""Tests for Phase 1560 key-custody attestation record.

Validates that the attestation correctly clears the custody blocker,
references the Phase 1431 manifest, uses genesis_operator_held mode,
and does not claim per-VPS proof-of-possession or any unauthorized activation.
"""
import pathlib

ATTESTATION_PATH = pathlib.Path(
    "docs/specs/ilc_phase_1560_key_custody_attestation_v0.1.md"
)
MANIFEST_1431_PATH = pathlib.Path(
    "docs/specs/ilc_rehearsal_agent_identity_manifest_1431_v0.1.md"
)
SEQUENCE_LOCK_PATH = pathlib.Path(
    "docs/specs/ilc_phase_1556_1564_sequence_lock_v0.1.md"
)


def _attest() -> str:
    return ATTESTATION_PATH.read_text(encoding="utf-8")


def _lock() -> str:
    return SEQUENCE_LOCK_PATH.read_text(encoding="utf-8")


def test_attestation_file_exists():
    assert ATTESTATION_PATH.exists()


def test_phase_1431_manifest_exists():
    """The custody attestation is only meaningful if the Phase 1431 manifest exists."""
    assert MANIFEST_1431_PATH.exists()


def test_custody_blocker_cleared_token_present():
    assert "phase_1560_key_custody_blocker_cleared" in _attest()


def test_custody_mode_is_genesis_operator_held():
    assert "custody_mode=genesis_operator_held" in _attest()


def test_attestation_covers_seven_agents():
    text = _attest()
    assert "genesis_operator_holds_seven_rehearsal_keypairs_phase_1560" in text


def test_phase_1431_manifest_referenced():
    assert "ilc_rehearsal_agent_identity_manifest_1431_v0.1.md" in _attest()


def test_node6_correctly_scoped_as_harness_not_init_participant():
    text = _attest()
    assert "node6_openclaw_harness_not_an_init_participant_phase_1560" in text


def test_vps_local_proof_deferred():
    assert "vps_local_proof_of_possession_deferred" in _attest()


def test_no_private_key_committed():
    assert "no_private_key_material_committed_phase_1560_attestation" in _attest()


def test_no_public_rc_claim():
    assert "no_public_rc_authorized_phase_1560_attestation" in _attest()


def test_no_production_economics_claim():
    assert "no_production_economics_authorized_phase_1560_attestation" in _attest()


def test_public_rc_exclude_header_present():
    assert "PUBLIC_RC_EXCLUDE" in _attest()


def test_sequence_lock_updated_to_preconditions_cleared():
    assert "PRECONDITIONS_CLEARED" in _lock()


def test_sequence_lock_references_attestation():
    assert "ilc_phase_1560_key_custody_attestation_v0.1.md" in _lock()


def test_sequence_lock_custody_tokens_recorded():
    lock = _lock()
    assert "phase_1560_key_custody_attested" in lock
    assert "phase_1560_key_custody_blocker_cleared" in lock
