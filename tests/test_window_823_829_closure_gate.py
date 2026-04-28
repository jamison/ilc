"""Closure gate tests for Window 823-829."""

from __future__ import annotations

from pathlib import Path


WINDOW_ARTIFACTS = (
    Path("docs/specs/ilc_phase_823_829_sequence_lock_v0.1.md"),
    Path("docs/specs/ilc_high_002_production_disposition_824_v0.1.md"),
    Path("docs/specs/ilc_settlement_path_rotation_wiring_design_825_v0.1.md"),
    Path("docs/specs/ilc_first_validator_deployment_entry_conditions_826_v0.1.md"),
    Path("docs/phases/phase_0827_h013_implementation.md"),
    Path("docs/phases/phase_0828_coherence_report.md"),
    Path("docs/specs/ilc_antigravity_context_capsule_v5.14.md"),
    Path("docs/phases/phase_0829_window_823_829_closure_gate.md"),
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _window_text() -> str:
    return "\n".join(_read(path) for path in WINDOW_ARTIFACTS)


def test_closure_artifacts_and_tokens_exist() -> None:
    text = _window_text()
    for token in (
        "window_823_829_mysticeti_activation_sequencing_open",
        "high_002_disposition_record_published_824",
        "settlement_path_rotation_wiring_design_825_published",
        "first_validator_entry_conditions_record_826_published",
        "h013_sealed_sender_spectral_beacon_implemented_827",
        "h013_post_audit_hardening_applied",
        "capsule_v5_14_supersedes_v5_13",
        "window_823_829_mysticeti_activation_sequencing_closed",
        "phase_829_window_823_829_verdict=pass",
    ):
        assert token in text


def test_status_contains_entries_for_all_window_phases() -> None:
    status = _read(Path("docs/phases/STATUS.md"))
    for phase in range(823, 830):
        assert f"## Phase {phase}" in status


def test_planning_index_marks_capsule_v5_14_current_and_window_closed() -> None:
    planning = _read(Path("docs/PLANNING_INDEX.md"))
    assert "Window 823-829 CLOSED" in planning
    assert "Context Capsule v5.14" in planning
    assert "docs/specs/ilc_antigravity_context_capsule_v5.14.md" in planning
    assert "Phase 829 closure gate" in planning
    assert "Launch Roadmap v0.7" in planning


def test_no_decision_log_mutation_claim_or_row5_runtime_closure_claim() -> None:
    text = _window_text()
    assert "no_cdl_mutation_in_window_823_829" in text
    assert "no_row5_runtime_closure_claim_in_window_823_829" in text
    assert "row5_runtime_closed" not in text
    assert "Row 5 is runtime_closed" not in text
    assert "SIM-LEAKAGE-03 completion" not in text


def test_no_first_validator_deployment_or_option_b_graduation_claim() -> None:
    text = _window_text()
    assert "no_first_validator_deployment_in_window_823_829" in text
    assert "no_option_b_graduation_claim_in_window_823_829" in text
    assert "first non-Genesis validator deployed" not in text
    assert "Option B is graduated" not in text
    assert "option_b_graduated" not in text


def test_no_cdl_062_opening_and_h013_activation_boundary_preserved() -> None:
    text = _window_text()
    assert "no_cdl_062_opening_in_window_823_829" in text
    assert "Production D2d gossip activation remains a later gate" in text
