"""Gate tests for Window 823-829 sequence lock and disposition artifacts."""

from __future__ import annotations

from pathlib import Path


LOCK = Path("docs/specs/ilc_phase_823_829_sequence_lock_v0.1.md")
HIGH_002 = Path("docs/specs/ilc_high_002_production_disposition_824_v0.1.md")
ROTATION = Path("docs/specs/ilc_settlement_path_rotation_wiring_design_825_v0.1.md")
FIRST_VALIDATOR = Path("docs/specs/ilc_first_validator_deployment_entry_conditions_826_v0.1.md")
PROMPT = Path("docs/antigravity_tasks/antigravity_prompt__window_823_829_mysticeti_activation_sequencing.md")


REQUIRED_SEQUENCE_TOKENS = (
    "window_823_829_mysticeti_activation_sequencing_open",
    "option_b_selected_adr_0028_posture_confirmed",
    "adr_0028_posture=option_b",
    "cdl_017_ratified_activation_boundary_preserved",
    "row5_spec_closed_runtime_pending_no_change_this_window",
    "high_002_documented_liveness_limitation_not_safety_break",
    "h013_adr_0034_accepted_implementation_is_next",
    "first_validator_deployment_human_gated_no_trigger_this_window",
    "b_impl_local_reviewer_no_row5_work_this_window",
    "no_cdl_mutation_authorized_window_823_829",
    "no_cdl_062_opening_authorized_window_823_829",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_sequence_lock_exists_and_contains_required_tokens() -> None:
    text = _read(LOCK)
    for token in REQUIRED_SEQUENCE_TOKENS:
        assert token in text


def test_sequence_lock_contains_phase_to_workstream_table() -> None:
    text = _read(LOCK)
    for phrase in (
        "Phase-to-Workstream Lock",
        "HIGH-002 production disposition",
        "Settlement-path activation design",
        "First-validator deployment gate",
        "H-013 implementation",
    ):
        assert phrase in text


def test_prompt_is_present_as_canonical_execution_basis() -> None:
    text = _read(PROMPT)
    assert "Window 823-829: Mysticeti Activation Sequencing" in text
    assert "Begin with Phase 823" in text


def test_high_002_disposition_records_liveness_not_safety_and_entry_conditions() -> None:
    text = _read(HIGH_002)
    assert "high_002_disposition_record_published_824" in text
    assert "liveness limitation" in text
    assert "not a safety break" in text
    assert "epoch_settlement.rs" in text
    assert "fast_aggregate_verify" in text
    assert "N >= 4" in text
    assert "F >= 1" in text


def test_rotation_design_is_design_only_and_names_smoke_criteria() -> None:
    text = _read(ROTATION)
    assert "settlement_path_rotation_wiring_design_825_published" in text
    assert "design-only" in text
    assert "handle_broadcast_honest" in text
    assert "handle_full_transfer_honest" in text
    assert "three-machine smoke proof" in text
    assert "Row-5 privacy queue implementation" in text


def test_first_validator_entry_conditions_preserve_human_gate() -> None:
    text = _read(FIRST_VALIDATOR)
    assert "first_validator_entry_conditions_record_826_published" in text
    assert "first_validator_deployment_human_gated_no_trigger_this_window" in text
    assert "Row 5 runtime closure is not a prerequisite" in text
    assert "HIGH-002 hardening is not a prerequisite" in text
    assert "explicit statement that the first non-Genesis validator deployment gate is" in text
