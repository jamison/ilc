from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1156_1165_sequence_lock_v0.1.md"


def test_phase_1156_sequence_lock_exists_with_token() -> None:
    text = SEQUENCE_LOCK.read_text(encoding="utf-8")
    assert "window_1156_1165_sequence_lock_committed" in text


def test_phase_1156_records_prior_tail_deferred() -> None:
    text = SEQUENCE_LOCK.read_text(encoding="utf-8")
    assert "phase_1156_deferred_not_authorized_inherited_from_window_1148_1156" in text


def test_phase_1156_records_cdl_085_preopening_gap() -> None:
    text = SEQUENCE_LOCK.read_text(encoding="utf-8")
    assert "cdl_085_no_canonical_opening_spec_exists_prior_to_phase_1163" in text
    assert "docs/specs/ilc_cdl_085_werner_phi_bound_opening_1163_v0.1.md" in text


def test_phase_1156_requires_phase_1163_human_go() -> None:
    text = SEQUENCE_LOCK.read_text(encoding="utf-8")
    assert "sim_spectral_04_gate_pass" in text
    assert "GO Phase 1163" in text
