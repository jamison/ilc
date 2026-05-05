from pathlib import Path


SEQUENCE_LOCK = Path("docs/specs/ilc_phase_1218_1224_sequence_lock_v0.1.md")
PLANNING_INDEX = Path("docs/PLANNING_INDEX.md")
GUIDANCE = Path("docs/specs/ilc_window_1218_1224_candidate_phase_grouping_v0.1.md")
WALKTHROUGH = Path("docs/phases/phase_1218_window_sequence_lock_walkthrough.md")


def test_sequence_lock_file_exists() -> None:
    assert SEQUENCE_LOCK.exists()


def test_sequence_lock_contains_window_token() -> None:
    content = SEQUENCE_LOCK.read_text(encoding="utf-8")
    assert "window_1218_1224_sequence_lock_committed" in content


def test_sequence_lock_references_baseline_commits() -> None:
    content = SEQUENCE_LOCK.read_text(encoding="utf-8")
    assert "09bef7e7" in content
    assert "55901768" in content
    assert "window_1209_1217_closed_phase_1217" in content


def test_sequence_lock_records_permanence_deadline() -> None:
    content = SEQUENCE_LOCK.read_text(encoding="utf-8")
    assert "truth_primitive_permanence_unsafe_after_window_1225_1232_closure" in content
    assert "truth_primitive_permanence_ratification_event_required_window_1218_1224" in content


def test_sequence_lock_records_rate_limit_boundary() -> None:
    content = SEQUENCE_LOCK.read_text(encoding="utf-8")
    assert "transport_abuse_circuit_breaker_not_final_scaling_policy" in content
    assert "reciprocal_fetch_admission_model_required" in content


def test_sequence_lock_records_genesis_attestation_not_roster() -> None:
    content = SEQUENCE_LOCK.read_text(encoding="utf-8")
    assert "Genesis authority attestation" in content
    assert "no multi-party signer roster is required" in content


def test_guidance_no_longer_requires_human_signer_roster() -> None:
    content = GUIDANCE.read_text(encoding="utf-8")
    assert "requires `GO Phase 1219`; ratification by Genesis authority attestation" in content
    assert "requires `GO Phase 1219` + human signers" not in content
    assert "At least 3 distinct Genesis founding/member signers" not in content


def test_planning_index_points_to_active_window_and_lock() -> None:
    content = PLANNING_INDEX.read_text(encoding="utf-8")
    assert "Window 1218-1224 is IN PROGRESS through Phase 1218" in content
    assert "ilc_window_1218_1224_candidate_phase_grouping_v0.1.md" in content
    assert "ilc_phase_1218_1224_sequence_lock_v0.1.md" in content
    assert "Window 1209-1217 sequence lock** (closed reference)" in content


def test_walkthrough_marked_complete() -> None:
    content = WALKTHROUGH.read_text(encoding="utf-8")
    assert "**Status:** complete" in content
    assert "window_1218_1224_sequence_lock_committed" in content
