# SPDX-License-Identifier: AGPL-3.0-only

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = ROOT / "docs/ops/genesis_recovery_ceremony_runbook_v0.1.md"
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1573au_g8_genesis_recovery_ceremony_runbook.md"
STATUS = ROOT / "docs/phases/STATUS.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_runbook_exists_and_is_private_public_rc_excluded() -> None:
    text = _text(RUNBOOK)

    assert "PUBLIC_RC_EXCLUDE: genesis_recovery_runbook" in text
    assert "private custody material" in text


def test_runbook_records_forward_supersession_not_revocation() -> None:
    text = _text(RUNBOOK)

    assert "Genesis root keys are not revoked" in text
    assert "forward-superseded" in text
    assert "Old root signatures remain historically valid" in text
    assert "No retroactive invalidation" in text


def test_runbook_is_runbook_only_and_does_not_claim_execution() -> None:
    text = _text(RUNBOOK)

    assert "This document is procedural only" in text
    assert "did not reconstruct real Genesis recovery material" in text
    assert "did not reconstruct real Genesis recovery material, execute a real recovery" in text
    assert "Phase 1573as explicitly records that Genesis recovery is not operational" in text


def test_runbook_references_required_foundations() -> None:
    text = _text(RUNBOOK)

    assert "ilc_genesis_recovery_transaction_spec_1573as_v0.1.md" in text
    assert "Phase 1573at" in text
    assert "genesis_shamir_verify_only_drill_runbook_v0.1.md" in text
    assert "genesis_agent1_pubkey_record_838a.txt" in text


def test_runbook_preserves_two_factor_plate_model() -> None:
    text = _text(RUNBOOK)

    assert "Plate 1 provides `identity_seed`" in text
    assert "Plate 1 is not the recovery signing key" in text
    assert "Plate 3" in text
    assert "SPHINCS+/SLH-DSA recovery signing seed" in text


def test_runbook_public_record_excludes_private_material() -> None:
    text = _text(RUNBOOK)

    assert "must not contain Plate 1 words" in text
    assert "Shamir share hex" in text
    assert "reconstructed seed bytes" in text
    assert "successor root secret seed bytes" in text


def test_runbook_contains_no_private_material_field_assignments() -> None:
    text = _text(RUNBOOK)
    banned_fragments = (
        "sphincs_sk_hex:",
        "mldsa_sk_hex:",
        "private_key_hex:",
        "recovery_seed_hex:",
        "blinding_factor_hex:",
        "identity_seed =",
        "mnemonic =",
        "BEGIN PRIVATE KEY",
    )

    for fragment in banned_fragments:
        assert fragment not in text


def test_prompt_uses_actual_1573as_test_path() -> None:
    text = _text(PROMPT)

    assert "tests/test_phase_1573as_genesis_recovery_spec.py" in text
    assert "tests/test_phase_1573as_genesis_recovery_transaction_spec.py" not in text


def test_phase_status_tokens_present() -> None:
    text = _text(STATUS)

    assert "genesis_recovery_ceremony_runbook_committed_phase_1573au" in text
    assert "public_path_remains_blocked_phase_1573au" in text
