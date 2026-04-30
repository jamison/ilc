from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from ilc_core.types import PROVENANCE_DECAY_ALPHA


ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.36.md"
COHERENCE = ROOT / "docs/specs/ilc_integration_coherence_report_1122_v0.1.md"
CONLEY = ROOT / "docs/antigravity_tasks/antigravity_prompt__conley_index_framing_review_v0.1.md"


def test_c1_capsule_v5_36_exists_with_supersession_token() -> None:
    assert CAPSULE.exists()
    assert "capsule_v5_36_supersedes_v5_35" in CAPSULE.read_text(encoding="utf-8")


def test_c2_capsule_records_float_kill_01_complete() -> None:
    text = CAPSULE.read_text(encoding="utf-8")
    assert "float_kill_01_complete_phase_1119" in text


def test_c3_capsule_records_sim_provenance_complete() -> None:
    text = CAPSULE.read_text(encoding="utf-8")
    assert "sim_provenance_01_complete_phase_1120_1121" in text


def test_c4_capsule_records_q8_satisfied() -> None:
    text = CAPSULE.read_text(encoding="utf-8")
    assert "q8_satisfied_sim_provenance_01_complete" in text
    assert "Q8" in text
    assert "SATISFIED Phase 1121" in text


def test_c5_capsule_records_q2_active_alpha_amendment_pending() -> None:
    text = CAPSULE.read_text(encoding="utf-8")
    assert "q2_active_cdl_amendment_pending_alpha_0_45" in text
    assert "SIM recommendation `α=0.45`" in text or "SIM recommendation: `α=0.45`" in text


def test_c6_production_alpha_locked_decimal_0_45() -> None:
    assert isinstance(PROVENANCE_DECAY_ALPHA, Decimal)
    assert PROVENANCE_DECAY_ALPHA == Decimal("0.45")


def test_c7_coherence_report_exists_with_pass_verdict() -> None:
    assert COHERENCE.exists()
    text = COHERENCE.read_text(encoding="utf-8")
    assert "coherence_report_1122_verdict=pass" in text


def test_c8_coherence_references_run_01_and_run_02_results() -> None:
    text = COHERENCE.read_text(encoding="utf-8")
    assert "Run 01 (Phase 1120)" in text
    assert "Run 02 (Phase 1121)" in text
    assert "α=0.45" in text


def test_c9_sim_spectral_02_data_dependency_satisfied_but_deferred() -> None:
    text = CAPSULE.read_text(encoding="utf-8") + COHERENCE.read_text(encoding="utf-8")
    assert "sim_spectral_02_data_dependency_satisfied" in text
    assert "Time-series data dependency satisfied" in text
    assert "Not scheduled" in text or "not scheduled" in text


def test_c10_conley_research_is_archived_and_deferred() -> None:
    assert CONLEY.exists()
    text = CAPSULE.read_text(encoding="utf-8") + COHERENCE.read_text(encoding="utf-8")
    assert "Conley Index research" in text
    assert "pre-RC1.0" in text
    assert "not scheduled" in text
