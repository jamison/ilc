"""Phase 1148 — Window 1148-1156 sequence lock and ADR review."""

from __future__ import annotations

import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_sequence_lock_exists_with_window_token() -> None:
    text = _read("docs/specs/ilc_phase_1148_1156_sequence_lock_v0.1.md")
    assert "window_1148_1156_sequence_lock_committed" in text
    assert "Phases 1148-1154 may be Strike Forced" in text
    assert "Phase 1155 requires explicit human GO" in text


def test_guidance_doc_records_36_node_candidate_scope() -> None:
    text = _read("docs/specs/ilc_window_1148_1156_candidate_phase_grouping_v0.1.md")
    assert "v0.2 candidate: 36 nodes" in text or "36 nodes" in text
    assert "adr_status_normalization_required_before_tier2_promotion" in text
    assert "adr_0020_acceptance_review_priority_before_tier3_embedding_linkage" in text


def test_accepted_adr_promotions_are_locked() -> None:
    text = _read("docs/specs/ilc_phase_1148_1156_sequence_lock_v0.1.md")
    for token in (
        "adr_0019_tier2_promote_phase_1149",
        "adr_0026_tier2_promote_phase_1149",
        "adr_0028_tier2_promote_phase_1149",
        "adr_0031_tier2_promote_phase_1149",
    ):
        assert token in text


def test_proposed_adrs_are_blocked_from_tier2_promotion() -> None:
    text = _read("docs/specs/ilc_phase_1148_1156_sequence_lock_v0.1.md")
    for token in (
        "adr_0012_tier2_blocked_status_proposed_not_accepted",
        "adr_0020_tier2_blocked_status_proposed_not_accepted",
        "adr_0022_tier2_blocked_status_proposed_not_accepted",
        "adr_0023_tier2_blocked_status_proposed_not_accepted",
        "adr_0008_tier2_blocked_status_proposed_not_accepted",
    ):
        assert token in text


def test_adr0034_and_release_key_are_deferred() -> None:
    text = _read("docs/specs/ilc_phase_1148_1156_sequence_lock_v0.1.md")
    assert "adr_0034_tier2_deferred_to_window_1166_plus" in text
    assert "phase_1156_scenario_a_release_key_deferred_to_window_1157_plus" in text


def test_genesis_compile_tool_flags_are_recorded() -> None:
    text = _read("docs/specs/ilc_phase_1148_1156_sequence_lock_v0.1.md")
    assert "genesis_compile_coverage_diagnostic.py --star-map" in text
    assert "genesis_compile_coverage_diagnostic.py --json-out" in text
    assert "genesis_compile_coverage_diagnostic.py --report-out" in text


def test_walkthrough_records_required_tokens() -> None:
    text = _read("docs/phases/phase_1148_window_sequence_lock_adr_review_walkthrough.md")
    assert "window_1148_1156_sequence_lock_committed" in text
    assert "adr_status_normalization_required_before_tier2_promotion" in text
    assert "adr_0020_acceptance_review_priority_before_tier3_embedding_linkage" in text
