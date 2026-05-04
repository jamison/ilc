from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1176_1182_sequence_lock_v0.1.md"


def test_phase_1176_sequence_lock_doc_exists():
    assert SEQUENCE_LOCK.exists()


def test_phase_1176_sequence_lock_token_present():
    text = SEQUENCE_LOCK.read_text(encoding="utf-8")
    assert "window_1176_1182_sequence_lock_committed" in text
